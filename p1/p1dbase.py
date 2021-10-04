import sqlite3
import datetime

class P1DBase:

    def __init__(self, dbasepath):
        self.dbasepath = dbasepath
        con = sqlite3.connect(self.dbasepath)
        cur = con.cursor()
        query = ('CREATE TABLE IF NOT EXISTS records ('
                      'timestamp   text,'
                      'delivtarief1   float,'
                      'delivtarief2   float'
                 ')')
        cur.execute(query)
        con.close()

    def record(self, timestamp, delivtarief1, delivtarief2):
        try:
            print(f"1 {timestamp.isoformat()}/{delivtarief1}/{delivtarief2}")
            con = sqlite3.connect(self.dbasepath)
            cur = con.cursor()
            query = 'INSERT INTO records VALUES (?,?,?)'
            cur.execute(query, (timestamp, delivtarief1, delivtarief2))
            con.commit()
            con.close()
            print(f"2 {timestamp.isoformat()}/{delivtarief1}/{delivtarief2}")
        except Exception as e:
            print(f"help: {e}")
