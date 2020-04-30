import requests
from bs4 import BeautifulSoup
from sqlite3 import connect

headers = {'User-Agent': 'Mozilla/5.0'}
conn  = connect('vhdb.sqlite3')
curr = conn.cursor()

query = '''select * from series_record'''
curr.execute(query)

iquery = 'insert into series_record2 values(?, ?, ?, ?)'

for r in curr.fetchall()[:]:
    url = r[2]
    print(url)
    html = requests.get(url, headers).text

    args = (r[0], r[1], r[2], html)
    curr.execute(iquery, args)

conn.commit()



# def getmatchlist(year):
