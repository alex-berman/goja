import argparse
import json
import csv
import importlib
import yaml
import pandas as pd


def extract(log_path, settings_path, classifier_module_path, output_csv_path):
    settings = yaml.load(open(settings_path), yaml.Loader)
    if 'columns' in settings['cases']:
        names = settings['cases']['columns']
    else:
        names = None
    cases = pd.read_csv(settings['cases']['file'], names=names)

    classifier_module = importlib.import_module(classifier_module_path, '.')

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
                case_index = key[1]
                case_info = cases.loc[case_index]
                print(f'case_index={case_index}')
                print(f'case_info:\n{case_info}')
                print(f'assessment_without_bot={assessment_without_bot}')
                print(f'assessment_with_bot={assessment_with_bot}')
                ground_truth = case_info['target']
                classifier_assessment = classifier_module.predict(case_info)
                accuracy_without_bot = int(assessment_without_bot == ground_truth)
                classifier_accuracy = int(classifier_assessment == ground_truth)
                accuracy_with_bot = int(assessment_with_bot == ground_truth)
                output.writerow([accuracy_without_bot, classifier_accuracy, accuracy_with_bot])
                print(f'classifier_assessment={classifier_assessment}')
                print(f'accuracy_without_bot={accuracy_without_bot}')
                print(f'classifier_accuracy={classifier_accuracy}')
                print(f'accuracy_with_bot={accuracy_with_bot}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='path to structured log')
    parser.add_argument('settings', help='path to settings file (YML)')
    parser.add_argument('classifier', help='path to module containing classifier (AI)')
    parser.add_argument('output', help='path to output CSV file')
    args = parser.parse_args()
    extract(args.log, args.settings, args.classifier, args.output)
