import os
from pathlib import Path
import subprocess
from time import time

from ffmpeg import probe

from flask_app.utils import delete_file, get_file_duration, is_mono_audio
from logger import log

aac_encoder = "libfdk_aac"
aac_vbr_enabler = "-vbr"


def get_ffmpeg_args(chosen_codec, output_name, is_keep_video, data, slider_value):
    # AAC
    if chosen_codec == "AAC":
        return aac(
            output_name,
            data["aacExtension"],
            is_keep_video,
            data["aacEncodingType"],
            slider_value,
            data["aacVbrMode"],
        )
    # AC3
    elif chosen_codec == "AC3":
        return ac3(output_name, is_keep_video, data["ac3Bitrate"])
    # ALAC
    elif chosen_codec == "ALAC":
        return alac(output_name, is_keep_video)
    # CAF
    elif chosen_codec == "CAF":
        return caf(output_name)
    # DTS
    elif chosen_codec == "DTS":
        return dts(output_name, is_keep_video, data["dtsBitrate"])
    # FLAC
    elif chosen_codec == "FLAC":
        return flac(output_name, is_keep_video, data["flacCompression"])
    # MKA
    elif chosen_codec == "MKA":
        return mka(output_name)
    # MP3
    elif chosen_codec == "MP3":
        return mp3(
            output_name,
            is_keep_video,
            data["mp3EncodingType"],
            slider_value,
            data["mp3VbrSetting"],
        )
    # H.264/AVC
    elif chosen_codec == "H264":
        return h264(output_name, data)
    # Opus
    elif chosen_codec == "Opus":
        return opus(output_name, data["opusEncodingType"], slider_value)
    # Vorbis
    elif chosen_codec == "Vorbis":
        return vorbis(output_name, data["vorbisEncodingType"], data["qValue"], slider_value)
    # WAV
    elif chosen_codec == "WAV":
        return wav(output_name, is_keep_video, data["wavBitDepth"])


def send_args_to_ffmpeg_wasm(encoding_args, output_filename):
    encoding_args = encoding_args.split(" ")
    log.info(encoding_args)
    # Mutual arguments.
    ffmpeg_args = [
        "-metadata",
        "encoded_by=av-converter.com",
        "-id3v2_version",
        "3",
        "-write_id3v1",
        "true",
    ] + encoding_args

    return {
        "args": " ".join(ffmpeg_args),
        "output_filename": output_filename
    }


# AAC
def aac(output_name, extension, is_keep_video, encoding_type, bitrate, vbr_quality):
    mutual_args = f"-map 0:a -c:a {aac_encoder}"

    if is_keep_video == "yes":
        mutual_args += " -map 0:V -c:V copy"
        output_ext = Path(input_filename).suffix

        if encoding_type == "cbr":
            return send_args_to_ffmpeg_wasm(
                f"{mutual_args} -b:a {bitrate}k", f"{output_name}.{output_ext}",
            )
        # VBR was selected.
        return send_args_to_ffmpeg_wasm(
            f"{mutual_args} {aac_vbr_enabler} {vbr_quality}", f"{output_name}.{output_ext}",
        )

    # Keep video was not selected:

    if encoding_type == "cbr":
        return send_args_to_ffmpeg_wasm(f"{mutual_args} -b:a {bitrate}k", f"{output_name}.{extension}")
    # VBR was selected.
    return send_args_to_ffmpeg_wasm(
        f"{mutual_args} {aac_vbr_enabler} {vbr_quality}", f"{output_name}.{extension}"
    )


# AC3
def ac3(output_name, is_keep_video, ac3_bitrate):
    if is_keep_video == "yes":
        output_ext = Path(input_filename).suffix
        return send_args_to_ffmpeg_wasm(
            f"-c:v copy -c:a ac3 -b:a {ac3_bitrate}k", f"{output_name}.{output_ext}"
        )
    # Audio only output file.
    return send_args_to_ffmpeg_wasm(f"-c:a ac3 -b:a {ac3_bitrate}k", f"{output_name}.ac3")


# ALAC
def alac(output_name, is_keep_video):
    if is_keep_video == "yes":
        return send_args_to_ffmpeg_wasm(f"-c:v copy -c:a alac", f"{output_name}.mkv")
    # Audio only output file.
    return send_args_to_ffmpeg_wasm(f"-map 0:a -c:a alac", f"{output_name}.m4a")


# CAF
def caf(output_name):
    return send_args_to_ffmpeg_wasm(f"-c:a alac", f"{output_name}.caf")


# DTS
def dts(output_name, is_keep_video, dts_bitrate):
    if is_keep_video == "yes":
        output_ext = Path(input_filename).suffix
        return send_args_to_ffmpeg_wasm(
            f"-c:v copy -c:a dca -b:a {dts_bitrate}k -strict -2", f"{output_name}.{output_ext}"
        )
    # Audio only output file.
    return send_args_to_ffmpeg_wasm(f"-c:a dca -b:a {dts_bitrate}k -strict -2", f"{output_name}.dts")


