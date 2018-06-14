import sqlite3
import csv


def export(dbPath, csvOutPath):
    con = sqlite3.connect(dbPath)
    outfile = open(csvOutPath,'wb')
    outcsv = csv.writer(outfile)

    cursor = con.execute('select * from session')

    outcsv.writerow([x[0] for x in cursor.description])

    outcsv.writerows(cursor.fetchall())

    outfile.close()
