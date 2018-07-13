import sqlite3
import csv
import os
import glob
from xlsxwriter.workbook import Workbook
import datetime

dbPath = '/home/pi/Share/Public/releve.db'
csvInPath = '/home/pi/Share/Public/data.csv'
csvOutPath = '/home/pi/Share/Public/releve.csv'

def export(dbPath, csvInPath):
    con = sqlite3.connect('dbPath')
    outfile = open(csvInPath,'w')
    outcsv = csv.writer(outfile)
    cursor = con.execute('select ID_Reneco , Date, Weight, Note from session where Weight is not null')
    outcsv.writerow(['TInd_BagueId','DateSasie','Poids','Notes'])
    outcsv.writerows(cursor.fetchall())
    outfile.close()


def convert(csvOutPath):
    for csvfile in glob.glob(os.path.join('.',csvOutPath)):
        date = str(datetime.datetime.now())[0:10]
        workbook = Workbook("ProtocolePoids_" + date + '.xlsx')
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()