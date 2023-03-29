import openai
import yaml


class Bot:
    def __init__(self, api_key, settings_yml_path):
        self._api_key = api_key
        self._settings = yaml.load(open(settings_yml_path), yaml.Loader)

    def get_response(self, dialog_history):
        def messages():
            if 'prompt' in self._settings:
                return [{'role': 'system', 'content': self._settings['prompt']}] + dialog_history
            else:
                return dialog_history

        completion = openai.ChatCompletion.create(
            model=self._settings['model'],
            temperature=self._settings['temperature'],
            messages=messages())
        return completion.choices[0].message.content
