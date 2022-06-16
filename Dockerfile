FROM python:3

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN sudo apt-get install texlive-latex-base
RUN sudo apt-get install texlive-fonts-recommended
RUN sudo apt-get install texlive-fonts-extra
RUN sudo apt-get install texlive-latex-extra
RUN pdflatex latex_source_name.tex
RUN sudo apt-cache search texlive russian
RUN sudo apt-get install texlive-lang-cyrillic

COPY . .

CMD [ "python3", "main.py" ]
