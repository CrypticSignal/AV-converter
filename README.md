[![HitCount](http://hits.dwyl.com/BassThatHertz/AudioAndVideoConverter.svg)](http://hits.dwyl.com/BassThatHertz/AudioAndVideoConverter)
[![contributors welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

On https://free-av-tools.com you can:
- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis, FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.
- Trim an audio file (will not work if using the Safari browser).
- Download a YouTube video or the audio only.

## Features (audio/video converter):
- You can see the file upload progress as a percentage and also amount uploaded (MB) in realtime.
- Upload completion time is shown in realtime.
- Whilst the file is being converted, you can see how far into the file the encoder currently is. This information is updated every second.

## Features (YouTube downloader):
- Download the video. MP4 format is available.
- Download the audio only. MP3 format is available.

## Supported Filetypes:
Many filetypes are supported, click [here](https://freeaudioconverter.net/filetypes) for details.

## Requirements for developers/running locally:
You can run the Flask app locally for development purposes or if you want audio/video conversion to be quicker as the file(s) will not need to be uploaded to my server.
- Python **3.6+**
- [FFmpeg](https://ffmpeg.org/download.html)
- `pip3 install -r requirements.txt`

## How to self-host:
- Clone this repository.
- Change the value of `ffmpeg_path` in converter.py to the correct path.
- cd into the directory of this repository.
- `pip3 install -r requirements.txt`
- `python3 main.py`
- Enter localhost:5000 in the address bar of your web browser and hit enter.

**If you want to convert to AAC when running this web application locally:**

*When running locally, you will not be able to convert to AAC unless your build of FFmpeg has `--enable-libfdk-aac` in the configuration. This is because this web application uses the high quality [fdk-aac](https://github.com/mstorsjo/fdk-aac) AAC encoder, and "the license of libfdk_aac is not compatible with GPL" ([source](https://trac.ffmpeg.org/wiki/Encode/AAC)). Therefore, you cannot download a pre-built FFmpeg binary that supports that encoder. [Here's](https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu) how to complile FFmpeg on Ubuntu/Debian/Mint with libfdk_aac support, if your build of FFmpeg does not have `--enable-libfdk-aac`. Or, if you know what you're doing, you can edit the code in converter.py to use FFmpeg's native AAC encoder instead.*

# Building with Docker
Run these commands to build and run the Dockerfile.

*Note: sudo is usually required on Linux.*
```
docker build -t audio-and-video-converter .
docker run -p 5000:5000 audio-and-video-converter
```

## Notes for contributors
Contributors are welcome, simply submit a pull request and I ([BassThatHertz](https://github.com/BassThatHertz)) will have a look at it within 24 hours.

[Python files] No more than 120 characters per line. Use f-strings instead of `.format()` if you know how to do so. Comment sections of code where the purpose may not be obvious to the reader.
