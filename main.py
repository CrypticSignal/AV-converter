from flask import Flask, request, render_template, send_from_directory, make_response, jsonify, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from colorama import init
init()
from colorama import Fore, Style
import os
import converter
from time import time, strftime, sleep
from threading import Thread, Event
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Limit file upload size to 5GB.
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000

# Turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

thread = Thread()
thread_stop_event = Event()

def GetOutput():
    while not thread_stop_event.isSet():
       with open('1.txt', 'r') as f:
            lines = f.readlines()
            last_line = lines[-5:]
            last_line = last_line[0]
            last_line = last_line[:-8]
            last_line = last_line[9:]
            formatted_output = last_line + " [HH:MM:SS]" + " of the file has been converted so far..."
            # Trigger a new event called "show progress" 
            socketio.emit('show progress', {'number': formatted_output})
            socketio.sleep(1)

@socketio.on('my event') # Decorator to catch an event called "my event":
def test_connect(): # test_connect() is the event callback function.
    global thread # Need visibility of the global thread object
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@app.route("/")
def homepage():
    visit_time = strftime('%d-%m-%Y [%H:%M:%S]')
    print("Page Visit at {}".format(visit_time))
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/filetypes")
def filetypes():
    return render_template("filetypes.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/game")
def game():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def upload():
    allowed_filetypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv","avi", "ac3", "3gp", "MTS", "webm", "ADPCM", "dts", "spx", "caf"]

    if request.form["requestType"] == "upload": # Upload complete.
        
        # Get the time as soon as the upload is complete.
        visit_time = strftime('%d-%m-%Y [%H:%M:%S]')

        # Make a variable called chosen_file which is the uploaded audio file.
        chosen_file = request.files["chosen_file"]

        extension = (chosen_file.filename).split(".")[-1]
        print("Extension is " + extension)

        if extension not in allowed_filetypes:
            return make_response(jsonify({"message": "error: Incompatible filetype selected."}), 415)

        print("\n" + Fore.GREEN + chosen_file.filename + " uploaded at {}".format(visit_time))
        print(Style.RESET_ALL)
        # Sanitize the filename to make it safe (or something like that).
        filename_secure = secure_filename(chosen_file.filename)
        # Save the uploaded file to the uploads folder.
        chosen_file.save(os.path.join("uploads", filename_secure))
        res = make_response(jsonify({"message": "File uploaded. Converting..."}), 200)
        return res
    
    if request.form["requestType"] == "convert":
     
        # Start the textfile reading thread.
        thread = socketio.start_background_task(GetOutput)

        file_name = request.form["file_name"]
        chosen_file = os.path.join("uploads", secure_filename(file_name))
        chosen_codec = request.form["chosen_codec"]
        # Put the JavaSript FormData into appropriately-named variables:
        mp3_encoding_type = request.form["mp3_encoding_type"]
        cbr_abr_bitrate = request.form["cbr_abr_bitrate"]
        mp3_vbr_setting = request.form["mp3_vbr_setting"]
        # Fraunhofer
        fdk_type = request.form["fdk_type"]
        fdk_cbr = request.form["fdk_cbr"]
        fdk_vbr = request.form["fdk_vbr"]
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
        # Desired filename
        output_name = request.form["output_name"]
        # Downmix multi-channel audio to stereo?
        radio_button = request.form["radio_button"]

        # Run the appropritate section of converter.py:

        if chosen_codec == 'MP3':
            converter.run_mp3(chosen_file, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, output_name, radio_button)
            extension = 'mp3'
        elif chosen_codec == 'AC3':
            converter.run_ac3(chosen_file, ac3_bitrate, output_name, radio_button)
            extension = 'ac3'
        elif chosen_codec == 'AAC':
            converter.run_aac(chosen_file, fdk_type, fdk_cbr, fdk_vbr, output_name, radio_button)
            extension = 'm4a'
        elif chosen_codec == 'Opus':
            converter.run_opus(chosen_file, opus_encoding_type, slider_value, opus_cbr_bitrate, output_name, radio_button)
            extension = 'opus'                                                                                          
        elif chosen_codec == 'FLAC':
            converter.run_flac(chosen_file, flac_compression, output_name, radio_button)
            extension = 'flac'
        elif chosen_codec == 'Vorbis':
            converter.run_vorbis(chosen_file, vorbis_encoding, vorbis_quality, slider_value, output_name, radio_button) 
            extension = 'ogg'
        elif chosen_codec == 'WAV':
            converter.run_wav(chosen_file, output_name, radio_button)
            extension = 'wav'
        elif chosen_codec == 'MKV':
            converter.run_mkv(chosen_file, output_name, radio_button)
            extension = 'mkv'
        elif chosen_codec == 'MKA':
            converter.run_mka(chosen_file, output_name, radio_button)
            extension = 'mka'
        elif chosen_codec == 'ALAC':
            converter.run_alac(chosen_file, output_name, radio_button)
            extension = 'm4a'
        elif chosen_codec == 'CAF':
            converter.run_caf(chosen_file, output_name, radio_button)
            extension = 'caf'
        elif chosen_codec == 'DTS':
            converter.run_dts(chosen_file, dts_bitrate, output_name, radio_button)
            extension = 'dts'
        else: # The chosen codec is Speex
            converter.run_speex(chosen_file, output_name, radio_button)
            extension = 'spx'

        converted_file_name = output_name + "." + extension

        res = make_response(jsonify({
            "message": "File converted. The converted file will now start downloading.",
            "downloadFilePath": 'download/' + converted_file_name
        }), 200)

        return res

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        return send_from_directory(os.getcwd(), filename, mimetype="audio/m4a", as_attachment=True)   
    else:
        return send_from_directory(os.getcwd(), filename, as_attachment=True)
        
if __name__ == "__main__":
    socketio.run(app)