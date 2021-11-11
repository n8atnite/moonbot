import os
import json
import pickle
import argparse
import requests
from types import SimpleNamespace
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

#######
# API #
#######

def get_page_count(total, size):
    return total//size + 1

def import_config(path):
    """
    Loads in global configuration from json from given path
    Return: tuple of configuration values
    """
    with open(path) as f:
        return json.load(f, object_hook=lambda x: SimpleNamespace(**x)) 

def write_to_file(name, obj):
    """
    Handler for writing an object into a file with given name
    Return: None
    """
    # identify extension of object
    ext = os.path.splitext(name)[1].lower()

    # handle case of txt
    if ext == ".txt":
        with open(name, "w") as file:
            try:
                thing = str(obj)
            except TypeError:
                print("Cannot convert object to string. Skipping file write...")
                return
            file.write(thing)
    # handle case of json
    elif ext == ".json":
        with open(name, "w") as file:
            try:
                json.dump(obj, file, indent=4)
            except:
                print("Cannot jsonify object. Skipping file write...")
                return

def get_token(response, index):
    """
    Helper for identifying the token of caller upon successful completion of GET request
    Return: string
    """
    soup = bs(response.text, "html.parser")
    return soup.findAll("input", {"name": "__RequestVerificationToken"})[index].get("value")

def login(session, uname, pwd, url):
    """
    Subroutine for logging into the webpage
    Return: Response
    """
    # send GET request to homepage
    homepage = session.get(url)

    # identify the unique session token "cookie"
    cookie = homepage.cookies["__RequestVerificationToken"]

    # identify the embedded CFRS token "token"
    token = get_token(homepage, 0)

    # add "cookie" and "token" to session headers
    login_headers = {"Cookie": "__RequestVerificationToken=" + cookie}
    login_payload = {
        "__RequestVerificationToken": token,
        "Login.Username": uname,
        "Login.Password": pwd
    }
    return session.post(url, headers=login_headers, data=login_payload)

def get_users(session, config):
    """
    Subroutine for scraping user profile info
    Return: list
    """
    # send GET request to user profiles page
    profiles_response = s.get(config.url+config.routes.profiles)

    # get token from caller to craft correct POST payload
    token = get_token(profiles_response, 0) 
    users_payload = {
        "sort": "",
        "page": "1",
        "pageSize": "40",
        "group": "",
        "filter": "",
        "__RequestVerificationToken": token
    }

    # send POST request for user profile data
    users_response = session.post(config.url+config.routes.getprofiles, data=users_payload)

    # print to stdout if verbose
    if config.verbose:
        print("GetUserProfiles status: %s" % users_response.status_code)
        print(users_response.headers)
        print(users_response.text)

    # capture POST request response as json and extract only page count
    page_count = get_page_count(int(users_response.json()["Total"]), 40)

    # capture POST request response as json and extract UIDs
    # optional: save json to file
    userIDs = []
    pages = tqdm(range(1779+1836+1025, page_count))
    for page in pages:
        users_payload["page"] = str(page+1)
        data = session.post(config.url+config.routes.getprofiles, data=users_payload).json()
        userIDs.append([user["Id"] for user in data["Data"]])
        if config.save:
            write_to_file('data/users/users_%d.json' % page, data)

    return userIDs

def get_problems(session, config, uid):
    problems_payload = {
        "sort": "",
        "page": "1",
        "pageSize": "15",
        "group": "",
        "filter": ""
    }

    problems_response = session.post(config.url+config.routes.getproblems+uid, data=problems_payload)
    if config.verbose:
        print('GetProblems status: %s' % problems_response.status_code)
        print(problems_response.headers)
        print(problems_response.text)

    page_count = get_page_count(int(problems_response.json()["Total"]), 15)

    problems = {}
    for page in range(page_count):
        problems_payload["page"] = str(page+1)
        data = session.post(config.url+config.routes.getproblems+uid, data=problems_payload).json()
        problems.update({x["Id"] : x for x in data["Data"]})

    return problems

##########
# DRIVER #
##########
if __name__ == "__main__":
    # define path to config file and import
    config = import_config('config.json')

    # spawn a session
    with requests.session() as s:
        # login to site
        details = (s, config.username, config.password, config.url+config.routes.login)
        login_response = login(*details)

        # define the session specific cookies that have to be carried across requests
        cookies = (s.cookies["__RequestVerificationToken"], s.cookies["_MoonBoard"])

        # update session headers with 'cookies'
        s.headers.update({"Cookie": "__RequestVerificationToken=%s; _MoonBoard=%s" % cookies})

        # print out to stdout if verbose
        if config.verbose:
            print("login status: %s" % login_response.status_code)
            print(login_response.headers)
            print(login_response.text)

        # 
        userIDs = get_users(s, config)
        # print(userIDs)
