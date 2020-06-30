from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
import os, subprocess
from loggers import log_this, log
import converter

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

        variables_to_validate = [filename, start_time, end_time]
        strings_not_allowed = ['command', ';', '$', '&&', '/', '\\' '"', '?', '*', '<', '>', '|', ':', '`', '.']

        # check_no_variable_contains_bad_string is a func defined in converter.py
        if converter.is_bad_string_in_variables(variables_to_validate, strings_not_allowed):
            return 'You tried being clever, but there\'s a server-side check for disallowed strings', 400

        else:
            log.info(f'ffmpeg -y -ss {start_time} -i "{uploaded_file_path}" '
            f'-to {end_time} -map 0 -c copy "trims/{output_name}"')

            subprocess.run(['ffmpeg', '-y', '-ss', start_time, '-i', uploaded_file_path, '-to', end_time,
            '-map', '0', '-c', 'copy', f'trims/{output_name}'])

            return {
                "message": "File trimmed. The trimmed file will now start downloading.",
                "downloadFilePath": f'/trims/{output_name}'
            }

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@trimmer.route("/trims/<filename>", methods=["GET"])
def download_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        log.info(f'[M4A] SENDING {filename}')
        return send_from_directory(f'{os.getcwd()}/trims', filename, mimetype="audio/mp4", as_attachment=True)
    else:
        log.info(f'SENDING {filename}')
        return send_from_directory(f'{os.getcwd()}/trims', filename, as_attachment=True)