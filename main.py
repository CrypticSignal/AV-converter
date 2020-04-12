from flask import Flask, request, render_template, send_from_directory, make_response, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import logging, os
import converter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from confidential import *

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000 # 5 GB max upload size.
app.jinja_env.auto_reload = True

socketio = SocketIO(app) # Turn the flask app into a SocketIO app.

def setup_logger(name, log_file, level=logging.DEBUG):
    log_format = logging.Formatter('%(message)s')
    file_handler = logging.FileHandler(log_file)        
    file_handler.setFormatter(log_format)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    return logger

info_logger = setup_logger('info_logger', 'Info.log')
visit_logger = setup_logger('visit_logger', 'Visit.log')
user_agent_logger = setup_logger('user_agent_logger', 'UserAgent.log')
socket_logger = setup_logger('socket_logger', 'Socket.log')

# Info.log
def log_this(message):
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H.%M.%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    info_logger.info(f'{current_datetime} | {client} {message}')

# Visit.log
def log_visit(message):
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H.%M.%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    visit_logger.info(f'{client} {message} on {current_datetime}')

# UserAgent.log
def log_user_agent():
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H.%M.%S')
    user_agent = request.headers.get('User-Agent')
    user_agent_logger.info(f'{current_datetime}\n{user_agent}')

# Socket.log
def log_socket(message):
    current_datetime = (datetime.now() + timedelta(hours=1)).strftime('%d-%m-%y at %H.%M.%S')
    client = request.environ.get("HTTP_X_REAL_IP").split(',')[0]
    socket_logger.info(f'{current_datetime} | {client} {message}.')

# FFmpeg will write the conversion progress to a txt file. Read the file eery second to get the current conversion progress every second.
def read_progress():
    while True:
        with open('progress.txt', 'r') as f:
            lines = f.readlines()
            # This gives us the amount of the file (HH:MM:SS) that has been converted so far.
            current_time = lines[-5].split('=')[-1].split('.')[0]
            info_logger.info(current_time)
            # If the amount converted is the same twice in a row, that means that the conversion is complete.
            if previous_time == current_time:
                info_logger.info("Conversion complete. Progress no longer being read.")
                break
            # Set the value of previous_time to current_time, so we can check if the value of previous_time is the same as the value of current_time in the next iteration of the loop.
            previous_time = current_time
            progress_message = current_time + " [HH:MM:SS]" + " of the file has been converted so far..."
            info_logger.info(progress_message)
            # Trigger a new event called "show progress" 
            socketio.emit('show progress', {'progress': progress_message})
            socketio.sleep(1)

@socketio.on('my event') # Decorator to catch an event called "my event"
def test_connect(): # test_connect() is the event callback function.
    log_socket("disconected")

@socketio.on('disconnect')
def test_disconnect():
    log_socket("connected")

@app.route("/")
def homepage():
    log_visit("visited homepage")
    log_user_agent()
    return render_template("home.html", title="FreeAudioConverter.net")

@app.route("/about", methods=["GET", "POST"])
def about():
    log_visit("visited about page")
    return render_template("about.html", title="About")

@app.route("/filetypes")
def filetypes():
    log_visit("visited filetypes")
    return render_template("filetypes.html", title="Filetypes")

@app.route("/file-trimmer")
def trimmer():
    log_visit("visited trimmer")
    return render_template("trimmer.html", title="File Trimmer")

@app.route("/game")
def game():
    log_visit("visited game")  
    return render_template("game.html", title="Game")

allowed_filetypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv","avi", "ac3", "3gp", "MTS", "webm", "ADPCM", "dts", "spx", "caf", "mov"]

