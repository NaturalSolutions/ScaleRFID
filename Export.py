import sqlite3
import csv
import os
import glob
from xlsxwriter.workbook import Workbook
import datetime


def export(dbPath, nameFile):
    con = sqlite3.connect(dbPath)
    outfile = open("/home/pi/Share/Public/temp.csv", 'w')
    outcsv = csv.writer(outfile)
    cursor = con.execute(
        'select ID_Reneco , Date, Weight, Note from session where Weight is not null')  # noqa: E501
    outcsv.writerow(['Tind_BagueId', 'DateSaisie', 'Poids', 'Notes'])
    outcsv.writerows(cursor.fetchall())
    outfile.close()
    date = datetime.datetime.now()
    with open("/home/pi/Share/Public/temp.csv", 'r') as csv_in, \
            open("/home/pi/Share/Public/" + nameFile + ".csv", 'w') as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)
        writer.writerow(['Tind_BagueId', 'DateSaisie', 'Poids', 'Notes'])
        p = 0
        for row in reader:
            if p != 0:
                writer.writerow(
                    [row[0]] + [date.strftime("%d/%m/%Y")] + [row[2]] + [row[3]])  # noqa: E501
            else:
                p = 1
    csv_in.close()
    csv_out.close()

    for csvfile in glob.glob(os.path.join(
            '/home/pi/Share/Public/', nameFile + ".csv")):
        workbook = Workbook("/home/pi/Share/Public/" + nameFile + ".xlsx")
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()


# if __name__ == '__main__':
#     export(dbPath)
