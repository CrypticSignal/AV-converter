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

def setup_logger(name, log_file):
    log_format = logging.Formatter('%(levelname)s | %(message)s')
    file_handler = logging.FileHandler(log_file)        
    file_handler.setFormatter(log_format)
    logger = logging.getLogger(name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(10)
    logger.addHandler(file_handler)
    return logger

# Info logger
logger = setup_logger('logger', 'Info.txt')

def run_ffmpeg(chosen_file, params):
    os.system(f'ffmpeg -hide_banner -progress progress.txt -y -i "{chosen_file}" {params}')

def ffmpeg_pipe(chosen_file, params):
    os.system(f'ffmpeg -hide_banner -progress progress.txt -y -i "{chosen_file}" -f wav - | {params}')

# MP3
def run_mp3(chosen_file, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, is_y_switch, output_path):
    try:
        if mp3_encoding_type == "cbr":
            run_ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -b {cbr_abr_bitrate} - {output_path}.mp3')
        elif mp3_encoding_type == "abr": 
            run_ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" --preset {cbr_abr_bitrate} - {output_path}.mp3')
        elif mp3_encoding_type == "vbr": 
            if is_y_switch == "no":
                run_ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -V {mp3_vbr_setting} - {output_path}.mp3')
            else:
                run_ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -Y -V {mp3_vbr_setting} - {output_path}.mp3')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# AAC
def run_aac(chosen_file, fdk_type, fdk_cbr, fdk_vbr, is_fdk_lowpass, fdk_lowpass, output_path):
    try:
        if fdk_type == "fdk-cbr":
            if is_fdk_lowpass == "yes":
                ffmpeg_pipe(chosen_file, f'fdkaac --comment "Encoded using freeaudioconverter.net" --bandwidth {fdk_lowpass} -b {fdk_cbr} - -o {output_path}.m4a')

            else:
                ffmpeg_pipe(chosen_file, f'fdkaac --comment "Encoded using freeaudioconverter.net" -b {fdk_cbr} - -o {output_path}.m4a')
        else: # VBR
            if is_fdk_lowpass == "yes":
                ffmpeg_pipe(chosen_file, f'fdkaac --comment "Encoded using freeaudioconverter.net" --bandwidth {fdk_lowpass} --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')
            else:
                ffmpeg_pipe(chosen_file, f'fdkaac --comment "Encoded using freeaudioconverter.net" --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# WAV
def run_wav(chosen_file, is_keep_video, output_path):
    try:
        if is_keep_video == "yes":
            run_ffmpeg(chosen_file, f'-map 0:v -map 0:a:0 -c:v copy -c:a:0 pcm_s16le {output_path}.mkv')
        else:
            run_ffmpeg(chosen_file, f'{output_path}.wav')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# Opus
def run_opus(chosen_file, opus_encoding_type, slider_value, opus_cbr_bitrate, output_path):
    try:
        if opus_encoding_type == "opus-vbr":
            ffmpeg_pipe(chosen_file, f'opusenc --comment Comment="Encoded using freeaudioconverter.net" --bitrate {slider_value} - {output_path}.opus')
        else: # CBR
            ffmpeg_pipe(chosen_file, f'opusenc --comment Comment="Encoded using freeaudioconverter.net" --hard-cbr {opus_cbr_bitrate} - {output_path}.opus')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# Vorbis
def run_vorbis(chosen_file, vorbis_encoding, vorbis_quality, slider_value, output_path):
    try:
        if vorbis_encoding == "vbr_bitrate": # VBR with nominal bitrate
            ffmpeg_pipe(chosen_file, f'oggenc -c "Comment=Encoded using freeaudioconverter.net" -b {slider_value} - -o {output_path}.ogg')
        elif vorbis_encoding == "vbr_quality": # True VBR
            ffmpeg_pipe(chosen_file, f'oggenc -c "Comment=Encoded using freeaudioconverter.net" -q {vorbis_quality} - -o {output_path}.ogg')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# FLAC
def run_flac(chosen_file, is_keep_video, flac_compression, output_path):
    try:
        if is_keep_video == "yes":
            run_ffmpeg(chosen_file, f'-map 0:v -map 0:a:0 -c:v copy -c:a:0 flac {output_path}.mkv')
        else:
            run_ffmpeg(chosen_file, f'-c:a flac {output_path}.flac')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# ALAC
def run_alac(chosen_file, is_keep_video, output_path):
    try:
        if is_keep_video == "yes":
            run_ffmpeg(chosen_file, f'-map 0:v -map 0:a:0 -c:a:0 alac {output_path}.mkv')
        else:
            run_ffmpeg(chosen_file, f'-c:a alac {output_path}.m4a')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# AC3
def run_ac3(chosen_file, is_keep_video, ac3_bitrate, output_path):
    try:
        if is_keep_video == "yes":
            run_ffmpeg(chosen_file, f'-map 0:v -map 0:a:0 -c:a:0 ac3 -b:a:0 {ac3_bitrate}k {output_path}.mkv')
        else:
            run_ffmpeg(chosen_file, f'-c:a ac3 -b:a {ac3_bitrate}k {output_path}.ac3')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# DTS
def run_dts(chosen_file, is_keep_video, dts_bitrate, output_path):
    try:
        if is_keep_video == "yes":
            run_ffmpeg(chosen_file, f'-map 0:v -map 0:a:0 -c:a:0 dca -b:a:0 {dts_bitrate}k -strict -2 {output_path}.mkv')
        else:
            run_ffmpeg(chosen_file, f'-c:a ac3 -b:a {dts_bitrate}k -strict -2 {output_path}.dts')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# CAF
def run_caf(chosen_file, output_path):
    try:
        run_ffmpeg(chosen_file, f'{output_path}.caf')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# MKA
def run_mka(chosen_file, output_path):
    try:
        run_ffmpeg(chosen_file, f'-c:a copy {output_path}.mka')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')

# MKV
def run_mkv(chosen_file, output_path):
    try:
        run_ffmpeg(chosen_file, f'-c copy {output_path}.mkv')
    except Exception as error:
        logger.error(f'CONVERTER: {error}')
    else:
        logger.info(f'{chosen_file} converted.')