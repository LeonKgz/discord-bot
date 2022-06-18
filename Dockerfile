FROM python:3

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y install texlive-latex-base
RUN apt-get -y install texlive-fonts-recommended
RUN apt-get -y install texlive-fonts-extra
RUN apt-get -y install texlive-latex-extra
RUN apt-get -y install texlive-lang-cyrillic

COPY . .

CMD [ "python3", "main.py" ]
