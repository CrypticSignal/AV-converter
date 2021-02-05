import json
import os
from datetime import datetime
from time import time
from flask import Flask, request, send_from_directory, session
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import converter  # converter.py
from loggers import log, log_this, log_visit
from trimmer import trimmer  # Importing the blueprint in trimmer.py
from yt import yt  # Importing the blueprint in yt.py
from utils import delete_file

app = Flask(__name__)
secret_key = str(os.urandom(16))
app.secret_key = secret_key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Set the maximum upload size to 3 GB.
max_upload_size = 3  # in GB.
app.config['MAX_CONTENT_LENGTH'] = max_upload_size * 1000 * 1000 * 1000
# Changes to the HTML files are reflected on the website without having to restart the Flask app.
app.jinja_env.auto_reload = True

app.register_blueprint(yt)
app.register_blueprint(trimmer)

# The database object (db) needs to be defined in main.py even though we're not using the database in main.py
# Otherwise you get the following error:
# 'AssertionError: The sqlalchemy extension was not registered to the current application.'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

os.makedirs('uploads', exist_ok=True)
os.makedirs('conversions', exist_ok=True)
previous_conversion = None


def run_converter(codec, params):
    codec_to_converter = {
                            'aac': converter.aac,
                            'ac3': converter.ac3,
                            'alac': converter.alac,
                            'dts': converter.dts,
                            'flac': converter.flac,
                            'mka': converter.mka,
                            'mkv': converter.mkv,
                            'mp3': converter.mp3,
                            'mp4': converter.mp4,
                            'opus': converter.opus,
                            'vorbis': converter.vorbis,
                            'wav': converter.wav
    }
    return codec_to_converter[codec](*params)


@app.route('/api', methods=['POST'])
def homepage():
    if request.form['request_type'] =='uploaded':
        log.info(f'\nUpload complete at {datetime.now().strftime("%H:%M:%S")}')
        log.info(request.files['chosen_file'])
        filename_secure = secure_filename(request.files['chosen_file'].filename)
        # Save the uploaded file to the uploads folder.
        request.files['chosen_file'].save(os.path.join('uploads', filename_secure))
        session['progress_filename'] = f'{str(time())[:-8]}.txt'
        with open(f'ffmpeg-progress/{session["progress_filename"]}', 'w'): pass
        return f'api/ffmpeg-progress/{session["progress_filename"]}'


@app.route('/api/convert', methods=['POST'])
def convert_file():
    data = request.form['states']
    
    filename = request.form['filename']
    uploaded_file_path = os.path.join("uploads", secure_filename(filename))

    chosen_codec = json.loads(data)['codec']
    crf_value = json.loads(data)['crfValue']
    video_mode = json.loads(data)['videoSetting']
    is_keep_video = json.loads(data)['isKeepVideo']

    # MP3
    mp3_encoding_type = json.loads(data)['mp3EncodingType']
    mp3_bitrate = json.loads(data)['sliderValue']
    mp3_vbr_setting = json.loads(data)['mp3VbrSetting']
    # AAC
    fdk_type = json.loads(data)['aacEncodingType']
    fdk_cbr = json.loads(data)['sliderValue']
    fdk_vbr = json.loads(data)['aacVbrMode']
    # Vorbis
    vorbis_encoding = json.loads(data)['vorbisEncodingType']
    vorbis_quality = json.loads(data)['qValue']
    # Vorbis/Opus
    opus_vorbis_slider = json.loads(data)['sliderValue']
    # AC3
    ac3_bitrate = json.loads(data)['ac3Bitrate']
    # FLAC
    flac_compression = json.loads(data)['flacCompression']
    # DTS
    dts_bitrate = json.loads(data)['dtsBitrate']
    # Opus
    opus_cbr_bitrate = json.loads(data)['sliderValue']
    opus_encoding_type = json.loads(data)['opusEncodingType']
    # WAV
    wav_bit_depth = json.loads(data)['wavBitDepth']
    # Desired filename
    output_name = request.form['output_name']

    log.info(f'They chose {chosen_codec} | Output Filename: {output_name}')
    output_path = os.path.join('conversions', output_name)

    # AAC
    if chosen_codec == 'AAC':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, fdk_type, fdk_cbr,
                    fdk_vbr, output_path]
        extension = run_converter('aac', params)

    # AC3
    elif chosen_codec == 'AC3':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, ac3_bitrate, output_path]
        extension = run_converter('ac3', params)

    # ALAC
    elif chosen_codec == 'ALAC':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, output_path]
        extension = run_converter('alac', params)

    # CAF
    elif chosen_codec == 'CAF':
        params = [session['progress_filename'], uploaded_file_path, output_path]
        extension = run_converter('caf', params)

    # DTS
    elif chosen_codec == 'DTS':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, dts_bitrate, output_path]
        extension = run_converter('dts', params)

    # FLAC
    elif chosen_codec == 'FLAC':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, flac_compression,
                    output_path]
        extension = run_converter('flac', params)

    # MKA
    elif chosen_codec == 'MKA':
        params = [session['progress_filename'], uploaded_file_path, output_path]
        extension = run_converter('mka', params)

    # MKV
    elif chosen_codec == 'MKV':
        params = [session['progress_filename'], uploaded_file_path, video_mode, crf_value, output_path]
        extension = run_converter('mkv', params)

    # MP3
    elif chosen_codec == 'MP3':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, mp3_encoding_type,
                    mp3_bitrate, mp3_vbr_setting, output_path]
        extension = run_converter('mp3', params)

    # MP4
    elif chosen_codec == 'MP4':
        params = [session['progress_filename'], uploaded_file_path, video_mode, crf_value, output_path]
        extension = run_converter('mp4', params)

    # Opus
    elif chosen_codec == 'Opus':
        params = [session['progress_filename'], uploaded_file_path, opus_encoding_type, opus_vorbis_slider,
                    opus_cbr_bitrate, output_path]
        extension = run_converter('opus', params)

    # Vorbis
    elif chosen_codec == 'Vorbis':
        params = [session['progress_filename'], uploaded_file_path, vorbis_encoding, vorbis_quality,
                    opus_vorbis_slider, output_path]
        extension = run_converter('vorbis', params)

    # WAV
    elif chosen_codec == 'WAV':
        params = [session['progress_filename'], uploaded_file_path, is_keep_video, wav_bit_depth,
                    output_path]
        extension = run_converter('wav', params)

    if extension['error'] is not None:
        return extension, 500

    else:
        # Filename after conversion.
        session["converted_file_name"] = f'{output_name}{extension["ext"]}'

        global previous_conversion
        if previous_conversion is not None:
            delete_file(previous_conversion)
        previous_conversion = f'conversions/{session["converted_file_name"]}'

        return extension


@app.route('/api/ffmpeg-progress/<filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory('ffmpeg-progress', filename)


# @app.route('/api/conversions/<filename>', methods=['GET'])
# def send_file(filename):
#     mimetype_value = 'audio/mp4' if os.path.splitext(filename)[1] == '.m4a' else ''
#     try:
#         return send_from_directory('conversions', filename, mimetype=mimetype_value, as_attachment=True)
#     except Exception as error:
#         log.error(f'Unable to send conversions/{filename}. Error: \n{error}')

    
if __name__ == '__main__':
    app.run(app, port=5000)
