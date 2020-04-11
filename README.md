## Demo
![Demo](demo/demo.gif)
## About
https://freeaudioconverter.net - convert an audio file to another format (high quality encoders are used) or extract the audio from a video. Many file formats are supported, click [here](https://freeaudioconverter.net/filetypes) for details. A recent addition is the ability to trim a video or audio file.

I'm not a proponent of lossy-to-lossy encoding which is something that you can do with this website, but perhaps you have an audio file that you'd like to convert to a format that is more compatible with certain devices/players. The best use of this website is using it to convert a lossless (e.g. WAV, FLAC) audio file to a lossy format for space saving. Or to extract the audio from a video. Simply upload the video and select your desired audio format, and you will receive an audio-only file of your desired format when the conversion is complete.
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
