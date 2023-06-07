import argparse
import json


def generate_role(role):
    return role[0].upper()


def extract(log_path, output_dir_path):
    outputs = {}

    def output_file_path(participant):
        return f'{output_dir_path}/{participant}.txt'

    def process_entry(entry):
        if 'event' in entry:
            event = entry['event']
            if event == 'utterance':
                process_utterance(entry)
            elif event == 'restart_chat':
                process_restart_chat(entry)

    def process_utterance(entry):
        participant = entry['participant']
        output = get_output(participant)
        append_utterance_to_output(output, entry['utterance']['role'], entry['utterance']['content'])

    def get_output(participant):
        if participant in outputs:
            output = outputs[participant]
        else:
            output = outputs[participant] = open(output_file_path(participant), 'w')
        return output

    def append_utterance_to_output(output, role, content):
        output.write(f'{generate_role(role)}: {content}\n\n')

    def process_restart_chat(entry):
        participant = entry['payload']['participant']
        output = get_output(participant)
        output.write('-' * 40 + '\n\n')

    for line in open(log_path):
        try:
            entry = json.loads(line)
        except json.decoder.JSONDecodeError:
            entry = None
        if entry:
            process_entry(entry)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='path to structured log')
    parser.add_argument('output', help='path to output folder')
    args = parser.parse_args()
    extract(args.log, args.output)