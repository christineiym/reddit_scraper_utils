"""A supplementary scraper for Reddit comments, made in a hurry

Only for comments
"""

import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import csv
import pandas as pd
import re


http = httplib2.Http()
APPEND_MODE = "a"
SUBREDDIT_NAME = "cmu"

header_written = False

def main():
    keywords = pd.read_csv("input_disability.csv")
    queries_raw = list(keywords["keywords"])
    queries = [keyword.lower() for keyword in queries_raw]
    print(queries)

    i = 0
    while i < len(queries):
        data = []
        query_string = queries[i].replace(" ", "%20")
        query_url = "https://www.reddit.com/r/" + SUBREDDIT_NAME + "/search/?q=" + query_string + \
            "&restrict_sr=1&sr_nsfw=&include_over_18=1&type=comment"
        status, response = http.request(query_url)
        soup = BeautifulSoup(response, features="html.parser")
        # print(soup)
        relevant_soup = soup.find_all("div", {"data-testid" : "search-comment-content"})
        # print(relevant_soup)

        for item in relevant_soup:
            item_info: dict[str, str] = {}
            item_info["query"] = queries[i]

            user = item.find("faceplate-tracker", {"data-faceplate-tracking-context": "{\";search\";:{\";origin_element\";:\";comment_author\";}}"})
            if user is not None:
                item_info["user"] = user.get("href")
            else:
                item_info["user"] = ""

            # flair = item.find("span", {"class": "_1jNPl3YUk6zbpLWdjaJT1r cFNx42ceihnMpvAsovOTi"})
            # if flair is not None:
            #     item_info["flair"] = flair.get_text()
            # else:
            #     item_info["flair"] = ""
            
            
            raw_comment_text = item.find("div", {"class": "i18n-search-comment-content max-h-[260px] overflow-hidden text-ellipsis text-neutral-content-strong hover:no-underline no-underline no-visited"}).get_text()
            item_info["comment_text"] = raw_comment_text.replace("(\r\n|\r|\n)( |\t)", " ")  # remove paragraph breaks  #TODO: buggy, fix
            # item_info["upvotes"] = item.find("div", {"data-testid": "search-counter-row"}).get_text()
            # item_info["link"] = "https://www.reddit.com" + item.find("faceplate-tracker", {"data-faceplate-tracking-context": "{\"search\";:{\";origin_element\";:\";go_to_comment_link\";}}"}).get("href")
            
            data.append(item_info)
        
        with open("reddit_comments_disability.csv", APPEND_MODE, newline='') as output_file:
            if len(data) > 0:
                dict_writer = csv.DictWriter(output_file, data[0].keys())

                global header_written
                if not header_written:
                    dict_writer.writeheader()
                    header_written = True
                dict_writer.writerows(data)
        
        print("Done with query: " + queries[i])
        i += 1


if __name__ == "__main__":
    main()