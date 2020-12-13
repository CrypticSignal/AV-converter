import os
import subprocess

from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename

from loggers import log, log_this

trimmer = Blueprint('trimmer', __name__)
os.makedirs('trims', exist_ok=True)


@trimmer.route("/trimmer", methods=["POST"])
def trim_file():

    if request.form["request_type"] == "upload_complete":

        uploaded_file = request.files["chosen_file"]
        # Make the filename safe
        filename_secure = secure_filename(uploaded_file.filename)
        # Save the uploaded file to the trims folder.
        uploaded_file.save(os.path.join('uploads', filename_secure))

        # Empty the trims folder to ensure that there will be enough storage space for the trimmed file.
        if os.path.exists('trims'):
            for file in os.listdir('trims'):
                os.remove(os.path.join('trims', file))
                log.info(f'Deleted trims/{file}')
        return ''

    if request.form["request_type"] == "trim":

        filename = request.form["filename"]
        log_this(f'wants to trim: {filename}')
        uploaded_file_path = os.path.join("uploads", secure_filename(filename))
        start_time = request.form["start_time"]
        log.info(f'Start: {start_time}')
        end_time = request.form["end_time"]
        log.info(f'End: {end_time}')
        just_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        output_name = f'{just_name} [trimmed]{extension}'
        output_file_path = os.path.join('trims', output_name)

        try:
            subprocess.run(['ffmpeg', '-y', '-i', uploaded_file_path, '-ss', start_time, '-to', end_time,
                           '-map', '0', '-c', 'copy', output_file_path])
        except Exception as error:
            log.error(f'Unable to trim file: \n{error}')

        return output_file_path


@trimmer.route("/trims/<filename>", methods=["GET"])
def download_file(filename):
    log.info(f'https://free-av-tools.com/trims/{filename}')
    mimetype_value = 'audio/mp4' if os.path.splitext(filename)[1] == ".m4a" else ''
    try:
        return send_from_directory('trims', filename, mimetype=mimetype_value, as_attachment=True)
    except Exception as error:
        log.error(f'Unable to send file. Error: \n{error}')
    finally:
        os.remove(f'trims/{filename}')

