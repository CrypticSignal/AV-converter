from loggers import log
import os, shutil

# A function that checks if a variable contains a disallowed substring.
def does_variable_contain_bad_string(variable, disallowed_strings):
    for string in disallowed_strings:
        if string in variable:
            return True
    # If we've gotten to this point, the loop has finished without the if-statement ever being True, 
    # so the variable didn't contain a disallowed string.
    return False

# If a variable in the list contains a disallowed string, return True. Otherwise, return False.
def is_bad_string_in_variables(variables_list, disallowed_strings):
    for variable in variables_list:
        if does_variable_contain_bad_string(variable, disallowed_strings):
            return True
    return False
    
def run_ffmpeg(progress_filename, uploaded_file_path, params):
    progress_file_path = f'static/progress/"{progress_filename}".txt'
    log.info(params)
    os.system(f'ffmpeg -hide_banner -progress {progress_file_path} -y -i "{uploaded_file_path}" '
    f'-id3v2_version 3 -write_id3v1 true -metadata comment="freeaudioconverter.net" '
    f'-metadata encoded_by="freeaudioconverter.net" {params}')
    shutil.rmtree('static/progress')
    os.mkdir('static/progress')

# MP3
def run_mp3(progress_filename, uploaded_file_path, is_keep_video, mp3_encoding_type, mp3_bitrate, mp3_vbr_setting, output_path):
    if is_keep_video == "yes":

        just_ext = uploaded_file_path.split('.')[-1]
        if just_ext == 'mp4':
            output_ext = 'mp4'
        else:
            output_ext = 'mkv'

        if mp3_encoding_type == "cbr":
            run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libmp3lame -b:a {mp3_bitrate}k {output_path}.{output_ext}')
        elif mp3_encoding_type == "abr":
            run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libmp3lame --abr 1 -b:a {mp3_bitrate}k {output_path}.{output_ext}')
        elif mp3_encoding_type == "vbr": 
            run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libmp3lame -q:a {mp3_vbr_setting} {output_path}.{output_ext}')
    else:

        if mp3_encoding_type == "cbr":
            run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libmp3lame -b:a {mp3_bitrate}k {output_path}.mp3')
        elif mp3_encoding_type == "abr":
            run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libmp3lame --abr 1 -b:a {mp3_bitrate}k {output_path}.mp3')
        elif mp3_encoding_type == "vbr": 
            run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libmp3lame -q:a {mp3_vbr_setting} {output_path}.mp3')
      
# AAC
def run_aac(progress_filename, uploaded_file_path, is_keep_video, fdk_type, fdk_cbr, fdk_vbr, is_fdk_lowpass, fdk_lowpass, output_path):
    if is_keep_video == "yes":

        just_ext = uploaded_file_path.split('.')[-1]
        if just_ext == 'mp4':
            output_ext = 'mp4'
        else:
            output_ext = 'mkv'

        if fdk_type == "fdk_cbr":
            if is_fdk_lowpass == "yes":
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} -b:a {fdk_cbr}k '
                f'-c:s copy {output_path}.{output_ext}')
            else:
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -b:a {fdk_cbr}k '
                f'-c:s copy {output_path}.{output_ext}')
        else: # VBR
            if is_fdk_lowpass == "yes":
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} -vbr {fdk_vbr} '
                f'-c:s copy {output_path}.{output_ext}')
            else:
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr {fdk_vbr} '
                f'-c:s copy {output_path}.{output_ext}')
        
    else: # Keep video not selected.

        if fdk_type == "fdk_cbr":
            if is_fdk_lowpass == "yes":
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libfdk_aac -cutoff {fdk_lowpass} -b:a {fdk_cbr}k '
                f'{output_path}.m4a')
            else:
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libfdk_aac -b:a {fdk_cbr}k {output_path}.m4a')
        else: # VBR
            if is_fdk_lowpass == "yes":
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libfdk_aac -cutoff {fdk_lowpass} -vbr {fdk_vbr} '
                f'{output_path}.m4a')
            else:
                run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libfdk_aac -vbr {fdk_vbr} {output_path}.m4a')

