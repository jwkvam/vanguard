#!/usr/bin/env python

import requests
import sys
import re
import pandas as pd

from bs4 import BeautifulSoup

VANGUARD_FUNDS_PAGE = 'http://quicktake.morningstar.com/fundfamily/vanguard/0C00001YUF/fund-list.aspx'
NAME_OFFSET = 9  # remove 'Vanguard ' from names

r = requests.get(VANGUARD_FUNDS_PAGE)
if r.status_code != 200:
  print('Could not retrieve funds page, code %d' % r.status_code)
  sys.exit(1)

soup_all = BeautifulSoup(r.text)

links = soup_all.find_all('a', href=re.compile('quote.morningstar.com/fund/f.aspx'))

funds = []

for link in links:
  f = {}
  f['name'] = link.text[NAME_OFFSET:]
  url = link['href'].strip()
  f['symbol'] = url[-5:]  # vanguard mutual funds are all 5 characters
  print(f['symbol'])

  r = requests.get(url)
  if r.status_code != 200:
    print('Received status %d when retrieving %s' % (r.status_code, f['name']))
    continue

  soup_fund = BeautifulSoup(r.text)
  
  fund_attr = soup_fund.find('div', class_='r_title')

  for i, child in enumerate(fund_attr.children):
    if i == 2:
      f['stars'] = int(child['class'][0][-1])
    if i == 3:
      f['medal'] = child['class'][0][2:-3]
  
  funds.append(f)

df = pd.DataFrame(funds, columns=['name', 'symbol', 'stars', 'medal'])
df.to_csv('vanguard_funds.csv', index=False, header=False)
  

