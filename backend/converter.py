import os
from pathlib import Path
import shutil
import subprocess
from time import time

from ffmpeg import probe

from loggers import log
from utils import delete_file, empty_folder, is_mono_audio

os.makedirs("ffmpeg-progress", exist_ok=True)
os.makedirs("ffmpeg-output", exist_ok=True)
# If you want to run this web app locally, change this (if necessary) to the path of your FFmpeg executable.
ffmpeg_path = "/home/h/bin/ffmpeg"

if "libfdk-aac" in subprocess.check_output([ffmpeg_path, "-hide_banner", "-buildconf"]).decode(
    "utf-8"
):
    aac_encoder = "libfdk_aac"
    aac_vbr_enabler = "-vbr"
# FFmpeg was not compiled with libfdk-aac support, use the native AAC encoder.
else:
    aac_encoder = "aac"
    aac_vbr_enabler = "-q:a"


def run_ffmpeg(progress_filename, uploaded_file_path, params, output_name):
    progress_file_path = os.path.join("ffmpeg-progress", progress_filename)
    ffmpeg_output_file = os.path.join("ffmpeg-output", f"{Path(uploaded_file_path).stem}.txt")
    with open(ffmpeg_output_file, "w"):
        pass

    params = params.split(" ")
    log.info(params)
    params.append(output_name)
    ffmpeg_start_time = time()

    with open(ffmpeg_output_file, "a") as f:
        process = subprocess.Popen(
            [
                ffmpeg_path,
                "-hide_banner",
                "-loglevel",
                "verbose",
                "-progress",
                "-",
                "-nostats",
                "-y",
                "-i",
                uploaded_file_path,
                "-metadata",
                "comment=Transcoded using av-converter.com",
                "-metadata",
                "encoded_by=av-converter.com",
                "-id3v2_version",
                "3",
                "-write_id3v1",
                "true",
            ]
            + params,
            stdout=subprocess.PIPE,
            stderr=f,
        )

    try:
        file_duration = float(probe(uploaded_file_path)["format"]["duration"])
    except Exception as e:
        can_get_duration = False
        log.info(f"Unable to get the duration of {uploaded_file_path}:\n{e}")
    else:
        can_get_duration = True
        log.info(f"File Duration: {file_duration}")

    if can_get_duration:
        percentage = "unknown"
        speed = "unknown"
        eta_string = "unknown"

        while process.poll() is None:
            try:
                output = process.stdout.readline().decode().strip()
            except Exception as e:
                log.info(f"Unable to decode the FFmpeg output:\n{e}\nFFmpeg Output:\n{output}")
            else:
                if "out_time_ms" in output:
                    seconds_processed = int(output[12:]) / 1_000_000
                    try:
                        percentage = (seconds_processed / file_duration) * 100
                    except Exception as e:
                        log.info(f"Unable to calculate percentage progress:\n{e}\n")
                        log.info(f"Seconds Processed: {seconds_processed}\n")
                    else:
                        percentage = round(percentage, 1)

                elif "speed" in output:
                    speed = float(output[6:][:-1])
                    try:
                        eta = (file_duration - seconds_processed) / speed
                    except Exception as e:
                        log.info(f"Unable to calculate ETA:\n{e}\nSpeed:\n{speed}")
                    else:
                        minutes = int(eta / 60)
                        seconds = round(eta % 60)
                        eta_string = f"{minutes}m {seconds}s"

            with open(progress_file_path, "w") as f:
                f.write(f"Progress: {percentage}% | Speed: {speed}x | ETA: {eta_string}")

    # Empty the uploads folder if there is less than 500 MB free storage space.
    free_space_mb = shutil.disk_usage("/")[2] / 1_000_000
    if free_space_mb < 500:
        log.info(f"{free_space_mb} MB storage space remaining. Emptying the uploads folder...")
        empty_folder("uploads")

    # The return code is not 0 if an error occurred.
    if process.returncode != 0:
        log.info("Unable to convert.")
        return {
            "error": "Unable to convert",
            "log_file": f"api/{ffmpeg_output_file}",
        }

    log.info(f"Conversion took {round((time() - ffmpeg_start_time), 1)} seconds.")
    delete_file(uploaded_file_path)
    delete_file(progress_file_path)

    return {
        "error": None,
        "ext": os.path.splitext(output_name)[1],
        "download_path": f"api/{output_name}",
        "log_file": f"api/{ffmpeg_output_file}",
    }


