[![HitCount](http://hits.dwyl.com/BassThatHertz/AudioAndVideoConverter.svg)](http://hits.dwyl.com/BassThatHertz/AudioAndVideoConverter)
[![contributors welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

On https://free-av-tools.com you can:
- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis (in the .mka container), FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.
- Trim a video or audio file (will not work if using the Safari browser).
- Download a YouTube video or the audio only. The [webpage](https://freeaudioconverter.net/yt) is a [youtube-dl](https://github.com/ytdl-org/youtube-dl) wrapper.

## Quick Links:
**[1]** [Features (audio/video converter)](https://github.com/BassThatHertz/AudioAndVideoConverter#features-audiovideo-converter)

**[2]** [Features (YouTube downloader)](https://github.com/BassThatHertz/AudioAndVideoConverter#features-youtube-downloader)

**[3]** [Supported Filetypes](https://github.com/BassThatHertz/AudioAndVideoConverter#supported-filetypes)

**[4]** [Tools used](https://github.com/BassThatHertz/AudioAndVideoConverter#tools-used)

**[5]** [Requirements for developers/running locally](https://github.com/BassThatHertz/AudioAndVideoConverter#requirements-for-developersrunning-locally)

## Features (audio/video converter):
- You can see the file upload progress as a percentage and also amount uploaded (MB) in realtime.
- Upload completion time is shown in realtime.
- Whilst the file is being converted, you can see how far into the file the encoder currently is. This information is updated every second.

## Features (YouTube downloader):
- Download as an MP3 or MP4 file, or simply the best quality video/audio stream that is available.
- Download the best quality audio stream without encoding it, so no lossy-to-lossy encoding is done (only applicable if you use the "Audio [best]" button.

## Supported Filetypes:
Many filetypes are supported, click [here](https://freeaudioconverter.net/filetypes) for details.

## Tools used:
[FFmpeg](https://github.com/FFmpeg/FFmpeg) is used for the audio and video converter. Configuration:
```
--enable-gpl --enable-libaom --enable-libass --enable-libfdk-aac --enable-libfreetype --enable-libmp3lame --enable-libopus --enable-libvorbis --enable-libvpx --enable-libx264 --enable-libx265 --enable-nonfree
```
[youtube-dl](https://github.com/ytdl-org/youtube-dl) is used for the YouTube downloader.

## Requirements for developers/running locally:
You can run the Flask app locally for development purposes or if you want audio/video conversion to be quicker as the file(s) will not need to be uploaded to my server.
- Python **3.6+**
- FFmpeg
- `pip install -r requirements.txt`

*If youtube-dl doesn't install when doing `pip install -r requirements.txt`, follow the instruction [here](https://github.com/ytdl-org/youtube-dl#installation) to install youtube-dl, unless you do not wish to do any development/testing related to the YouTube downloader.*
- Clone this repository.
- Change the value of `ffmpeg_path` in converter.py to the correct path.
- Change the value of `youtube_dl_path` in yt.py to the correct path.
- cd into the directory that main.py is and enter `python3 main.py` (or just `python` if that uses Python 3 for you) in the terminal.
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