@app.route("/", methods=["POST"])
def main():

    if request.form["requestType"] == "uploaded":

        chosen_file = request.files["chosen_file"]
        extension = (chosen_file.filename).split(".")[-1]

        if extension not in allowed_filetypes:
            return make_response(jsonify({"message": "Incompatible filetype selected."}), 415)

        # Make the filename safe
        filename_secure = secure_filename(chosen_file.filename)
        # Save the uploaded file to the uploads folder.
        chosen_file.save(os.path.join("uploads", filename_secure))

        response = make_response(jsonify({"message": "File uploaded. Converting..."}), 200)

        return response

    if request.form["requestType"] == "convert":

        try:
            socketio.start_background_task(read_progress)

        except Exception as error:
            info_logger.error(f'start_background_task error: {error}')

        else:
            info_logger.info("Started progress reader.")

        finally:
            file_name = request.form["file_name"]
            chosen_file = os.path.join("uploads", secure_filename(file_name))
            chosen_codec = request.form["chosen_codec"]

            # Put the JavaSript FormData into appropriately-named variables:

            # MP3
            mp3_encoding_type = request.form["mp3_encoding_type"]
            cbr_abr_bitrate = request.form["cbr_abr_bitrate"]
            mp3_vbr_setting = request.form["mp3_vbr_setting"]
            is_y_switch = request.form["is_y_switch"]
            # AAC
            fdk_type = request.form["fdk_type"]
            fdk_cbr = request.form["fdk_cbr"]
            fdk_vbr = request.form["fdk_vbr"]
            is_fdk_lowpass = request.form["is_fdk_lowpass"]
            fdk_lowpass = request.form["fdk_lowpass"]
            # Vorbis
            vorbis_encoding = request.form["vorbis_encoding"]
            vorbis_quality = request.form["vorbis_quality"]
            # Vorbis/Opus
            slider_value = request.form["slider_value"]
            # AC3 
            ac3_bitrate = request.form["ac3_bitrate"]
            # FLAC
            flac_compression = request.form["flac_compression"]
            # DTS
            dts_bitrate = request.form["dts_bitrate"]
            # Opus
            opus_cbr_bitrate = request.form["opus-cbr-bitrate"]
            opus_encoding_type = request.form["opus-encoding-type"]
            # Downmix multi-channel audio to stereo?
            is_downmix = request.form["is_downmix"]
            # Desired filename
            output_name = request.form["output_name"]

            log_this(f'Wants to convert "{file_name}" to {chosen_codec}.')
            info_logger.info(f'OUTPUT NAME: {output_name}')

            output_path = f'"/home/ubuntu/website/Conversions/{output_name}"'

            # Run the appropritate section of converter.py:

            if chosen_codec == 'MP3':
                converter.run_mp3(chosen_file, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, is_y_switch, output_name, is_downmix, output_path)
                extension = 'mp3'
            elif chosen_codec == 'AAC':
                converter.run_aac(chosen_file, fdk_type, fdk_cbr, fdk_vbr, output_name, is_downmix, is_fdk_lowpass, fdk_lowpass, output_path)
                extension = 'm4a'
            elif chosen_codec == 'Opus':
                converter.run_opus(chosen_file, opus_encoding_type, slider_value, opus_cbr_bitrate, output_name, is_downmix, output_path)
                extension = 'opus'                                                                     
            elif chosen_codec == 'FLAC':
                converter.run_flac(chosen_file, flac_compression, output_name, is_downmix, output_path)
                extension = 'flac'
            elif chosen_codec == 'Vorbis':
                converter.run_vorbis(chosen_file, vorbis_encoding, vorbis_quality, slider_value, output_name, is_downmix, output_path) 
                extension = 'ogg'
            elif chosen_codec == 'WAV':
                converter.run_wav(chosen_file, output_name, is_downmix, output_path)
                extension = 'wav'
            elif chosen_codec == 'MKV':
                converter.run_mkv(chosen_file, output_name, is_downmix, output_path)
                extension = 'mkv'
            elif chosen_codec == 'MKA':
                converter.run_mka(chosen_file, output_name, is_downmix, output_path)
                extension = 'mka'
            elif chosen_codec == 'ALAC':
                converter.run_alac(chosen_file, output_name, is_downmix, output_path)
                extension = 'm4a'
            elif chosen_codec == 'AC3':
                converter.run_ac3(chosen_file, ac3_bitrate, output_name, is_downmix, output_path)
                extension = 'ac3'
            elif chosen_codec == 'CAF':
                converter.run_caf(chosen_file, output_name, is_downmix, output_path)
                extension = 'caf'
            elif chosen_codec == 'DTS':
                converter.run_dts(chosen_file, dts_bitrate, output_name, is_downmix, output_path)
                extension = 'dts'
            else: # The chosen codec is Speex
                converter.run_speex(chosen_file, output_name, is_downmix, output_path)
                extension = 'spx'

            converted_file_name = output_name + "." + extension
           
            response = make_response(jsonify({
                "message": "File converted. The converted file will now start downloading.",
                "downloadFilePath": 'download/' + converted_file_name
            }), 200)

            return response

# CONTACT PAGE

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        send_from = "theaudiophile@outlook.com"
        send_to = "hshafiq@hotmail.co.uk"
        text = MIMEMultipart()
        text['From'] = send_from
        text['To'] = send_to
        text['Subject'] = "Your Website"
        body = request.form['message']
        text.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(my_email, password)
        text = text.as_string()
        server.sendmail(send_from, send_to, text)
        return make_response("Message sent!", 200)
    else:
        log_this("visited contact page")
        return render_template("contact.html", title="Contact")

# FILE TRIMMER

@app.route("/file-trimmer", methods=["GET", "POST"])
def trim_file():

    if request.form["request_type"] == "upload_complete":
   
        chosen_file = request.files["chosen_file"]

        extension = (chosen_file.filename).split(".")[-1]

        if extension not in allowed_filetypes:
            return make_response(jsonify({"message": "Incompatible filetype selected."}), 415)

        # Make the filename safe
        filename_secure = secure_filename(chosen_file.filename)

        # Save the uploaded file to the uploads folder.
        chosen_file.save(os.path.join("uploads", filename_secure))

        response = make_response(jsonify({"message": "File uploaded. Converting..."}), 200)

        return response

    if request.form["request_type"] == "trim":

        file_name = request.form["filename"]
        chosen_file = os.path.join("uploads", secure_filename(file_name))
        filename = request.form["filename"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        ext = "." + filename.split(".")[-1]
        just_name = filename.split(".")[0]
        output_name = just_name + " [trimmed]" + ext

        try:
            os.system(f'ffmpeg -y -i "{chosen_file}" -ss {start_time} -to {end_time} -c copy "{output_name}"')
        except Exception as error:
            info_logger.error(f'TRIM ERROR: {error}')
        else:
            info_logger.info('Trim complete.')

        response = make_response(jsonify({
            "message": "File converted. The converted file will now start downloading.",
            "downloadFilePath": 'download/' + output_name
        }), 200)

        return response

# Send the converted/trimmed file to the following URL, where <filename> is the "value" for downloadFilePath
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    just_extension = filename.split('.')[-1]
    try:
        if just_extension == "m4a":
            info_logger.info('Sending file to user...')
            return send_from_directory(os.getcwd() + "/Conversions", filename, mimetype="audio/mp4")
        else:
            return send_from_directory(os.getcwd()+ "/Conversions", filename)
    except Exception as error:
        info_logger.error(error)
    else:
        info_logger.info("File sent.")

if __name__ == "__main__":
    socketio.run(app)