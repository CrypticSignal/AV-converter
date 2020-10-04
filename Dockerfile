FROM alfg/ffmpeg

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apk update
RUN apk add build-base git wget curl \
    bash npm python-dev py3-pip python3

COPY . .
   
RUN pip3 install -r requirements.txt
RUN mkdir conversions
RUN mkdir uploads

RUN curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl

RUN chmod 777 /app/uploads
RUN chmod 777 /app/conversions


EXPOSE 5000

CMD [ "python3", "main.py" ]
