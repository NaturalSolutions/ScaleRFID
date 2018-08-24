import sqlite3
import csv
import os
import glob
from xlsxwriter.workbook import Workbook
import datetime


list_of_files = glob.glob('/home/pi/Share/Public/*.db') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
dbPath = latest_file

 

def export(dbPath):

    con = sqlite3.connect(dbPath)
    date = str(datetime.datetime.now())[0:10]
    name_file = "WeightsFile_" + date
    name_file = name_file.replace("-","")
    dateDB = date[8] +  date[9] + '/' + date[5] + date[6] + '/'+ date[0] + date[1] + date[2] +  date[3]
    """outfile = open("/home/pi/Share/Public/" + name_file + ".csv",'w')"""
    outfile = open("/home/pi/Share/Public/hi.csv",'w')
    outcsv = csv.writer(outfile)
    cursor = con.execute('select ID_Reneco , Date, Weight, Note from session where Weight is not null')
    outcsv.writerow(['Tind_BagueId','DateSaisie','Poids','Notes'])
    outcsv.writerows(cursor.fetchall())
    outfile.close()

    with open("/home/pi/Share/Public/hi.csv",'rt') as csv_in, open("/home/pi/Share/Public/" + name_file + ".csv",'w') as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)
        for row in reader:
            writer.writerow([row[0]] + [dateDB] + [row[2]] + [row[3]])

    
    for csvfile in glob.glob(os.path.join('/home/pi/Share/Public/'+ name_file+ ".csv")):
        workbook = Workbook("/home/pi/Share/Public/" + name_file + ".xlsx")
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()

if __name__ == '__main__':        
    export(dbPath)
