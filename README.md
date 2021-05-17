![Lines of code](https://img.shields.io/tokei/lines/github/CrypticSignal/av-converter?label=lines%20of%20code)
![GitHub repo size](https://img.shields.io/github/repo-size/CrypticSignal/av-converter)
![GitHub last commit](https://img.shields.io/github/last-commit/CrypticSignal/av-converter?color=blue)

On https://av-converter.com you can:

- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis, FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.
- Download a YouTube video or just the audio.

## Features (audio/video converter):

- You can see the file upload progress as a percentage and also amount uploaded (MB) in realtime.
- Upload completion time is shown in realtime.
- Whilst the file is being converted, an alert shows how much of the file (HH:MM:SS) has been converted so far. The alert is updated every second.

## Features (YouTube downloader):

- Download the video. MP4 format is available.
- Download the audio only. MP3 format is available.

## Supported Filetypes:

Many filetypes are supported, click [here](https://free-av-tools.com/filetypes) for details.

## Requirements for running locally:

You can run the Flask app locally for development purposes or if you want audio/video conversion to be quicker as the file(s) will not need to be uploaded to my server.

- npm
- Python **3.6+**
- [FFmpeg](https://ffmpeg.org/download.html)
- `cd backend`, `pip3 install -r requirements.txt`

## How to self-host:

- Clone this repository.
- add `"proxy": "http://127.0.0.1:5000"` to `frontend/package.json`.
- Change the value of `ffmpeg_path` in converter.py to the correct path.

Open 2 terminal windows.

Window 1:

- `cd backend`
- `pip3 install -r requirements.txt`
- `python3 main.py`

Window 2:

- `cd frontend`

- `npm install`

- Enter `npm start` and after a moment you should be taken to http://127.0.0.1:3000

**If you want to convert to AAC when running this web application locally:**

_When running locally, you will not be able to convert to AAC unless your build of FFmpeg has `--enable-libfdk-aac` in the configuration (if unsure, enter `ffmpeg -buildconf` in the terminal and look under `configuration:`). This is because this web application uses the high quality [fdk-aac](https://github.com/mstorsjo/fdk-aac) AAC encoder, and "the license of libfdk_aac is not compatible with GPL" ([source](https://trac.ffmpeg.org/wiki/Encode/AAC)). Therefore, you cannot download a pre-built FFmpeg binary that supports that encoder. [Here's](https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu) how to complile FFmpeg on Ubuntu/Debian/Mint with libfdk_aac support, if your build of FFmpeg does not have `--enable-libfdk-aac`. Or, if you know what you're doing, you can edit the code in converter.py to use FFmpeg's native AAC encoder instead._
