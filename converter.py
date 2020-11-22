import os
import subprocess
from time import time

from loggers import log

os.makedirs('ffmpeg-progress', exist_ok=True)
os.makedirs('ffmpeg_output', exist_ok=True)
# If you want to run this web app locally, change this (if necessary) to the path of your FFmpeg executable.
ffmpeg_path = '/home/h/bin/ffmpeg'


def run_ffmpeg(progress_filename, uploaded_file_path, params, output_name):
    progress_file_path = os.path.join('ffmpeg-progress', progress_filename)
    log.info(f'Conversion progress will be saved to: {progress_file_path}')
    # Turn params into a list as I want to use subprocess.run() with an array of arguments.
    params = params.split(' ')
    params.append(output_name)
    log.info(params)
    log.info(f'Converting {uploaded_file_path}...')
    start_time = time()
    filename_without_ext = os.path.splitext(output_name)[0][12:]
    ffmpeg_output_file = f'ffmpeg_output/{filename_without_ext}.txt'
    open(ffmpeg_output_file, 'w').close()

    process = subprocess.run([ffmpeg_path, '-hide_banner', '-progress', progress_file_path, '-y', '-i', uploaded_file_path,
                        '-metadata', 'comment=Transcoded using free-av-tools.com', '-metadata',
                        'encoded_by=free-av-tools.com', '-id3v2_version', '3', '-write_id3v1', 'true'] + params,
                        stderr=subprocess.PIPE)

    with open(ffmpeg_output_file, 'w') as f:
        f.write(process.stderr.decode('utf-8'))
        
    if process.returncode != 0:
        return {
            'error': process.stderr.decode('utf-8'),
            'log_file': ffmpeg_output_file
        }
    else:
        end_time = time()
        time_taken = round((end_time - start_time), 2)
        log.info(f'Conversion took {time_taken} seconds.')
        return {
            'error': None,
            'ext': os.path.splitext(output_name)[1],
            'download_path': output_name,
            'log_file': ffmpeg_output_file
        }


# AAC
def aac(progress_filename, uploaded_file_path, is_keep_video, fdk_type, fdk_cbr, fdk_vbr, is_fdk_lowpass,
        fdk_lowpass, output_path):
    # Keep the video (if applicable)
    if is_keep_video == "yes":
        ext = os.path.splitext(uploaded_file_path)[-1]
        output_ext = 'mp4' if ext == '.mp4' else '.mkv'
        # CBR
        if fdk_type == "fdk_cbr":
            if is_fdk_lowpass == "yes":
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} '
                           f'-b:a {fdk_cbr}k -c:s copy', f'{output_path}.{output_ext}')
            else:
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -b:a {fdk_cbr}k '
                           f'-c:s copy', f'{output_path}.{output_ext}')
        # VBR
        else:
            if is_fdk_lowpass == "yes":
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} '
                           f'-vbr {fdk_vbr} -c:s copy', f'{output_path}.{output_ext}')
            else:
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr {fdk_vbr} '
                           f'-c:s copy', f'{output_path}.{output_ext}')

    # Audio-only output file,outpt
    else:
        output_ext = 'm4a'
        # CBR
        if fdk_type == "fdk_cbr":
            if is_fdk_lowpass == "yes":
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} '
                           f'-b:a {fdk_cbr}k', f'{output_path}.m4a')
            else:
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -b:a {fdk_cbr}k',
                           f'{output_path}.m4a')
        # VBR
        else:
            if is_fdk_lowpass == "yes":
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -cutoff {fdk_lowpass} '
                           f'-vbr {fdk_vbr}', f'{output_path}.m4a')
            else:
                return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr {fdk_vbr}',
                           f'{output_path}.m4a')


# AC3
def ac3(progress_filename, uploaded_file_path, is_keep_video, ac3_bitrate, output_path):
    # Keep video (if applicable)
    if is_keep_video == "yes":
        ext = os.path.splitext(uploaded_file_path)[-1]
        output_ext = 'mp4' if ext == '.mp4' else 'mkv'
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a ac3 -b:a {ac3_bitrate}k -c:s copy',
                   f'{output_path}.{output_ext}')
    # Audio-only output file
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a ac3 -b:a {ac3_bitrate}k', f'{output_path}.ac3')


# ALAC
def alac(progress_filename, uploaded_file_path, is_keep_video, output_path):
    # Keep video (if applicable)
    if is_keep_video == "yes":
        return run_ffmpeg(progress_filename, uploaded_file_path, '-c:v copy -c:a alac -c:s copy', f'{output_path}.mkv')
    # Audio-only output file
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, '-c:a alac', f'{output_path}.m4a')


# CAF
def caf(progress_filename, uploaded_file_path, output_path):
    return run_ffmpeg(progress_filename, uploaded_file_path, '-c:a alac', f'{output_path}.caf')


# DTS
def dts(progress_filename, uploaded_file_path, is_keep_video, dts_bitrate, output_path):
    # Keep video (if applicable)
    if is_keep_video == "yes":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a dca -b:a {dts_bitrate}k '
                   f'-c:s copy -strict -2', f'{output_path}.mkv')
    # Audio-only output file
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a dca -b:a {dts_bitrate}k -strict -2',
                   f'{output_path}.dts')


