from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
import os
from loggers import log_this, log

trimmer = Blueprint('trimmer',__name__)

@trimmer.route("/trimmer", methods=["POST"])
def trim_file():

    if request.form["request_type"] == "upload_complete":
   
        chosen_file = request.files["chosen_file"]
        # Make the filename safe
        filename_secure = secure_filename(chosen_file.filename)
        # Save the uploaded file to the uploads folder.
        chosen_file.save(os.path.join("uploads", filename_secure))
        return ''

    if request.form["request_type"] == "trim":

        filename = request.form["filename"]
        log_this(f'wants to trim: {filename}')
        uploaded_file_path = os.path.join("uploads", secure_filename(filename))
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        ext = "." + filename.split(".")[-1]
        just_name = filename.split(".")[0]
        output_name = just_name + " [trimmed]" + ext

        log.info(f'/usr/local/bin/ffmpeg -y -i "{uploaded_file_path}" -ss {start_time} '
        f'-to {end_time} -c copy "conversions/{output_name}"')

        os.system(f'/usr/local/bin/ffmpeg -y -i "{uploaded_file_path}" -ss {start_time} '
        f'-to {end_time} -map 0:v? -map 0:a? -map 0:s? -c:v copy -c:a copy -c:s copy "conversions/{output_name}"')

        return {
            "message": "File trimmed. The trimmed file will now start downloading.",
            "downloadFilePath": f'/download/{output_name}'
        }

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@trimmer.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        return send_from_directory(f'{os.getcwd()}/conversions', filename, mimetype="audio/mp4")
    else:
        return send_from_directory(f'{os.getcwd()}/conversions', filename)