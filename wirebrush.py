# wirebrush.py - a scraper for climbing websites
#
# author: n8
# github: n8atnite
#

import os
import json
import pickle
import argparse
import requests
from bs4 import BeautifulSoup as bs

URL = 'https://www.moonboard.com/'
USERNAME = 'n8bot'
PASSWORD = 'qr2RkyKTDt8rxG2'
ROUTES = {
    'login': 'Account/Login/',
    'dash': 'Dashboard/Index',
    'index': 'Account/Index/',
    'profiles': 'Account/UserProfiles/',
    'getprofiles': 'Account/GetUserProfiles/',
    'user': 'Account/Profile/',
    'getproblems': 'Account/GetProblems/'
}
VERBOSE = False

def write_to_file(name, obj):
    ext = os.path.splitext(name)[1].lower()
    if ext == '.txt':
        with open(name, 'w') as file:
            try:
                thing = str(obj)
            except TypeError:
                print("Cannot convert object to string. Skipping file write...")
                return
            file.write(thing)
    elif ext == '.json':
        with open(name, 'w') as file:
            try:
                json.dump(obj, name, indent=4)
            except:
                print("Cannot jsonify object. Skipping file write...")
                return

# tokens for POST requests are generated on their parent page's html
# use this helper to get the token for a parent page after GETting it
def get_token(response, index):
    soup = bs(response.text, 'html.parser')
    return soup.findAll('input', {'name': '__RequestVerificationToken'})[index].get('value')

def login(session, uname, pwd, url):
    homepage = session.get(url)
    cookie = homepage.cookies['__RequestVerificationToken']
    token = get_token(homepage, 0)
    login_headers = {
        'Cookie': '__RequestVerificationToken=' + cookie,
    }
    login_payload = {
        '__RequestVerificationToken': token,
        'Login.Username': uname,
        'Login.Password': pwd
    }
    return session.post(url, headers=login_headers, data=login_payload)

def get_users(session, cookies, url, page):
    profiles_response = s.get(URL + ROUTES["profiles"])
    token = get_token(profiles_response, 0) # correct token found by guess-n-check
    users_payload = {
        "sort": "",
        "page": str(page),
        "pageSize": "40",
        "group": "",
        "filter": "",
        "__RequestVerificationToken": token
    }

    users_response = session.post(url, data=users_payload)
    if VERBOSE:
        print('GetUserProfiles status: %s' % users_response.status_code)
        print(users_response.headers)
        print(users_response.text)

    data = users_response.json()
    userIDs = [user['Id'] for user in data['Data']]
    return (userIDs, int(data['Total'])) if page == 1 else userIDs

with requests.session() as s:
    details = (s, USERNAME, PASSWORD, URL+ROUTES['login'])
    login_response = login(*details)
    cookies = (s.cookies['__RequestVerificationToken'], s.cookies['_MoonBoard'])
    s.headers.update({"Cookie": "__RequestVerificationToken=%s; _MoonBoard=%s" % cookies})

    if VERBOSE:
        print('login status: %s' % login_response.status_code)
        print(login_response.headers)
        print(login_response.text)
    
    userIDs, user_count = get_users(s, cookies, URL+ROUTES['getprofiles'], 1)
    print(user_count)
    print(userIDs)