# FLAC
def flac(progress_filename, uploaded_file_path, is_keep_video, flac_compression, output_path):
    # Keep video (if applicable)
    if is_keep_video == "yes":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a flac -compression_level {flac_compression} '
                   f'-c:s copy', f'{output_path}.mkv')
    # Audio-only output file
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a flac -compression_level {flac_compression}',
                   f'{output_path}.flac')


# MKA
def mka(progress_filename, uploaded_file_path, output_path):
    return run_ffmpeg(progress_filename, uploaded_file_path, '-c:v copy -c:a copy', f'{output_path}.mka')


# MKV
def mkv(progress_filename, uploaded_file_path, video_mode, crf_value, output_path):
    # No transcoding, simply change the container to MKV.
    if video_mode == "keep_codecs":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-map 0 -c copy', f'{output_path}.mkv')
    # Keep the video as-is, encode the audio.
    elif video_mode == "keep_video_codec":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-map 0 -c:v copy -c:a libfdk_aac -c:s copy -vbr 5',
                   f'{output_path}.mkv')
    # Transcode the video, leave the audio as-is.
    elif video_mode == 'convert_video_keep_audio':
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-map 0 -c:v libx264 -crf {crf_value} -c:a copy -c:s copy',
                   f'{output_path}.mkv')
    # Transcode the video and audio.
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-map 0 -c:v libx264 -preset {video_mode} '
                   f'-crf {crf_value} -c:a libfdk_aac', f'{output_path}.mkv')


# MP3
def mp3(progress_filename, uploaded_file_path, is_keep_video, mp3_encoding_type, mp3_bitrate, mp3_vbr_setting,
        output_path):
    # Keep the video (if applicable)
    if is_keep_video == "yes":
        ext = os.path.splitext(uploaded_file_path)[-1]
        output_ext = 'mp4' if ext == '.mp4' else 'mkv'
        # CBR
        if mp3_encoding_type == "cbr":
            return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libmp3lame -b:a {mp3_bitrate}k',
                       f'{output_path}.{output_ext}')
        # ABR
        elif mp3_encoding_type == "abr":
            return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libmp3lame --abr 1 -b:a {mp3_bitrate}k',
                       f'{output_path}.{output_ext}')
        # VBR
        elif mp3_encoding_type == "vbr":
            return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libmp3lame -q:a {mp3_vbr_setting}',
                       f'{output_path}.{output_ext}')
    # Audio-only output file
    else:
        output_ext = 'mp3'
        if mp3_encoding_type == "cbr":
            return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libmp3lame -b:a {mp3_bitrate}k',
                       f'{output_path}.mp3')
        elif mp3_encoding_type == "abr":
            return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libmp3lame --abr 1 -b:a {mp3_bitrate}k',
                       f'{output_path}.mp3')
        elif mp3_encoding_type == "vbr":
            return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libmp3lame -q:a {mp3_vbr_setting}',
                       f'{output_path}.mp3')


# MP4
def mp4(progress_filename, uploaded_file_path, video_mode, crf_value, output_path):
    # No transcoding, simply change the container to MP4.
    if video_mode == "keep_codecs":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c copy -f mp4 -movflags faststart', f'{output_path}.mp4')
    # Keep the video as-is, encode the audio.
    elif video_mode == "keep_video_codec":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libfdk_aac -vbr 5 -f mp4 '
                   f'-movflags faststart', f'{output_path}.mp4')
    # Transcode the video, keep the audio as-is.
    elif video_mode == 'convert_video_keep_audio':
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v libx264 -crf {crf_value} -c:a copy -f mp4 '
                   f'-movflags faststart', f'{output_path}.mp4')
    # Transcode the video and audio.
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v libx264 -preset {video_mode} -crf {crf_value} '
                   f'-c:a libfdk_aac -vbr 5 -f mp4 -movflags faststart', f'{output_path}.mp4')


# Opus
def opus(progress_filename, uploaded_file_path, opus_encoding_type, opus_vorbis_slider, opus_cbr_bitrate,
         output_path):
    # VBR
    if opus_encoding_type == "opus_vbr":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libopus -b:a {opus_vorbis_slider}k',
                   f'{output_path}.opus')
    # CBR
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a libopus -vbr off -b:a {opus_cbr_bitrate}k',
                   f'{output_path}.opus')


# Vorbis
def vorbis(progress_filename, uploaded_file_path, vorbis_encoding, vorbis_quality, opus_vorbis_slider, output_path):
    # ABR
    if vorbis_encoding == "abr":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libvorbis -b:a {opus_vorbis_slider}k',
                   f'{output_path}.ogg')
    # True VBR
    elif vorbis_encoding == "vbr":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a libvorbis -q:a {vorbis_quality}', f'{output_path}.ogg')


# WAV
def wav(progress_filename, uploaded_file_path, is_keep_video, wav_bit_depth, output_path):
    # Keep the video (if applicable)
    if is_keep_video == "yes":
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:v copy -c:a pcm_s{wav_bit_depth}le -c:s copy',
                   f'{output_path}.mkv')
    # Audio-only output file
    else:
        return run_ffmpeg(progress_filename, uploaded_file_path, f'-c:a pcm_s{wav_bit_depth}le', f'{output_path}.wav')