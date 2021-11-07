# wirebrush.py - a scraper for climbing websites
#
# author: n8
# github: n8atnite
#

import json
import argparse
import requests
from bs4 import BeautifulSoup as bs

URL = 'https://www.moonboard.com/'
USERNAME = 'n8bot'
PASSWORD = 'qr2RkyKTDt8rxG2'
ROUTES = {
    'login': 'Account/Login/',
    'getprofiles': 'Account/GetUserProfiles/',
    'user': 'Account/Profile/',
    'getproblems': 'Account/GetProblems/'
}
VERBOSE = True

def login(session, uname, pwd, url):
    homepage = session.get(url)
    cookie = homepage.cookies['__RequestVerificationToken']
    soup = bs(homepage.text, 'html.parser')
    token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

    login_headers = {
        'DNT': '1',
        'Cookie': '__RequestVerificationToken=' + cookie,
    }

    login_payload = {
        '__RequestVerificationToken': token,
        'Login.Username': uname,
        'Login.Password': pwd
    }

    return session.post(url, headers=login_headers, data=login_payload), token

def get_users(session, url, token, page):
    users_payload = {
        'sort': '',
        'page': page,
        'pageSize': '40',
        'group': '',
        'filter': '',
        '__RequestVerificationToken': token
    }

    users_response = session.post(url, data=users_payload)
    print(users_response.status_code)
    

with requests.session() as s:
    login_response, token = login(s, USERNAME, PASSWORD, URL+ROUTES['login'])
    print('login status: %s' % login_response.status_code)
    if VERBOSE:
        print(login_response.headers)
        print(login_response.text)
    
    users = get_users(s, URL+ROUTES['getprofiles'], token, 1)

# dash_req = s.get(URL + 'Dashboard/Index')
# print(dash_req.status_code)
# print(dash_req.text)
