import os, logging

# A function that checks if a variable contains a disallowed substring.
def variable_has_no_disallowed_substrings(variable_to_check, disallowed_substrings):
    for substring in disallowed_substrings:
        if substring in variable_to_check:
            return False
    # If we've gotten to this point, the loop has finished without the if-statement ever being True, 
    # so the variable didn't contain a disallowed substring.
    return True

# If a variable in the list contains a disallowed string, return False. Otherwise, return True.
def check_no_variable_contains_bad_string(variables_list, disallowed_strings):
    for variable in variables_list:
        if not variable_has_no_disallowed_substrings(variable, disallowed_strings):
            return False
    return True

log_format = logging.Formatter('%(message)s')
file_handler = logging.FileHandler('info/Info.txt')        
file_handler.setFormatter(log_format)
logger = logging.getLogger('logger')
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.setLevel(10)
logger.addHandler(file_handler)

progress_file_path = 'progress.txt'

def run_ffmpeg(uploaded_file_path, params):
    logger.info(params)
    os.system(f'/usr/local/bin/ffmpeg -hide_banner -progress {progress_file_path} -y -i "{uploaded_file_path}" '
    f'{params}')
    
def ffmpeg_pipe(uploaded_file_path, params):
    logger.info(params)
    os.system(f'/usr/local/bin/ffmpeg -hide_banner -progress {progress_file_path} -y -i "{uploaded_file_path}" -f wav'
    f' - | {params}')

# MP3
def run_mp3(uploaded_file_path, mp3_encoding_type, mp3_bitrate, mp3_vbr_setting, is_y_switch, output_path):

    if mp3_encoding_type == "cbr":
        run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" '
        f'-b {mp3_bitrate} - {output_path}.mp3')
        
    elif mp3_encoding_type == "abr": 
        run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" '
        f'--preset {mp3_bitrate} - {output_path}.mp3')
    elif mp3_encoding_type == "vbr": 
        if is_y_switch == "no":
            run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" '
            f'-V {mp3_vbr_setting} - {output_path}.mp3')
        else:
            run_ffmpeg(uploaded_file_path, f'-ac 2 -f wav - | lame --tc "Encoded using freeaudioconverter.net" -Y '
            f'-V {mp3_vbr_setting} - {output_path}.mp3')

# AAC
def run_aac(uploaded_file_path, is_keep_video, fdk_type, fdk_cbr, fdk_vbr, is_fdk_lowpass, fdk_lowpass, output_path):

    if is_keep_video == "yes":

        just_ext = uploaded_file_path.split('.')[-1]
        if just_ext == 'mp4':
            output_ext = 'mp4'
        else:
            output_ext = 'mkv'

        if fdk_type == "fdk_cbr":
            if is_fdk_lowpass == "yes":
                run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:s copy -c:v copy -c:a libfdk_aac '
                f'-cutoff {fdk_lowpass} -b:a {fdk_cbr}k {output_path}.{output_ext}')
            else:
                run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:s copy -c:v copy -c:a libfdk_aac '
                f'-b:a {fdk_cbr}k {output_path}.{output_ext}')
        else: # VBR
            if is_fdk_lowpass == "yes":
                run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:s copy -c:v copy -c:a libfdk_aac '
                f'-cutoff {fdk_lowpass} -vbr {fdk_vbr} {output_path}.{output_ext}')
            else:
                run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:s copy -c:v copy -c:a libfdk_aac '
                f'-vbr {fdk_vbr} {output_path}.{output_ext}')

        return output_ext
        
    else: # Keep video not selected, use standalone fdkaac encoder.

        if fdk_type == "fdk_cbr":
            if is_fdk_lowpass == "yes":
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" '
                f'--bandwidth {fdk_lowpass} -b {fdk_cbr} - -o {output_path}.m4a')
            else:
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" -b {fdk_cbr} '
                f'- -o {output_path}.m4a')
        else: # VBR
            if is_fdk_lowpass == "yes":
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" '
                f'--bandwidth {fdk_lowpass} --bitrate-mode {fdk_vbr} - -o {output_path}.m4a')
            else:
                ffmpeg_pipe(uploaded_file_path, f'fdkaac --comment "Encoded using freeaudioconverter.net" '
                f'--bitrate-mode {fdk_vbr} - -o {output_path}.m4a')