# AAC
def aac(
    progress_filename,
    uploaded_file_path,
    output_path,
    is_keep_video,
    encoding_type,
    bitrate,
    vbr_quality,
):
    if is_keep_video == "yes":
        output_ext = Path(uploaded_file_path).suffix

        if encoding_type == "cbr":
            return run_ffmpeg(
                progress_filename,
                uploaded_file_path,
                f"-c:v copy -c:a {aac_encoder} -b:a {bitrate}k",
                f"{output_path}.{output_ext}",
            )
        # VBR was selected.
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:v copy -c:a {aac_encoder} {aac_vbr_enabler} {vbr_quality}",
            f"{output_path}.{output_ext}",
        )

    # Keep video was not selected:

    if encoding_type == "cbr":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-map 0:a -c:a {aac_encoder} -b:a {bitrate}k",
            f"{output_path}.m4a",
        )
    # VBR was selected.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-map 0:a -c:a {aac_encoder} {aac_vbr_enabler} {vbr_quality}",
        f"{output_path}.m4a",
    )


# AC3
def ac3(progress_filename, uploaded_file_path, output_path, is_keep_video, ac3_bitrate):
    if is_keep_video == "yes":
        output_ext = Path(uploaded_file_path).suffix
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:v copy -c:a ac3 -b:a {ac3_bitrate}k",
            f"{output_path}.{output_ext}",
        )
    # Audio only output file.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-c:a ac3 -b:a {ac3_bitrate}k",
        f"{output_path}.ac3",
    )


# ALAC
def alac(progress_filename, uploaded_file_path, output_path, is_keep_video):
    if is_keep_video == "yes":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            "-c:v copy -c:a alac",
            f"{output_path}.mkv",
        )
    # Audio only output file.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        "-map 0:a -c:a alac",
        f"{output_path}.m4a",
    )


# CAF
def caf(progress_filename, uploaded_file_path, output_path):
    return run_ffmpeg(progress_filename, uploaded_file_path, "-c:a alac", f"{output_path}.caf")


# DTS
def dts(progress_filename, uploaded_file_path, output_path, is_keep_video, dts_bitrate):
    if is_keep_video == "yes":
        output_ext = Path(uploaded_file_path).suffix
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:v copy -c:a dca -b:a {dts_bitrate}k " f"-strict -2",
            f"{output_path}.{output_ext}",
        )
    # Audio only output file.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-c:a dca -b:a {dts_bitrate}k -strict -2",
        f"{output_path}.dts",
    )


# FLAC
def flac(progress_filename, uploaded_file_path, output_path, is_keep_video, flac_compression):
    if is_keep_video == "yes":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-map 0 -c:v copy -c:s copy -c:a flac " f"-compression_level {flac_compression}",
            f"{output_path}.mkv",
        )
    # Audio only output file.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-c:a flac -compression_level {flac_compression}",
        f"{output_path}.flac",
    )


# MKA
def mka(progress_filename, uploaded_file_path, output_path):
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        "-map 0:a -c:a copy",
        f"{output_path}.mka",
    )


# MKV
def mkv(progress_filename, uploaded_file_path, output_path, video_mode, crf_value):
    # No transcoding, simply change the container to MKV.
    if video_mode == "keep_codecs":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-map 0 -c copy",
            f"{output_path}.mkv",
        )
    # Keep the video as-is, encode the audio.
    elif video_mode == "keep_video_codec":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-map 0 -c:v copy -c:s copy -c:a {aac_encoder} {aac_vbr_enabler} 5",
            f"{output_path}.mkv",
        )
    # Transcode the video, leave the audio as-is.
    elif video_mode == "convert_video_keep_audio":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-map 0 -c:v libx264 -crf {crf_value} -c:a copy " "-c:s copy",
            f"{output_path}.mkv",
        )
    # Transcode the video and audio.
    else:
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-map 0 -c:v libx264 -preset {video_mode} "
            f"-crf {crf_value} -c:a {aac_encoder}  copy",
            f"{output_path}.mkv",
        )


