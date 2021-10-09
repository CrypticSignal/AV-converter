![Lines of code](https://img.shields.io/tokei/lines/github/CrypticSignal/av-converter?label=lines%20of%20code)
![GitHub repo size](https://img.shields.io/github/repo-size/CrypticSignal/av-converter)
![GitHub last commit](https://img.shields.io/github/last-commit/CrypticSignal/av-converter?color=blue)

On https://av-converter.com you can:

- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis, FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.

## Supported Filetypes:

Many filetypes are supported, click [here](https://av-converter.com/filetypes) for details.

## Requirements for running locally:

You can run the Flask app locally for development purposes or if you want audio/video conversion to be quicker as the file(s) will not need to be uploaded to my server.

- npm
- Python **3.6+**
- [FFmpeg](https://ffmpeg.org/download.html)
- `cd backend`, `pip3 install -r requirements.txt`

## How to run locally:

- Clone this repository.
- add `"proxy": "http://127.0.0.1:5000"` to `frontend/package.json`.
- Change the value of `ffmpeg_path` in converter.py to the correct path.

Open 2 terminal windows.

Window 1:

- `cd backend`
- `pip3 install -r requirements.txt`
- Create the database table by entering the following in the terminal:

```
python3
from flask_app import db
db.create_all()
exit()
```

- `python3 run.py`

Window 2:

- `cd frontend`
- `npm install`
- Enter `npm start` and after a moment you should be taken to http://127.0.0.1:3000
