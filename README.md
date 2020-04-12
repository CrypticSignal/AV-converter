## Demo
![Demo](demo/demo.gif)
## About
On https://freeaudioconverter.net, you can:
- Convert an audio file to another format - MP3, AAC, WAV, FLAC, ALAC, CAF, Opus, Vorbis, AC3, DTS or Speex.
- Convert a video to an audio-only file (to any of the above formats).
- Trim a video or audio file [https://freeaudioconverter.net/file-trimmer]
- Convert a video to the MKV format (well, container).
## Supported filetypes
Many filetypes are supported, click [here](https://freeaudioconverter.net/filetypes) for details. Support for other filetypes may be added, feel free to [contact me](https://freeaudioconverter.net/contact) to enquire. 
## About me
I'm a 24-year-old from the UK. This website is a personal project of mine which I started working on in 2019. Over time I've added features and it's been a continual work-in-progress. I've been into audio for several years, and in case you didn't notice, my username is another way of saying "bass that hurts".
## Technologies and encoders used:
[Flask](https://github.com/pallets/flask) - a micro framework for building web applications with Python.

[FFmpeg](https://github.com/FFmpeg/FFmpeg)

LAME v3.100 | https://lame.sourceforge.io/

fdkaac (https://github.com/nu774/fdkaac) which is a command line encoder frontend for fdk-aac (https://github.com/mstorsjo/fdk-aac).

libopus 1.3.1 | https://github.com/xiph/opus

libvorbis 1.3.6 | https://github.com/xiph/vorbis
## Contributing
I'm open to contributors, especially those who are familiar with video encoding with FFmpeg because a consideration that I have is adding the ability to transcode a video (under a new Flask route (/video-encoder)) to expand on what users can do on the website. Feel free to contact me using the [contact](https://freeaudioconverter.net/contact) section of the website if you have any questions.
## License
Custom - see the [LICENSE](https://github.com/BassThatHertz/freeaudioconverter.net/blob/master/LICENSE) file for details.
