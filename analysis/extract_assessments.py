import argparse
import json
import csv


def extract(log_path, output_csv_path):
    assessments = {
        'assess_without_bot': {},
        'assess_with_bot': {}
    }

    def process_entry(entry):
        if 'event' in entry:
            event = entry['event']
            if event == 'update_assessment':
                process_assessment_update(entry)

    def process_assessment_update(entry):
        payload = entry['payload']
        state_specific_assessments = assessments[payload['state']]
        key = (payload['participant'], payload['case_index'])
        state_specific_assessments[key] = payload['assessment']

    for line in open(log_path):
        try:
            entry = json.loads(line)
        except json.decoder.JSONDecodeError:
            entry = None
        if entry:
            process_entry(entry)

    with open(output_csv_path, 'w') as csv_file:
        output = csv.writer(csv_file)
        for key in assessments['assess_without_bot'].keys():
            if key in assessments['assess_with_bot']:
                assessment_without_bot = assessments['assess_without_bot'][key]
                assessment_with_bot = assessments['assess_with_bot'][key]
                output.writerow([assessment_without_bot, assessment_with_bot])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='path to structured log')
    parser.add_argument('output', help='path to output CSV file')
    args = parser.parse_args()
    extract(args.log, args.output)
