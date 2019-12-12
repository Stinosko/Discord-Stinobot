# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 14:48:36 2019

@author: Admin
"""

import requests


headers = {"referer": "https://www.twitch.tv/nilaus/events"}


class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())



s = requests.Session()
r = s.get("https://www.twitch.tv/nilaus/events")

with open('test.html', 'wb') as f: 
    url = "https://gql.twitch.tv/gql"  
    h = s.post(url, headers=  headers)
    f.write(h.content)
