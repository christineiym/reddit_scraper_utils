"""A supplementary scraper for obtaining SharePoint emails from the relevant element.

To use, open the member list on SharePoint, inspect the page, and copy the html for the div with class="ms-List"
into "email.html" (or a similar file). Then run the file as a module.

Further resources:
https://stackoverflow.com/questions/21570780/using-python-and-beautifulsoup-saved-webpage-source-codes-into-a-local-file
"""

from bs4 import BeautifulSoup
import csv

APPEND_MODE = "a"


def main():
    soup = BeautifulSoup(open("emails.html"), features="html.parser")
    relevant_soup = soup.find_all("div", {"data-automationid" : "GroupMemberPersona"})

    result = []
    for member in relevant_soup:
        data = {}

        name_twice = member.find("div", {"class": "ms-groupMember-lpcpersonatitle"})
        if name_twice is not None:
            name_twice_str = str(name_twice.get_text())
            name_with_spaces = name_twice_str[0:(len(name_twice_str))//2]
            name_components = name_with_spaces.split("\n")
            name = " ".join([component.strip() for component in name_components])
            data["name"] = name.strip()
        else:
            data["name"] = ""

        email_wrapper = member.find("img", {"class": "ms-Image-image is-loaded ms-Image-image--cover ms-Image-image--portrait is-fadeIn image-363"})
        if email_wrapper is not None:
            link_and_email = str(email_wrapper["src"]).split("accountname=")
            data["email"] = link_and_email[1].replace("%40", "@")
        else:
            data["email"] = ""

        result.append(data)

    with open("sharepoint_emails.csv", APPEND_MODE, newline='') as output_file:
        if len(result) > 0:
            dict_writer = csv.DictWriter(output_file, result[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(result)


if __name__ == "__main__":
    main()