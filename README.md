# av-converter

On https://av-converter.com you can:

- Convert an audio file to another format - MP3, AAC, WAV, Opus, Vorbis, FLAC, ALAC, AC3, DTS or CAF.
- Convert a video to an audio-only file (to any of the above formats).
- Convert a video to the MP4 or MKV format.
- Change the audio codec of a video to MP3, AAC, AC3, DTS, WAV, FLAC or ALAC.
- Download a YouTube video or just the audio.

**Supported Filetypes:**

Click [here](https://av-converter.com/filetypes) for a list of supported filetypes.

**If you prefer, you can run this web application locally using Docker:**

1. Clone this repository.
2. Change the value of `ENVIRONMENT` in /backend/flask_app/**init**.py to something other than "production".
3. `cd av-converter`
4. `docker build -f Dockerfile.backend -t backend .`
5. `docker build -f Dockerfile.frontend -t frontend .`
6. `docker-compose up`
7. Visit http://localhost:3000

_If you get a "sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) table "converterDB" already exists" error, re-running `docker-compose up` fixed the issue for me._
