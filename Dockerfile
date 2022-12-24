FROM python:3

COPY bot.py bot.py
COPY yf_utils yf_utils
COPY requirements.txt requirements.txt
COPY bot_config.json bot_config.json

RUN pip install -r requirements.txt

CMD python3 bot.py