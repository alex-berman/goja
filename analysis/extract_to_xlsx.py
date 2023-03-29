import argparse
import json

import xlsxwriter


def extract_to_xslx(log_path, xlsx_path):
    workbook = xlsxwriter.Workbook(xlsx_path)
    worksheets = {}
    for line in open(log_path):
        try:
            entry = json.loads(line)
        except:
            entry = None
        if entry:
            if 'event' in entry:
                event = entry['event']
                if event == 'utterance':
                    participant = entry['participant']
                    if participant in worksheets:
                        worksheet = worksheets[participant]
                    else:
                        name = participant[0:30]
                        worksheet = worksheets[participant] = workbook.add_worksheet(name)
    workbook.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='path to structured log')
    parser.add_argument('xlsx', help='path to XLSX output')
    args = parser.parse_args()
    extract_to_xslx(args.log, args.xlsx)