# WAV
def run_wav(progress_filename, uploaded_file_path, is_keep_video, wav_bit_depth, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a pcm_s{wav_bit_depth}le -c:s copy {output_path}.mkv')
    else:
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a pcm_s{wav_bit_depth}le {output_path}.wav')

# MP4
def run_mp4(progress_filename, uploaded_file_path, mp4_encoding_mode, crf_value, output_path):
    if mp4_encoding_mode == "keep_codecs":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c copy -f mp4 -movflags faststart {output_path}.mp4')
    elif mp4_encoding_mode == "keep_video_codec":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr 5 -f mp4 -movflags faststart {output_path}.mp4')
    elif mp4_encoding_mode == 'convert_video_keep_audio':
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v libx264 -crf {crf_value} -c:a copy -f mp4 -movflags faststart '
        f'{output_path}.mp4')
    else: # Preset selected
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v libx264 -preset {mp4_encoding_mode} -crf {crf_value} '
        f'-c:a libfdk_aac -vbr 5 -f mp4 -movflags faststart {output_path}.mp4')
    
# Opus
def run_opus(progress_filename, uploaded_file_path, opus_encoding_type, opus_vorbis_slider, opus_cbr_bitrate, output_path):
    if opus_encoding_type == "opus_vbr":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libopus -b:a {opus_vorbis_slider}k {output_path}.opus')
    else: # CBR
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libopus -vbr off -b:a {opus_cbr_bitrate}k {output_path}.opus')

# Vorbis
def run_vorbis(progress_filename, uploaded_file_path, vorbis_encoding, vorbis_quality, opus_vorbis_slider, output_path):
    if vorbis_encoding == "abr": # ABR
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libvorbis -b:a {opus_vorbis_slider}k {output_path}.mka')
    elif vorbis_encoding == "vbr": # True VBR
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libvorbis -q:a {vorbis_quality} {output_path}.mka')

# FLAC
def run_flac(progress_filename, uploaded_file_path, is_keep_video, flac_compression, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a flac -compression_level {flac_compression} '
        f'-c:s copy {output_path}.mkv')
    else:
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a flac -compression_level {flac_compression} {output_path}.flac')

# ALAC
def run_alac(progress_filename, uploaded_file_path, is_keep_video, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a alac -c:s copy {output_path}.mkv')
    else:
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a alac {output_path}.m4a')

# AC3
def run_ac3(progress_filename, uploaded_file_path, is_keep_video, ac3_bitrate, output_path):
    just_ext = uploaded_file_path.split('.')[-1]
    if just_ext == 'mp4':
        output_ext = 'mp4'
    else:
        output_ext = 'mkv'
    if is_keep_video == "yes":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a ac3 -b:a {ac3_bitrate}k '
        f'-c:s copy {output_path}.{output_ext}')
    else:
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a ac3 -b:a {ac3_bitrate}k {output_path}.ac3')

# DTS
def run_dts(progress_filename, uploaded_file_path, is_keep_video, dts_bitrate, output_path):
    if is_keep_video == "yes":
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a dca -b:a {dts_bitrate}k '
        f'-c:s copy -strict -2 {output_path}.mkv')
    else:
        run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a dca -b:a {dts_bitrate}k -strict -2 {output_path}.dts')

# CAF
def run_caf(progress_filename, uploaded_file_path, output_path):
    run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a alac {output_path}.caf')

# MKA
def run_mka(progress_filename, uploaded_file_path, output_path):
    run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a copy {output_path}.mka')

# MKV
def run_mkv(progress_filename, uploaded_file_path, output_path):
    run_ffmpeg(progress_filename, uploaded_file_path, f'-c copy -f matroska {output_path}.mkv')