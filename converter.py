import os, logging

def setup_logger(name, log_file, level=logging.DEBUG):
    log_format = logging.Formatter('%(message)s')
    file_handler = logging.FileHandler(log_file)        
    file_handler.setFormatter(log_format)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    return logger

# Info logger
logger = setup_logger('logger', 'Info.log')

def ffmpeg(chosen_file, params):
    os.system(f'ffmpeg -hide_banner -progress progress.txt -y -i "{chosen_file}" {params}')

# MP3
def run_mp3(chosen_file, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, is_y_switch, output_name, is_downmix, output_path):
    try:
        if mp3_encoding_type == "cbr":  
            ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -b {cbr_abr_bitrate} - {output_path}.mp3')
            logger.info(command)
        elif mp3_encoding_type == "abr": 
            ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --preset {cbr_abr_bitrate} - {output_path}.mp3')
        elif mp3_encoding_type == "vbr": 
            if is_y_switch == "no":
                ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -V {mp3_vbr_setting} - {output_path}.mp3')
            else:
                ffmpeg(chosen_file, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -Y -V {mp3_vbr_setting} - {output_path}.mp3')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# AC3
def run_ac3(chosen_file, ac3_bitrate, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c:a ac3 -b:a {ac3_bitrate}k {output_path}.ac3')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
    
# AAC
def run_aac(chosen_file, fdk_type, fdk_cbr, fdk_vbr, output_name, is_downmix, is_fdk_lowpass, fdk_lowpass, output_path):
    try:
        if fdk_type == "fdk-cbr":
            if is_fdk_lowpass == "yes":
                ffmpeg(chosen_file, f'{is_downmix} -f wav - | fdkaac --comment "Encoded using freeaudioconverter.net" --bandwidth {fdk_lowpass} -b {fdk_cbr} - -o {output_path}.m4a')

            else:
                ffmpeg(chosen_file, f'{is_downmix} -f wav - | fdkaac --comment "Encoded using freeaudioconverter.net" -b {fdk_cbr} - -o {output_path}.m4a')
        else: # VBR
            if is_fdk_lowpass == "yes":
                ffmpeg(chosen_file, f'{is_downmix} -f wav - | fdkaac --comment "Encoded using freeaudioconverter.net" --bandwidth {fdk_lowpass} --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')
            else:
                ffmpeg(chosen_file, f'{is_downmix} -f wav - | fdkaac --comment "Encoded using freeaudioconverter.net" --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
            
# Opus
def run_opus(chosen_file, opus_encoding_type, slider_value, opus_cbr_bitrate, output_name, is_downmix, output_path):
    try:
        if opus_encoding_type == "opus-vbr": 
            ffmpeg(chosen_file, f'{is_downmix} -c:a libopus -b:a {slider_value}k {output_path}.opus')
        else: # CBR
            ffmpeg(chosen_file, f'{is_downmix} -c:a libopus -vbr off -b:a {opus_cbr_bitrate}k {output_path}.opus')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')

# FLAC
def run_flac(chosen_file, flac_compression, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c:a flac -compression_level {flac_compression} {output_path}.flac')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')

# Vorbis
def run_vorbis(chosen_file, vorbis_encoding, vorbis_quality, slider_value, output_name, is_downmix, output_path):
    try:
        if vorbis_encoding == "vbr_bitrate": # VBR with nominal bitrate
            ffmpeg(chosen_file, f'{is_downmix} -f wav - | oggenc -c "Comment=Encoded using freeaudioconverter.net" -b {slider_value} - -o {output_path}.ogg')
        elif vorbis_encoding == "vbr_quality": # True VBR
            ffmpeg(chosen_file, f'{is_downmix} -f wav - | oggenc -c "Comment=Encoded using freeaudioconverter.net" -q {vorbis_quality} - -o {output_path}.ogg')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')

# WAV
def run_wav(chosen_file, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} {output_path}.wav')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# MKV
def run_mkv(chosen_file, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c copy {output_path}.mkv')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# ALAC
def run_alac(chosen_file, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c:a alac {output_path}.m4a')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# CAF
def run_caf(chosen_file, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} {output_path}.caf')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# DTS
def run_dts(chosen_file, dts_bitrate, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c:a dca -b:a {dts_bitrate}k -strict -2 {output_path}.dts')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# Speex
def run_speex(chosen_file, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c:a libspeex {output_path}.spx')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')
# MKA
def run_mka(chosen_file, output_name, is_downmix, output_path):
    try:
        ffmpeg(chosen_file, f'{is_downmix} -c:a copy {output_path}.mka')
    except Exception as error:
        logger.error(error)
    else:
        logger.info(f'{chosen_file} converted.')