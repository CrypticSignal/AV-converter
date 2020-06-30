FROM python:3

ADD ./ /

RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install ffmpeg

CMD [ "python", "./main.py" ]
