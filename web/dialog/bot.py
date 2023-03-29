import openai


MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0


class Bot:
    def __init__(self, api_key):
        self._api_key = api_key

    def get_response(self, dialog_history):
        completion = openai.ChatCompletion.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=dialog_history)
        return completion.choices[0].message.content
