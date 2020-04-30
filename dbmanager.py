import requests
from bs4 import BeautifulSoup
from sqlite3 import connect, IntegrityError

headers = {'User-Agent': 'Mozilla/5.0'}
conn = connect('vhdb.sqlite3')
curr = conn.cursor()


def insertmatchlist(seriesrow):

    linkpref = 'https://www.cricbuzz.com/live-cricket-scorecard'
    query = '''INSERT INTO MATCHES_INSERIES(series_code, match_code, team1, team2, result, file_path)
               VALUES(?, ?, ?, ?, ?, ?)'''
    html = seriesrow[3]

    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    matches = soup.find_all('div',class_= "cb-col-75 cb-col")

    # print(len(matches))

    for match in matches[:]:
        result = match.find('a', class_="cb-text-complete").get_text()
        m = match.find('a', class_="text-hvr-underline")
        url = m.get('href')
        # print(url)
        matchcode = url[16:]
        matchcode = matchcode[:matchcode.find('/')]

        url = linkpref + url[15:]
        # print(url)

        name = m.get_text()
        name = name[:name.find(',')].split(' vs ')
        # print(matchcode)

        try:
            ptitle = 'scorecards/' + str(seriesrow[0]) + '_' + matchcode + '.html'
            args = (seriesrow[0], matchcode, name[0], name[1], result, ptitle)

            curr.execute(query, args)

            phtml = requests.get(url).text
            f = open(ptitle, mode="w", encoding='utf8')
            f.write(phtml)

            print(matchcode, "- RECORD INSERTED!!")

        except IntegrityError as e:
            # print(e)
            print(matchcode, "- SKIPPING.. RECORD ALREADY EXIST")


def driver_insermatchlist():
    curr.execute('select * from series_record2')
    rows = curr.fetchall()

    for row in rows[:]:
        print(" " * 17 + "SERIES CODE - {}".format(row[0]) + " " * 20)
        print("-"*50)
        insertmatchlist(row)
        conn.commit()
        print("-" * 50)

driver_insermatchlist()