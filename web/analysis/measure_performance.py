import argparse
import importlib
import yaml
import pandas as pd
from sklearn.metrics import accuracy_score


def measure_performance(settings_path, classifier_module_path):
    settings = yaml.load(open(settings_path), yaml.Loader)
    if 'columns' in settings['cases']:
        names = settings['cases']['columns']
    else:
        names = None

    def map_dataset_value_to_ground_truth(value):
        for ground_truth, values in settings['target']['dataset_values'].items():
            if value in values:
                return ground_truth
        raise Exception(f"Failed to map value {value} to ground truth label")

    cases = pd.read_csv(settings['cases']['file'], names=names)

    ground_truth = cases['target'].apply(map_dataset_value_to_ground_truth)
    classifier_module = importlib.import_module(classifier_module_path, '.')
    predictions = [
        classifier_module.predict(case)
        for _, case in cases.iterrows()
    ]
    print(accuracy_score(ground_truth, predictions))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('settings', help='path to settings file (YML)')
    parser.add_argument('classifier', help='path to module containing classifier (AI)')
    args = parser.parse_args()
    measure_performance(args.settings, args.classifier)
