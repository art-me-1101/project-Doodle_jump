import sqlite3


con = sqlite3.connect('Chinook_Sqlite.sqlite')
cur = con.cursor()
a = cur.execute('''
select * from album
''').fetchall()
print(a)
con.commit()
con.close()




