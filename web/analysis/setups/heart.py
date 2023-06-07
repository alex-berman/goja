def predict(case_info):
    condition_evaluations = [
        (case_info['thalach'] < 136.5),
        (case_info['cp'] != 3),
        (case_info['thal'] == '7.0'),
        (case_info['ca'] in ['1.0', '2.0', '3.0'])
    ]
    print(f'condition_evaluations={condition_evaluations}')
    num_true_conditions = len([value for value in condition_evaluations if value])
    print(f'num_true_conditions={num_true_conditions}')
    return int(num_true_conditions >= 2)
