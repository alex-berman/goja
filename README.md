# Goja: Research tool for collecting human-computer chat dialogues
Highlights:
- Integrated with OpenAI's chat API
- Logs dialogs in structured (JSON) form
- Participants just need a link; no registration required

## Installation
It is recommended to install and run Goja using virtualenv (Python >=3), as follows:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

To be able to use the built-in setup (diagnosis of coronary heart disease), download `processed.cleveland.data` from
https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/ and put it in
`web/datasets/`.

## Usage
First you need to set the OpenAI API key:
```
export OPENAI_API_KEY=<key here>
```

To run the server with the built-in setup:
```
export GOJA_SETUP=setups/heart.yml
./start.sh
```

The link for participation is now shown in the console (typically http://127.0.0.1:5000)
