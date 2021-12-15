import os
import json
import aiohttp
import asyncio
from collections import namedtuple
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

USERS_PATH = './data/users.json'
PROBLEMS_PATH = './data/problems/problems_{}.json'
CONFIG_PATH = './config.json'
MAX_CONCURRENT_REQUESTS = 50
NUMCHUNKS = 200

class MoonBoardScraper:
    def __init__(self):
        self.config = self.import_config(CONFIG_PATH)
        self.cookies = ''
        self.headers = {"Cookie": self.cookies}
        self.problems_payload = {
            "sort": "",
            "page": "1",
            "pageSize": "100",
            "group": "",
            "filter": ""
        }

        self.timeout = aiohttp.ClientTimeout(
            total=0,
            connect=None,
            sock_connect=30,
            sock_read=30
        )
        self.connector = aiohttp.TCPConnector(limit_per_host=MAX_CONCURRENT_REQUESTS)
        self.session = aiohttp.ClientSession(self.config.url, connector=self.connector, timeout=self.timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    def import_config(self, path):
        """
        Loads in global configuration from json from given path
        Return: tuple of configuration values
        """
        with open(path) as f:
            return json.load(f, object_hook=lambda x: namedtuple('config', x.keys())(*x.values())) 

    def get_users(self, fpath):
       with open(fpath, 'r') as f:
           users = json.load(f)
           return list(users.keys())

    def get_page_count(self, total, size):
        return total//size + 1 if total > 0 else 0

    def get_token(self, html, index):
        """
        Helper for identifying the token of caller upon successful completion of GET request
        Return: string
        """
        soup = bs(html, "html.parser")
        return soup.findAll("input", {"name": "__RequestVerificationToken"})[index].get("value")

    def update_cookies(self, name, value):
        if self.cookies:
            self.cookies += ';'
        self.cookies += name + '=' + value
    
    async def login(self):
        async with self.session.get('/') as resp:
            assert resp.status == 200
            self.update_cookies('__RequestVerificationToken', resp.cookies['__RequestVerificationToken'].value)
            text = await resp.text()

        token = self.get_token(text, 0)
        login_payload = {
            "__RequestVerificationToken": token,
            "Login.Username": self.config.username,
            "Login.Password": self.config.password
        }

        async with self.session.post('/Account/Login', headers=self.headers, data=login_payload) as resp:
            assert resp.headers.get('content-type') == 'application/json; charset=utf-8'
            self.update_cookies('_MoonBoard', resp.cookies['_MoonBoard'].value)

    async def execute_tasks(self, tasks):
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        async with semaphore:
            bar = tqdm(total=len(tasks), position=0)
            for task in asyncio.as_completed(tasks):
                msg = await task
                bar.set_description(msg)
                bar.update()

    async def find_problems(self, uid, path):
        payload = self.problems_payload
        problems = {}
        status = 'problems found for user {} : {}'
        page_count = 0
        tmp = page_count
        
        try:
            async with self.session.post('/Account/GetProblems/'+uid, headers=self.headers, data=payload) as resp:
                if resp.headers.get('content-type') == 'application/json; charset=utf-8':
                    data = await resp.json()
                    page_count = self.get_page_count(data['Total'], 15)
                else:
                    status = 'Warning: user {} returned status: {}'
                    tmp = resp.status
        except Exception as e:
            print(e)
        
        if page_count != 0:
            for page in range(page_count):
                payload["page"] = str(page+1)
                async with self.session.post('/Account/GetProblems/'+uid, headers=self.headers, data=payload) as resp:
                    if resp.headers.get('content-type') == 'application/json; charset=utf-8':
                        data = await resp.json()
                        problems.update({x["Id"]:x for x in data["Data"]})
                    else:
                        status = 'Warning: user {} returned status {} on page %d' % page
                        tmp = resp.status

            with open(path.format(uid), "w") as file:
                json.dump(problems, file, indent=4)

        return status.format(uid, tmp)

async def main():
    async with MoonBoardScraper() as session:
        await session.login()

        users = session.get_users(USERS_PATH)
        chunks = [users[i::NUMCHUNKS] for i in range(NUMCHUNKS)]
        bar = tqdm(chunks)
        for board, query in session.config.boards._asdict().items():
            bar.set_description(board)
            session.problems_payload["filter"] = query
            for chunk in bar:
                await session.execute_tasks([session.find_problems(user, PROBLEMS_PATH) for user in chunk])

if __name__=='__main__':
    asyncio.run(main())