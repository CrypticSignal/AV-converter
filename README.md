[![HitCount](http://hits.dwyl.com/BassThatHertz/AudioAndVideoConverter.svg)](http://hits.dwyl.com/BassThatHertz/AudioAndVideoConverter)
[![contributors welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

On https://av-converter.com you can:
- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis (in the .mka container), FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.
- Trim a video or audio file (will not work if using the Safari browser).
- Download a YouTube video or the audio only. The [webpage](https://freeaudioconverter.net/yt) is a [youtube-dl](https://github.com/ytdl-org/youtube-dl) wrapper.

## Table of Contents:
**[1]** [Features (audio/video converter)](https://github.com/BassThatHertz/AudioAndVideoConverter#features-audiovideo-converter)

**[2]** [Features (YouTube downloader)](https://github.com/BassThatHertz/AudioAndVideoConverter#features-youtube-downloader)

**[3]** [Supported Filetypes](https://github.com/BassThatHertz/AudioAndVideoConverter#supported-filetypes)

**[4]** [Audio and Video Decoder](https://github.com/BassThatHertz/AudioAndVideoConverter#notes-for-contributors)

**[5]** [External encoders used](https://github.com/BassThatHertz/AudioAndVideoConverter#external-encoders-used)

**[6]** [Other tool(s) used](https://github.com/BassThatHertz/AudioAndVideoConverter#other-tools-used)

**[7]** [Requirements for developers/running locally](https://github.com/BassThatHertz/AudioAndVideoConverter#requirements-for-developersrunning-locally)

**[8]** [Notes for contributors](https://github.com/BassThatHertz/AudioAndVideoConverter#notes-for-contributors)

## Features (audio/video converter):
- You can see the file upload progress as a percentage and also amount uploaded (MB) in realtime.
- Upload completion time is shown in realtime.
- Whilst the file is being converted, you can see how far into the file the encoder currently is. This information is updated every second.

## Features (YouTube downloader):
- Download as an MP3 or MP4 file, or simply the best quality video/audio stream that is available.
- If you choose to download as an MP3, the thumbnail of the video gets embedded as the cover art.
- Download the best quality audio stream without encoding it, so no lossy-to-lossy encoding is done (only applicable if you use the "Audio [best]" button.

## Supported Filetypes:
Many filetypes are supported, click [here](https://freeaudioconverter.net/filetypes) for details. Support for other filetypes may be added, feel free to [contact me](https://freeaudioconverter.net/contact) to enquire. 

## Audio and Video Decoder:
[FFmpeg](https://github.com/FFmpeg/FFmpeg)

## External encoders used:
LAME v3.100 | https://lame.sourceforge.io/

fdk-aac | https://github.com/mstorsjo/fdk-aac

opusenc opus-tools 0.2 (using libopus 1.3.1) | https://github.com/xiph/opus

libvorbis
## Other tool(s) used:
youtube-dl | https://github.com/ytdl-org/youtube-dl

## Requirements for developers/running locally:
You can run the Flask app locally for development purposes or if you want audio/video conversion to be quicker as the file(s) will not need to be uploaded to my server.
- Python **3.6+**
- FFmpeg

*When running locally, you will not be able to convert to AAC unless you [compile FFmpeg](https://trac.ffmpeg.org/wiki/CompilationGuide) with `--enable-libfdk-aac` in the configuration. Or, if you know what you're doing, you can edit the code in converter.py to use FFmpeg's native AAC encoder instead.*
- `pip install -r requirements.txt`

*If youtube-dl fails to install when using `pip install -r requirements.txt`, install it manually. Installation details can be found [here](https://github.com/ytdl-org/youtube-dl#installation).*
- Clone this repository.
- Uncomment `db.create_all()` in main.py and yt.py
- Change the value of `youtube_dl_path` in yt.py to the correct path.
- cd into the directory that main.py is and enter `python3 main.py` (or just `python` if that uses Python 3 for you) in the terminal.
- Enter localhost:5000 in the address bar of your web browser and hit enter.

# Building with Docker
Run these commands to build and run the Dockerfile. Note sudo is usually required on Linux.
```
docker build -t audio-and-video-converter .
docker run -p 5000:5000 audio-and-video-converter
```

## Notes for contributors
Contributors are welcome, simply submit a pull request.

Use f-strings rather than `.format()` if you know how to do so.
