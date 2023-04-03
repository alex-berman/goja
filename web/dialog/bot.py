import openai


class Bot:
    def __init__(self, api_key, settings):
        self._api_key = api_key
        self._settings = settings

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
