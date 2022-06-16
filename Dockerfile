FROM python:3

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py" ]
