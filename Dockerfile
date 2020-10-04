FROM alfg/ffmpeg

WORKDIR /app

RUN apk update
RUN apk add build-base git wget curl \
    bash npm python3-dev py3-pip python3

COPY . .
   
RUN pip3 install -r requirements.txt

RUN curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl

EXPOSE 5000

CMD [ "python3", "main.py" ]
