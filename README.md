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

Visit the `/yt` endpoint to use the YouTube downloader, which is essentially a frontend for [yt-dlp](https://github.com/yt-dlp/yt-dlp). There are four options:

- **Video (MP4)** - downloads the best quality MP4 video stream and merges it with the best quality AAC audio stream. If no MP4 stream is available, this option will behave the same as **Video (best quality)**.
- **Video (best quality)** - downloads the best format (determined by yt-dlp) that contains video. If this format doesn't contain an audio stream, it is merged with the best quality audio stream. This option usually results in a video file in the WebM format with Opus audio.
- **Audio (best quality)** - downloads the best quality audio stream. Usually an Opus file with bitrate of ~160 kbps.
- **Audio (MP3)** - downloads the best quality audio stream and converts it to the MP3 format.

_If you are not sure which option to opt for, I recommend **Video (MP4)** and **Audio (MP3)** depending on whether you want the video or an audio-only file. This is because MP3 and MP4 files are more widely supported compared to Opus and WebM files._

# Usage

Simply visit https://av-converter.com. Alternatively, you can run this web application in a Docker container.

# Docker Instructions

- Clone this repository.
- `cd av-converter`
- ```
   docker compose up --build --wait && docker compose alpha watch
  ```
- Visit http://localhost:3001

Any changes you make in `/backend/src` or `/frontend/src` will be reflected without having to rebuild either container. Simply refresh your web browser.
