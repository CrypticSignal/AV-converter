## About
On https://freeaudioconverter.net, you can:
- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis (.ogg), FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.
- Trim a video or audio file (will not work if using the Safari browser).
- Download a YouTube video or the audio only. The [webpage](https://freeaudioconverter.net/yt) is a [youtube-dl](https://github.com/ytdl-org/youtube-dl) wrapper.
## Features (audio/video converter):
- You can see the file upload progress as a percentage and also amount uploaded (MB) in realtime.
- Upload completion time is shown in realtime.
- Whilst the file is being converted, you can see how far into the file the encoder currently is. This information is updated every second.
## Features (YouTube downloader):
- Download as an MP3 or MP4 file.
- If you choose to download as an MP3, the thumbnail of the video gets embedded as the cover art.
- Download the best quality audio stream without encoding it, so no lossy-to-lossy encoding is done (only applicable if you use the "Audio [best]" button.
## Supported filetypes:
Many filetypes are supported, click [here](https://freeaudioconverter.net/filetypes) for details. Support for other filetypes may be added, feel free to [contact me](https://freeaudioconverter.net/contact) to enquire. 
## To-do:
The file trimmer will not work when using the Safari browser as it does not support the HTML `<input type="time">`.
I may try to find another user-friendly way to allow the user to input their desired start and end time that is compatible with all browsers. Feel free to submit a pull request if you know of a good alternative implementation that is compatible with all browsers.
## Audio and video decoder:
[FFmpeg](https://github.com/FFmpeg/FFmpeg)
## External encoders used:
LAME v3.100 | https://lame.sourceforge.io/

fdk-aac | https://github.com/mstorsjo/fdk-aac

opusenc opus-tools 0.2 (using libopus 1.3.1) | https://github.com/xiph/opus

libvorbis
## External tool(s) used:
youtube-dl | https://github.com/ytdl-org/youtube-dl
## youtube-dl configuration for each download button:
**Video [MP4]** `-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"`

**Video [best quality]** youtube-dl <video_id>

**Audio [MP3]** `-x --embed-thumbnail --audio-format mp3 --audio-quality 0`

**Audio [best]** `-x <video_id>`
## FFmpeg configuration:
```
  --enable-gpl
  --enable-libfdk-aac 
  --enable-nonfree 
  --enable-libmp3lame 
  --enable-libopus 
  --enable-libvorbis 
  --enable-libvpx 
  --enable-libx264 
  --enable-libx265
```
## Requirements for development/running locally:
Python **3.6+**

`pip install youtube-dl`

`pip install -r requirements.txt`
## Contributing
Contributors are welcome, simply submit a pull request.
