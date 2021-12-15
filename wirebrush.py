import os
import core
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs

#######
# API #
#######

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

def get_users(store, config):
    """
    Subroutine for scraping user profile info
    Return: list
    """
    def get_from_session():
        userIDs = []
        # send GET request to user profiles page
        profiles_response = store.get(config.url+config.routes.profiles)
        
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
        users_response = store.post(config.url+config.routes.getprofiles, data=users_payload)

        # print to stdout if verbose
        if config.verbose:
            print("GetUserProfiles status: %s" % users_response.status_code)
            print(users_response.headers)
            print(users_response.text)

        # capture POST request response as json and extract only page count
        page_count = core.get_page_count(int(users_response.json()["Total"]), 40)

        # capture POST request response as json and extract UIDs
        # optional: save json to file
        pages = tqdm(range(page_count))
        for page in pages:
            users_payload["page"] = str(page+1)
            data = store.post(config.url+config.routes.getprofiles, data=users_payload).json()
            userIDs += [user["Id"] for user in data["Data"]]
            if config.save:
                core.write_to_file('data/users/users_%d.json' % page, data)

        return userIDs

    def get_from_file():
        userIDs = []
        datadir = os.path.join('.', store)
        for file in os.listdir(datadir):
            fpath = os.path.join(datadir, file)
            with open(fpath, 'r') as f:
                userIDs += [user["Id"] for user in json.load(f)["Data"]]

        if config.verbose:
            print("user ID length: %s" % len(userIDs))

        return userIDs

    return get_from_file() if type(store) == str else get_from_session()

def get_problems(store, config, uids):

    def get_from_session():
        problems_payload = {
            "sort": "",
            "page": "1",
            "pageSize": "15",
            "group": "",
            "filter": ""
        }

        problems = {}
        for uid in tqdm(uids[1230+38987+11852+10481:]):
            user_problems = {}
            problems_response = store.post(config.url+config.routes.getproblems+uid, data=problems_payload)
            if config.verbose:
                print('GetProblems status: %s' % problems_response.status_code)
                print(problems_response.headers)
                print(problems_response.text)

            page_count = get_page_count(int(problems_response.json()["Total"]), 15)
            if page_count == 0:
                continue
            
            print("problems found for user %s" % uid)
            for page in range(page_count):
                problems_payload["page"] = str(page+1)
                data = store.post(config.url+config.routes.getproblems+uid, data=problems_payload).json()
                user_problems.update({x["Id"] : x for x in data["Data"]})
            if config.save:
                write_to_file('data/problems/problems_%s.json' % uid, user_problems)
            problems.update(user_problems)

        return problems

    def get_from_file():
        problems = {}
        for file in os.listdir(store):
            fpath = os.path.join(store, file)
            with open(fpath, 'r') as f:
                problems.update({x["Id"] : x for x in json.load(f)["Data"]})

        if config.verbose:
            print("user ID length: %s" % len(userIDs))

    page_count = core.get_page_count(int(problems_response.json()["Total"]), 15)

    return get_from_file() if type(store) == str else get_from_session()


##########
# DRIVER #
##########
if __name__ == "__main__":
    # define path to config file and import
    config = core.import_json('config.json')

    # spawn a session
    with requests.session() as s:
        # login to site
        details = (s, config.username, config.password, config.url+config.routes.login)
        login_response = login(*details)
        assert login_response.headers.get('content-type') == 'application/json; charset=utf-8'

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
        userIDs = get_users('data/users', config) if os.path.isdir('data/users') else get_users(s, config)            
        # problems = get_problems('data/problems', config, userIDs) if os.path.isdir('data/problems') else get_problems(s, config, userIDs)
        problems = get_problems(s, config, userIDs)
        print(len(problems.keys()))