# wirebrush.py - a scraper for climbing websites
#
# author:       n8
# github:       n8atnite
#
# contributor:  mrp
# github:       factormrp
#

import os
import json
import pickle
import argparse
import requests
from bs4 import BeautifulSoup as bs

#######
# API #
#######

def import_config(path):
    """
    Loads in global configuration from json from given path
    Return: tuple of configuration values
    """
    with open(path) as f:
        data = json.load(f) 
    return data["URL"],data["USERNAME"],data["PASSWORD"],data["ROUTES"],data["VERBOSE"]

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
                json.dump(obj, name, indent=4)
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
    login_headers = {
        "Cookie": "__RequestVerificationToken=" + cookie,
    }
    login_payload = {
        "__RequestVerificationToken": token,
        "Login.Username": uname,
        "Login.Password": pwd
    }
    return session.post(url, headers=login_headers, data=login_payload)

def get_users(session, cookies, route_get_user_profiles, route_user_profiles, page):
    """
    Subroutine for scraping user profile info
    Return: list
    """
    # send GET request to user profiles page
    profiles_response = s.get(route_user_profiles)

    # get token from caller to craft correct POST payload
    token = get_token(profiles_response, 0) 
    users_payload = {
        "sort": "",
        "page": str(page),
        "pageSize": "40",
        "group": "",
        "filter": "",
        "__RequestVerificationToken": token
    }

    # send POST request for user profile data
    users_response = session.post(route_get_user_profiles, data=users_payload)

    # print to stdout if verbose
    if VERBOSE:
        print("GetUserProfiles status: %s" % users_response.status_code)
        print(users_response.headers)
        print(users_response.text)

    # capture POST request response as json and extract only list of user IDs
    data = users_response.json()
    userIDs = [user["Id"] for user in data["Data"]]
    return (userIDs, int(data["Total"])) if page == 1 else userIDs

##########
# DRIVER #
##########
if __name__ == "__main__":
    # define path to config file and import
    path = os.path.join("..","config.json")
    URL,USERNAME,PASSWORD,ROUTES,VERBOSE = import_config(path)

    # spawn a session
    with requests.session() as s:
        # login to site
        details = (s, USERNAME, PASSWORD, URL+ROUTES["login"])
        login_response = login(*details)

        # define the session specific cookies that have to be carried across requests
        cookies = (s.cookies["__RequestVerificationToken"], s.cookies["_MoonBoard"])

        # update session headers with 'cookies'
        s.headers.update({"Cookie": "__RequestVerificationToken=%s; _MoonBoard=%s" % cookies})

        # print out to stdout if verbose
        if VERBOSE:
            print("login status: %s" % login_response.status_code)
            print(login_response.headers)
            print(login_response.text)

        # 
        userIDs, user_count = get_users(s, cookies, URL+ROUTES["getprofiles"], 1)
        print(user_count)
        print(userIDs)
