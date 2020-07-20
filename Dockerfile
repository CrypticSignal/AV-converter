FROM python:3.8.3-slim-buster

ADD ./ /

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install git
RUN apt-get -y install ffmpeg
RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]