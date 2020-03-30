from flask import Flask, request, render_template, send_from_directory, make_response, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import os
import converter
from threading import Thread, Event

app = Flask(__name__)
socketio = SocketIO(app) # Turn the flask app into a SocketIO app.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000 * 1000 # 2 GB max upload size.

thread_stop_event = Event() # Not sure why this is needed, got it from https://github.com/shanealynn/async_flask/blob/master/application.py

def ReadProgress():
    while not thread_stop_event.isSet():
        with open('1.txt', 'r') as f:
            lines = f.readlines()
            get_time = lines[-5].split('=')[1].split('.')[0]
            progress_message = get_time + " [HH:MM:SS]" + " of the file has been converted so far..."
            # Trigger a new event called "show progress" 
            socketio.emit('show progress', {'progress': progress_message})
            socketio.sleep(1)

# Define the progress thread.
progress_thread = Thread(target=ReadProgress)

@socketio.on('my event') # Decorator to catch an event called "my event".
def test_connect(): # test_connect() is the event callback function.
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@app.route("/")
def homepage():
    return render_template("home.html", title="FreeAudioConverter.net")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/filetypes")
def filetypes():
    return render_template("filetypes.html", title="Filetypes")

@app.route("/video-trimmer")
def trimmer():
    return render_template("trimmer.html")

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")

@app.route("/game")
def game():
    return render_template("game.html", title="Game")

allowed_filetypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv","avi", "ac3", "3gp", "MTS", "webm", "ADPCM", "dts", "spx", "caf", "mov"]

@app.route("/", methods=["POST"])
def uploaded():

    if request.form["requestType"] == "uploaded":

        # Make a variable called chosen_file which is the uploaded file.
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

        if not progress_thread.is_alive():
            print("Thread not running. Starting...")
            progress_thread.start()

        file_name = request.form["file_name"]
        chosen_file = os.path.join("uploads", secure_filename(file_name))
        chosen_codec = request.form["chosen_codec"]
        # Put the JavaSript FormData into appropriately-named variables:
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
        # Desired filename
        output_name = request.form["output_name"]
        # Downmix multi-channel audio to stereo?
        is_downmix = request.form["is_downmix"]

        # Run the appropritate section of converter.py:

        if chosen_codec == 'MP3':
            converter.run_mp3(chosen_file, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, is_y_switch, output_name, is_downmix)
            extension = 'mp3'
        elif chosen_codec == 'AC3':
            converter.run_ac3(chosen_file, ac3_bitrate, output_name, is_downmix)
            extension = 'ac3'
        elif chosen_codec == 'AAC':
            converter.run_aac(chosen_file, fdk_type, fdk_cbr, fdk_vbr, output_name, is_downmix, is_fdk_lowpass, fdk_lowpass)
            extension = 'm4a'
        elif chosen_codec == 'Opus':
            converter.run_opus(chosen_file, opus_encoding_type, slider_value, opus_cbr_bitrate, output_name, is_downmix)
            extension = 'opus'                                                                                          
        elif chosen_codec == 'FLAC':
            converter.run_flac(chosen_file, flac_compression, output_name, is_downmix)
            extension = 'flac'
        elif chosen_codec == 'Vorbis':
            converter.run_vorbis(chosen_file, vorbis_encoding, vorbis_quality, slider_value, output_name, is_downmix) 
            extension = 'ogg'
        elif chosen_codec == 'WAV':
            converter.run_wav(chosen_file, output_name, is_downmix)
            extension = 'wav'
        elif chosen_codec == 'MKV':
            converter.run_mkv(chosen_file, output_name, is_downmix)
            extension = 'mkv'
        elif chosen_codec == 'MKA':
            converter.run_mka(chosen_file, output_name, is_downmix)
            extension = 'mka'
        elif chosen_codec == 'ALAC':
            converter.run_alac(chosen_file, output_name, is_downmix)
            extension = 'm4a'
        elif chosen_codec == 'CAF':
            converter.run_caf(chosen_file, output_name, is_downmix)
            extension = 'caf'
        elif chosen_codec == 'DTS':
            converter.run_dts(chosen_file, dts_bitrate, output_name, is_downmix)
            extension = 'dts'
        else: # The chosen codec is Speex
            converter.run_speex(chosen_file, output_name, is_downmix)
            extension = 'spx'

        converted_file_name = output_name + "." + extension

        response = make_response(jsonify({
            "message": "File converted. The converted file will now start downloading.",
            "downloadFilePath": 'download/' + converted_file_name
        }), 200)

        return response

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    just_extension = filename.split('.')[-1]
    if just_extension == "m4a":
        return send_from_directory(os.getcwd(), filename, mimetype="audio/m4a", as_attachment=True)   
    else:
        return send_from_directory(os.getcwd(), filename, as_attachment=True)

@app.route("/video-trimmer", methods=["GET", "POST"])
def trim_video():

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
        os.system(f'ffmpeg -y -i "{chosen_file}" -ss {start_time} -to {end_time} -c copy "{output_name}"')
        
        response = make_response(jsonify({
            "message": "File converted. The converted file will now start downloading.",
            "downloadFilePath": 'download/' + output_name
        }), 200)

        return response
        

@app.route("/download/<path:filename>", methods=["GET"])
def download_trimmed_file(filename):
    print("filename in path ting: " + filename)
    just_extension = filename.split('.')[-1]

    if just_extension == "m4a":
        return send_from_directory(os.getcwd(), filename, mimetype="audio/m4a", as_attachment=True)   
    else:
        return send_from_directory(os.getcwd(), filename, as_attachment=True)
        

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')