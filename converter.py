import os

def ffmpeg(chosen_file, params):
    os.system(f'ffmpeg -hide_banner -i "{chosen_file}" {params}')

# MP3
def run_mp3(chosen_file, mp3_encoding_type, cbr_abr_bitrate, mp3_vbr_setting, output_name, radio_button):
    if mp3_encoding_type == "cbr":  
        ffmpeg(chosen_file, f'-ac 2 -vn -f wav - | lame -b {cbr_abr_bitrate} - "{output_name}".mp3')
    elif mp3_encoding_type == "abr": 
        ffmpeg(chosen_file, f'-ac 2 -vn -f wav - | lame --abr {cbr_abr_bitrate} - "{output_name}".mp3')
    elif mp3_encoding_type == "vbr": 
        ffmpeg(chosen_file, f'-ac 2 -vn -f wav - | lame -V {mp3_vbr_setting} - "{output_name}".mp3')

    # (-ac 2 is used because LAME only supports stereo files.)

# AC3
def run_ac3(chosen_file, ac3_bitrate, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn -c:a ac3 -b:a {ac3_bitrate}k "{output_name}".ac3')
    
# AAC
def run_aac(chosen_file, fdk_type, fdk_cbr, fdk_vbr, output_name, radio_button):
    if fdk_type == "fdk-cbr":
        ffmpeg(chosen_file, f'{radio_button} -vn -f wav - | sudo fdkaac -b {fdk_cbr} - -o "{output_name}".m4a')
    else: # VBR
        print(fdk_vbr)
        ffmpeg(chosen_file, f'{radio_button} -vn -f wav - | sudo fdkaac --bitrate-mode {fdk_vbr} - -o "{output_name}".m4a')

# Opus
def run_opus(chosen_file, opus_encoding_type, slider_value, opus_cbr_bitrate, output_name, radio_button):
    if opus_encoding_type == "opus-vbr": 
        ffmpeg(chosen_file, f'{radio_button} -vn -f wav - | opusenc --bitrate {slider_value} - "{output_name}".opus')
    else: # CBR
        ffmpeg(chosen_file, f'{radio_button} -vn -f wav - | opusenc --hard-cbr --bitrate {opus_cbr_bitrate} - "{output_name}".opus')

# FLAC
def run_flac(chosen_file, flac_compression, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn -c:a flac -compression_level {flac_compression} "{output_name}".flac')

# Vorbis
def run_vorbis(chosen_file, vorbis_encoding, vorbis_quality, slider_value, output_name, radio_button):
    # VBR with a nominal bitrate
    if vorbis_encoding == "vbr_bitrate":
        ffmpeg(chosen_file, f'{radio_button} -vn -f wav - | oggenc -b {slider_value} - -o "{output_name}".ogg')
    elif vorbis_encoding == "vbr_quality": # True VBR
        ffmpeg(chosen_file, f'{radio_button} -vn -f wav - | oggenc -q {vorbis_quality} - -o "{output_name}".ogg')

# WAV
def run_wav(chosen_file, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn "{output_name}".wav')

# MKV
def run_mkv(chosen_file, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -c copy "{output_name}".mkv')

# MKA
def run_mka(chosen_file, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn -c:a copy "{output_name}".mka')

# ALAC
def run_alac(chosen_file, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn -c:a alac "{output_name}".m4a')

# CAF
def run_caf(chosen_file, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn "{output_name}".caf')

# DTS
def run_dts(chosen_file, dts_bitrate, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn -c:a dca -b:a {dts_bitrate}k -strict -2 "{output_name}".dts')

# Speex
def run_speex(chosen_file, output_name, radio_button):
    ffmpeg(chosen_file, f'{radio_button} -vn -c:a libspeex "{output_name}".spx')