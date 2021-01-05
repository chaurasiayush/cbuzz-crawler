import requests
from bs4 import BeautifulSoup
from sqlite3 import connect, IntegrityError
from scorecard import get_match

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


def driver_insertscorecardinfo():
    query = '''select * from matches_scorecard_toinsert'''

    qpins = '''insert into player_data(pid, name, team) values(?, ?, ?)'''

    qscore = '''insert into match_scorecard(match_code, pid, outby, notout, runs, ballfaced, 
                fours, sixes, strikerate, overs, maiden_overs, runs_given, wickets_taken, 
                noballs, wideballs) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    curr.execute(query)
    matches = curr.fetchall()
    c =0
    for match in matches[:]:
        print(" "*10, "MATCH ID - {}, {} VS {}".format(match[2], match[3], match[4]))
        print("-"*70)
        try:
            players = get_match(match[6])
            if players is None:
                print("NO MATCH RECORD FOUND, SKIPPING..")
                print("-" * 70, "\n")
                continue

            for player in players.keys():
                # print(player)
                p = players[player]
                args = (p['pid'], p['name'], p['team'])

                notout = 0
                if p['out_by'] == "none" or p['out_by'] == "not out":
                    notout = 1

                sargs = (
                    match[2], p['pid'], p['out_by'], notout, p['runs_scored'], p['balls_faced'], p['fours'],
                    p['sixes'], p['strike_rate'], p['overs'], p['maiden'], p['runs_given'], p['wickets'], p['no_balls'],
                    p['wide_balls'],
                )
                print(p['pid'].rjust(5, "0"), " - ", end="")
                try:
                    curr.execute(qpins, args)
                    print("(NEW PLAYER) ", end="")
                except IntegrityError as e:
                    pass

                try:
                    curr.execute(qscore, sargs)
                    print("PLAYER RECORD INSERTED SUCCESSFULLY")

                except IntegrityError as e:
                    print("PLAYER RECORD EXIST, SKIPPING..")
            # print(players)
            # print(players)
        except Exception as e:
            print(e.with_traceback())
            c = c+1

        print("-" * 70, "\n")
        conn.commit()
    print("ERROR COUNT - ",c)


# driver_insermatchlist()

driver_insertscorecardinfo()