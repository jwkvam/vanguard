#!/usr/bin/env python

import requests
import sys
import re
import pandas as pd

from bs4 import BeautifulSoup

VANGUARD_BASE = 'https://personal.vanguard.com'
MORNINGSTAR_BASE = 'http://quotes.morningstar.com/fund/f?region=USA&t='

VANGUARD_FUNDS_PAGE = '/us/funds/vanguard/FundsTableView'

r = requests.get(VANGUARD_BASE + VANGUARD_FUNDS_PAGE)
if r.status_code != 200:
  print('Could not retrieve funds page, code %d' % r.status_code)
  sys.exit(1)

soup_all = BeautifulSoup(r.text)

links = soup_all.find_all('a', href=re.compile('/us/funds/snapshot'))

funds = []

for link in links:
  f = {}

  f['name'] = link.text
  r = requests.get(VANGUARD_BASE + link['href'])
  if r.status_code != 200:
    print('Received status %d when retrieving %s symbol name' % (r.status_code, f['name']))
    continue
  soup_name = BeautifulSoup(r.text)
  f['symbol'] = soup_name.find('span', class_='note').text[2:-1]

  print(f['symbol'])

  r = requests.get(MORNINGSTAR_BASE + f['symbol'])
  if r.status_code != 200:
    print('Received status %d when retrieving %s morningstar info' % (r.status_code, f['name']))
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
  

