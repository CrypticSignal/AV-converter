<div align="center">
  <img src="https://img.shields.io/badge/Node.js-0F9A41?style=for-the-badge&logo=node&color=black" alt="Node.js" />
  <img src="https://img.shields.io/badge/Express-0F9A41?style=for-the-badge&logo=express&color=black" alt="Express" />
  <img src="https://img.shields.io/badge/React-000000?style=for-the-badge&logo=react&logoColor=60DAFB" alt="React" />
  <img src="https://img.shields.io/badge/FFmpeg-000000?style=for-the-badge&logo=ffmpeg&logoColor=green" alt="FFmpeg" />
  <img src="https://img.shields.io/badge/Docker-000000?style=for-the-badge&logo=docker&logoColor=0db7ed" alt="Docker" />
</div>

# AV converter

Convert an audio or video file to any of the following formats:

- AAC
- AC3 (Dolby Digital)
- ALAC
- DTS
- FLAC
- MP3
- Opus
- Vorbis
- WAV

You can also convert a video to the MP4 or MKV format. You can simply change the container without transcoding, or change the video codec to H.264 (AVC) using the x264 encoder and the audio codec to AAC using the high quality Fraunhofer FDK AAC encoder.

# YouTube Downloader

Visit the [/yt endpoint](https://av-converter.com/yt) to use the YouTube downloader. The following options are available:

- Download the best quality video - the video is usually in the WebM container (.webm file extension).
- Download the video as an MP4 file.
- Extract the best quality audio - usually Opus format with a bitrate of ~160 kbps.
- Download the audio as an MP3 file.

# Usage

Simply visit https://av-converter.com. Alternatively, you can run this web application in a Docker container.

# Docker Instructions

1. Clone this repository.
2. Change the value of `ENVIRONMENT` in /backend/flask_app/**init**.py to something other than "production".
3. `cd av-converter`
4. `docker build -f Dockerfile.backend -t backend .`
5. `docker build -f Dockerfile.frontend -t frontend .`
6. `docker-compose up`
7. Visit http://localhost:3000