# MP3
def mp3(
    progress_filename,
    uploaded_file_path,
    output_path,
    is_keep_video,
    encoding_type,
    bitrate,
    vbr_setting,
):
    if is_keep_video == "yes":
        output_ext = "mkv" if Path(uploaded_file_path).suffix != "mp4" else "mp4"

        if encoding_type == "cbr":
            return run_ffmpeg(
                progress_filename,
                uploaded_file_path,
                "-c:v copy -c:a libmp3lame -b:a {bitrate}k",
                f"{output_path}.{output_ext}",
            )
        elif encoding_type == "abr":
            return run_ffmpeg(
                progress_filename,
                uploaded_file_path,
                f"-c:v copy -c:a libmp3lame --abr 1 -b:a {bitrate}k",
                f"{output_path}.{output_ext}",
            )
        # VBR was selected.
        else:
            return run_ffmpeg(
                progress_filename,
                uploaded_file_path,
                "-c:v copy -c:a libmp3lame " f"-q:a {vbr_setting}",
                f"{output_path}.{output_ext}",
            )

    # Keep the video was not selected - audio only output file:

    if encoding_type == "cbr":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:a libmp3lame -b:a {bitrate}k",
            f"{output_path}.mp3",
        )
    elif encoding_type == "abr":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:a libmp3lame --abr 1 -b:a {bitrate}k",
            f"{output_path}.mp3",
        )
    # VBR was selected.
    else:
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:a libmp3lame -q:a {vbr_setting}",
            f"{output_path}.mp3",
        )


# MP4
def mp4(progress_filename, uploaded_file_path, output_path, video_mode, crf_value):
    constant_options = "-map 0:V? -map 0:a? -map 0:s? -movflags faststart"
    # No transcoding, simply change the container to MP4.
    if video_mode == "keep_codecs":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"{constant_options} -c copy",
            f"{output_path}.mp4",
        )
    # Keep the video as-is, encode the audio.
    elif video_mode == "keep_video_codec":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"{constant_options} -c:V copy -c:a {aac_encoder} {aac_vbr_enabler} 5",
            f"{output_path}.mp4",
        )
    # Transcode the video, keep the audio as-is.
    elif video_mode == "convert_video_keep_audio":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"{constant_options} -c:V libx264 -crf {crf_value} " "-c:a copy",
            f"{output_path}.mp4",
        )
    # Transcode the video and audio.
    else:
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"{constant_options} -c:V libx264 -preset {video_mode}"
            f" -crf {crf_value} -c:a {aac_encoder} {aac_vbr_enabler} 5",
            f"{output_path}.mp4",
        )


# Opus
def opus(
    progress_filename,
    uploaded_file_path,
    output_path,
    encoding_type,
    vbr_bitrate,
    cbr_bitrate,
):
    # Opus does not support >256 kbps per channel.
    if is_mono_audio(uploaded_file_path):
        if int(vbr_bitrate) > 256:
            vbr_bitrate = 256
        elif int(cbr_bitrate) > 256:
            cbr_bitrate = 256

    if encoding_type == "opus_vbr":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:a libopus -b:a {vbr_bitrate}k",
            f"{output_path}.opus",
        )
    # CBR
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-c:a libopus -vbr off -b:a {cbr_bitrate}k",
        f"{output_path}.opus",
    )


# Vorbis
def vorbis(
    progress_filename,
    uploaded_file_path,
    output_path,
    encoding_type,
    quality_level,
    bitrate,
):
    if encoding_type == "abr":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:a libvorbis -b:a {bitrate}k",
            f"{output_path}.ogg",
        )
    # Constant quality mode.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-c:a libvorbis -q:a {quality_level}",
        f"{output_path}.ogg",
    )


# WAV
def wav(progress_filename, uploaded_file_path, output_path, is_keep_video, wav_bit_depth):
    if is_keep_video == "yes":
        return run_ffmpeg(
            progress_filename,
            uploaded_file_path,
            f"-c:v copy -c:a pcm_s{wav_bit_depth}le",
            f"{output_path}.mkv",
        )
    # Audio only output file.
    return run_ffmpeg(
        progress_filename,
        uploaded_file_path,
        f"-c:a pcm_s{wav_bit_depth}le",
        f"{output_path}.wav",
    )
