import os
from dotenv import load_dotenv

load_dotenv()

import requests
from bs4 import BeautifulSoup as bs
import webbrowser

#logs into Gradescope and experiments with class dueDates
#Does not currently add anything to database or gui
def loginGradescope():
    USERNAME = os.getenv('USER_gradescope')
    PASS = os.getenv('PASS_gradescope')
    session = requests.Session();
    cookies = session.cookies;

    page = bs(session.get("https://www.gradescope.com/login").content, "html.parser")

    TOKEN = page.find("input", {"name":"authenticity_token"})["value"]
    payload = {"session[email]": USERNAME, "session[password]": PASS, "authenticity_token": TOKEN}

    response = session.post("https://www.gradescope.com/login", data=payload, verify=True, cookies=cookies)
    URL = response.url
    response = bs(response.content, "html.parser")

    classElems = response.find("div", {"class":"courseList--coursesForTerm"}).find_all("a", {"class":"courseBox"})
    for element in classElems:
        link = URL + element["href"]
        # print(link)


    # print(response)
    # siteToFile(response)
    # siteToFile(session.get("https://www.gradescope.com/account"))

#For Testing
#Writes the html responses as BeautifulSoup parsed html file
def siteToFile(page):
    f = open("result.html", "w", encoding="utf-8")
    f.write(bs(page.content,'html.parser').prettify())
    f.close()
    webbrowser.open("result.html")

#Returns an array of all files labled TODO given starting dir
def getTODOfiles(rootDir):
    files = [];
    for path, folderNames, fileNames in os.walk(rootDir):
        for name in fileNames:
            if name[:4] == "TODO": #Find the files we actually care about
                files.append((os.path.join(path,name), name));
    return files
