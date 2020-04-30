from sqlite3 import connect

conn  = connect('vhdb.sqlite3')
curr = conn.cursor()

query = '''select * from series_record'''
curr.execute(query)

for r in curr.fetchall():
    url = r[2]
    soup = Bea