# WAV
def run_wav(uploaded_file_path, is_keep_video, wav_bit_depth, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:s copy -c:v copy -c:a pcm_s{wav_bit_depth}le '
        f'{output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-map 0:a? -c:a pcm_s{wav_bit_depth}le {output_path}.wav')

# MP4
def run_mp4(uploaded_file_path, mp4_encoding_mode, crf_value, output_path):
    if mp4_encoding_mode == "keep_codecs":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -c:v copy -c:a copy -f mp4 -movflags faststart '
        f'{output_path}.mp4')
    elif mp4_encoding_mode == "keep_video_codec":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -c:v copy -c:a libfdk_aac -vbr 5 -f mp4 '
        f'-movflags faststart {output_path}.mp4')
    elif mp4_encoding_mode == 'convert_video_keep_audio':
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -c:v libx264 -crf {crf_value} -c:a copy -f mp4 '
        f'-movflags faststart {output_path}.mp4')
    else:
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -c:v libx264 -preset {mp4_encoding_mode} -crf {crf_value} '
        f'-c:a libfdk_aac -vbr 5 -f mp4 -movflags faststart {output_path}.mp4')

# Opus
def run_opus(uploaded_file_path, opus_encoding_type, opus_vorbis_slider, opus_cbr_bitrate, output_path):
    if opus_encoding_type == "opus_vbr":
        ffmpeg_pipe(uploaded_file_path, f'opusenc --comment Comment="Encoded using freeaudioconverter.net" '
        f'--bitrate {opus_vorbis_slider} - {output_path}.opus')
    else: # CBR
        ffmpeg_pipe(uploaded_file_path, f'opusenc --comment Comment="Encoded using freeaudioconverter.net" --hard-cbr '
        f'--bitrate {opus_cbr_bitrate} - {output_path}.opus')

# Vorbis
def run_vorbis(uploaded_file_path, vorbis_encoding, vorbis_quality, opus_vorbis_slider, output_path):
    if vorbis_encoding == "vbr_bitrate": # VBR with nominal bitrate
        ffmpeg_pipe(uploaded_file_path, f'oggenc -c "Comment=Encoded using freeaudioconverter.net" '
        f'-b {opus_vorbis_slider} - -o {output_path}.ogg')
    elif vorbis_encoding == "vbr_quality": # True VBR
        ffmpeg_pipe(uploaded_file_path, f'oggenc -c "Comment=Encoded using freeaudioconverter.net" -q {vorbis_quality} '
        f'- -o {output_path}.ogg')

# FLAC
def run_flac(uploaded_file_path, is_keep_video, flac_compression, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:v copy -c:s copy -c:v copy -c:a flac '
        f'{output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-map 0:a -c:a flac {output_path}.flac')

# ALAC
def run_alac(uploaded_file_path, is_keep_video, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:v copy -c:s copy -c:a alac {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-map 0:a -c:a alac {output_path}.m4a')

# AC3
def run_ac3(uploaded_file_path, is_keep_video, ac3_bitrate, output_path):
    just_ext = uploaded_file_path.split('.')[-1]
    if just_ext == 'mp4':
        output_ext = 'mp4'
    else:
        output_ext = 'mkv'

    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:v copy -c:s copy -c:a ac3 -b:a {ac3_bitrate}k'
        f' {output_path}.{output_ext}')
    else:
        run_ffmpeg(uploaded_file_path, f'-map 0:a -c:a ac3 -b:a {ac3_bitrate}k {output_path}.ac3')

# DTS
def run_dts(uploaded_file_path, is_keep_video, dts_bitrate, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c:v copy -c:s copy -c:a dca -b:a {dts_bitrate}k'
        f' -strict -2 {output_path}.mkv')
    else:
        run_ffmpeg(uploaded_file_path, f'-map 0:a -c:a dca -b:a {dts_bitrate}k -strict -2 {output_path}.dts')

# CAF
def run_caf(uploaded_file_path, output_path):
    run_ffmpeg(uploaded_file_path, f'-map 0:a -c:a alac {output_path}.caf')

# MKA
def run_mka(uploaded_file_path, output_path):
    run_ffmpeg(uploaded_file_path, f'-map 0:a -c:a copy {output_path}.mka')

# MKV
def run_mkv(uploaded_file_path, output_path):
    run_ffmpeg(uploaded_file_path, f'-map 0:V? -map 0:a? -map 0:s? -c copy -f matroska {output_path}.mkv')