# FLAC
def flac(output_name, is_keep_video, flac_compression):
    if is_keep_video == "yes":
        return send_args_to_ffmpeg_wasm(
            f"-map 0 -c:v copy -c:s copy -c:a flac -compression_level {flac_compression}", f"{output_name}.mkv"
        )
    # Audio only output file.
    return send_args_to_ffmpeg_wasm(
        f"-c:a flac -compression_level {flac_compression}", f"{output_name}.flac"
    )


# H264
def h264(output_name, data):
    output_filename = f"{output_name}.{data['videoContainer']}"
    ffmpeg_args = "-map 0:V? -map 0:a? -map 0:s?"

    if data["videoContainer"] == "mp4":
        ffmpeg_args += " -c:s mov_text -movflags faststart"

    # If the "Transcode the audio to AAC" checkbox is checked.
    if data["transcodeVideosAudio"]:
        ffmpeg_args += " -c:a libfdk_aac -vbr 5"
    else:
        ffmpeg_args += " -c:a copy"

    # Do not transcode the video.
    if data["transcodeVideo"] == "no":
        # MP4
        if data["videoContainer"] == "mp4":
            ffmpeg_args += f" -c:V copy -f mp4"
            return send_args_to_ffmpeg_wasm(ffmpeg_args, output_filename)
        # MKV
        ffmpeg_args += f" -c:V copy -c:s copy -f matroska"
        return send_args_to_ffmpeg_wasm(ffmpeg_args, output_filename)

    # Transcode to H.264/AVC.
    else:
        ffmpeg_args += f" -c:V libx264 -x264-params threads={data['numLogicalProcessors']} -preset {data['x264Preset']}"
        # CRF mode.
        if data["videoEncodingType"] == "crf":
            ffmpeg_args += f" -crf {data['crfValue']}"
            return send_args_to_ffmpeg_wasm(ffmpeg_args, output_filename)
        # Target a bitrate.
        elif data["videoEncodingType"] == "bitrate":
            #bufsize = str((float(data['videoBitrate']) * 2)) + "M"
            bitrate = data['videoBitrate'] + "M"
            ffmpeg_args += f" -b:v {bitrate}"
            return send_args_to_ffmpeg_wasm(ffmpeg_args, output_filename)


# MKA
def mka(output_name):
    return send_args_to_ffmpeg_wasm(f"-map 0:a -c:a copy", f"{output_name}.mka")


# MP3
def mp3(output_name, is_keep_video, encoding_type, bitrate, vbr_setting):
    if is_keep_video == "yes":
        output_ext = "mkv" if Path(input_filename).suffix != "mp4" else "mp4"

        if encoding_type == "cbr":
            return send_args_to_ffmpeg_wasm(
                f"-c:v copy -c:a libmp3lame -b:a {bitrate}k", f"{output_name}.{output_ext}",
            )
        elif encoding_type == "abr":
            return send_args_to_ffmpeg_wasm(
                f"-c:v copy -c:a libmp3lame --abr 1 -b:a {bitrate}k", f"{output_name}.{output_ext}",
            )
        # VBR was selected.
        else:
            return send_args_to_ffmpeg_wasm(
                f"-c:v copy -c:a libmp3lame " f"-q:a {vbr_setting}", f"{output_name}.{output_ext}",
            )

    # Keep the video was not selected - audio only output file:

    if encoding_type == "cbr":
        return send_args_to_ffmpeg_wasm(f"-c:a libmp3lame -b:a {bitrate}k", f"{output_name}.mp3")
    # ABR
    elif encoding_type == "abr":
        return send_args_to_ffmpeg_wasm(
            f"-c:a libmp3lame --abr 1 -b:a {bitrate}k", f"{output_name}.mp3"
        )
    # VBR
    else:
        return send_args_to_ffmpeg_wasm(f"-c:a libmp3lame -q:a {vbr_setting}", f"{output_name}.mp3")


# Opus
def opus(output_name, encoding_type, bitrate):
    # Opus does not support >256 kbps per channel.
    if is_mono_audio(input_filename):
        bitrate = "256" if int(bitrate) > 256 else bitrate
    # VBR
    if encoding_type == "opus_vbr":
        return send_args_to_ffmpeg_wasm(f"-c:a libopus -b:a {bitrate}k", f"{output_name}.opus")
    # CBR
    return send_args_to_ffmpeg_wasm(f"-c:a libopus -vbr off -b:a {bitrate}k", f"{output_name}.opus")


# Vorbis
def vorbis(output_name, encoding_type, quality_level, bitrate):
    if encoding_type == "abr":
        return send_args_to_ffmpeg_wasm(f"-c:a libvorbis -b:a {bitrate}k", f"{output_name}.ogg")
    # Constant quality mode.
    return send_args_to_ffmpeg_wasm(f"-c:a libvorbis -q:a {quality_level}", f"{output_name}.ogg")


# WAV
def wav(output_name, is_keep_video, wav_bit_depth):
    if is_keep_video == "yes":
        return send_args_to_ffmpeg_wasm(f"-c:v copy -c:a pcm_s{wav_bit_depth}le", f"{output_name}.mkv")
    # Audio only output file.
    return send_args_to_ffmpeg_wasm(f"-c:a pcm_s{wav_bit_depth}le", f"{output_name}.wav")
