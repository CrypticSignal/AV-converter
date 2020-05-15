import os, logging

# A function that checks if a variable contains a disallowed substring.
def variable_has_no_disallowed_substrings(variable_to_check, disallowed_substrings):
    for substring in disallowed_substrings:
        if substring in variable_to_check:
            return False
    # If we've gotten to this point, the loop has finished without the if-statement
    # ever being True, so the variable didn't contain a disallowed substring.
    return True

# If a variable in the list contains a disallowed string, return False.
# Otherwise, return True.
def check_no_variable_contains_bad_string(variables_list, disallowed_strings):
    for variable in variables_list:
        if not variable_has_no_disallowed_substrings(variable, disallowed_strings):
            return False
    return True

log_format = logging.Formatter('%(message)s')
file_handler = logging.FileHandler('Info.txt')        
file_handler.setFormatter(log_format)
logger = logging.getLogger('logger')
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.setLevel(10)
logger.addHandler(file_handler)

progress_file_path = 'info/progress.txt'

def run_ffmpeg(uploaded_file_path, params):
    try:
        os.system(f'/usr/local/bin/ffmpeg -hide_banner -progress {progress_file_path} -y -i "{uploaded_file_path}" {params}')
    except Exception as error:
        logger.error(f'CONVERTER ERROR: {error}')
    else:
        logger.info('File converted.')

def ffmpeg_pipe(uploaded_file_path, params):
    try:
        os.system(f'/usr/local/bin/ffmpeg -hide_banner -progress {progress_file_path} -y -i "{uploaded_file_path}" -f wav - | {params}')
    except Exception as error:
        logger.error(f'CONVERTER ERROR: {error}')
    else:
        logger.info('File converted.')

# MP3
def run_mp3(uploaded_file_path, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, is_y_switch, output_path):
    if mp3_encoding_type == "cbr":
        run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -b {cbr_abr_bitrate} - {output_path}.mp3')
    elif mp3_encoding_type == "abr": 
        run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" --preset {cbr_abr_bitrate} - {output_path}.mp3')
    elif mp3_encoding_type == "vbr": 
        if is_y_switch == "no":
            run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -V {mp3_vbr_setting} - {output_path}.mp3')
        else:
            run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -Y -V {mp3_vbr_setting} - {output_path}.mp3')

# AAC
def run_aac(uploaded_file_path, is_keep_video, fdk_type, fdk_cbr, fdk_vbr, is_fdk_lowpass, fdk_lowpass, output_path):

    if is_keep_video == "yes":

        if fdk_type == "fdk-cbr":
            if is_fdk_lowpass == "yes":
                run_ffmpeg(uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} -b:a {fdk_cbr}k {output_path}.mkv')
            else:
                run_ffmpeg(uploaded_file_path, f'-c:v copy -c:a libfdk_aac -b:a {fdk_cbr}k {output_path}.mkv')
        else: # VBR
            if is_fdk_lowpass == "yes":
                run_ffmpeg(uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} -vbr {fdk_vbr} {output_path}.mkv')
            else:
                run_ffmpeg(uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr {fdk_vbr} {output_path}.mkv')
        
    else: # Keep video not selected, use standalone fdkaac encoder.

        if fdk_type == "fdk-cbr":
            if is_fdk_lowpass == "yes":
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" --bandwidth {fdk_lowpass} -b {fdk_cbr} - -o {output_path}.m4a')
            else:
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" -b {fdk_cbr} - -o {output_path}.m4a')
        else: # VBR
            if is_fdk_lowpass == "yes":
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" --bandwidth {fdk_lowpass} --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')
            else:
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')

# WAV
def run_wav(uploaded_file_path, is_keep_video, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:v -map 0:a:0 -c:v copy -c:a:0 pcm_s16le {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'{output_path}.wav')

# MP4
def run_mp4(uploaded_file_path, encoding_speed, output_path):
    if encoding_speed == "keep_codec":
        run_ffmpeg(uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr 5 {output_path}.mp4')
    else:
        run_ffmpeg(uploaded_file_path, f'-c:v libx264 -preset {encoding_speed} -c:a libfdk_aac -vbr 5 {output_path}.mp4')

# Opus
def run_opus(uploaded_file_path, opus_encoding_type, slider_value, opus_cbr_bitrate, output_path):
    if opus_encoding_type == "opus-vbr":
        ffmpeg_pipe(uploaded_file_path, f'opusenc --comment Comment="Encoded using freeaudioconverter.net" --bitrate {slider_value} - {output_path}.opus')
    else: # CBR
        ffmpeg_pipe(uploaded_file_path, f'opusenc --comment Comment="Encoded using freeaudioconverter.net" --hard-cbr {opus_cbr_bitrate} - {output_path}.opus')

# Vorbis
def run_vorbis(uploaded_file_path, vorbis_encoding, vorbis_quality, slider_value, output_path):
    if vorbis_encoding == "vbr_bitrate": # VBR with nominal bitrate
        ffmpeg_pipe(uploaded_file_path, f'oggenc -c "Comment=Encoded using freeaudioconverter.net" -b {slider_value} - -o {output_path}.ogg')
    elif vorbis_encoding == "vbr_quality": # True VBR
        ffmpeg_pipe(uploaded_file_path, f'oggenc -c "Comment=Encoded using freeaudioconverter.net" -q {vorbis_quality} - -o {output_path}.ogg')

# FLAC
def run_flac(uploaded_file_path, is_keep_video, flac_compression, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:v -map 0:a:0 -c:v copy -c:a:0 flac {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-c:a flac {output_path}.flac')

# ALAC
def run_alac(uploaded_file_path, is_keep_video, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:v -map 0:a:0 -c:a:0 alac {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-c:a alac {output_path}.m4a')

# AC3
def run_ac3(uploaded_file_path, is_keep_video, ac3_bitrate, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:v -map 0:a:0 -c:a:0 ac3 -b:a:0 {ac3_bitrate}k {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-c:a ac3 -b:a {ac3_bitrate}k {output_path}.ac3')

# DTS
def run_dts(uploaded_file_path, is_keep_video, dts_bitrate, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:v -map 0:a:0 -c:a:0 dca -b:a:0 {dts_bitrate}k -strict -2 {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-c:a ac3 -b:a {dts_bitrate}k -strict -2 {output_path}.dts')

# CAF
def run_caf(uploaded_file_path, output_path):
    run_ffmpeg(uploaded_file_path, f'{output_path}.caf')

# MKA
def run_mka(uploaded_file_path, output_path):
    run_ffmpeg(uploaded_file_path, f'-c:a copy {output_path}.mka')

# MKV
def run_mkv(uploaded_file_path, output_path):
    run_ffmpeg(uploaded_file_path, f'-c copy {output_path}.mkv')