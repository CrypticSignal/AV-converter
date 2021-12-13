import os
from pathlib import Path
import subprocess
from time import time

from ffmpeg import probe

from flask_app.utils import delete_file, is_mono_audio
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
    # MKV
    elif chosen_codec == "MKV":
        return mkv(output_name, data["videoSetting"], data["crfValue"])
    # MP3
    elif chosen_codec == "MP3":
        return mp3(
            output_name,
            is_keep_video,
            data["mp3EncodingType"],
            slider_value,
            data["mp3VbrSetting"],
        )
    # MP4
    elif chosen_codec == "MP4":
        return mp4(output_name, data["videoSetting"], data["crfValue"])
    # Opus
    elif chosen_codec == "Opus":
        return opus(output_name, data["opusEncodingType"], slider_value)
    # Vorbis
    elif chosen_codec == "Vorbis":
        return vorbis(output_name, data["vorbisEncodingType"], data["qValue"], slider_value)
    # WAV
    elif chosen_codec == "WAV":
        return wav(output_name, is_keep_video, data["wavBitDepth"])


def return_args(encoding_args, output_name):
    encoding_args = encoding_args.split(" ")
    log.info(encoding_args)

    ffmpeg_args = [
        "-metadata",
        "encoded_by=av-converter.com",
        "-id3v2_version",
        "3",
        "-write_id3v1",
        "true",
    ] + encoding_args

    return {"ffmpeg_args": " ".join(ffmpeg_args), "output_name": output_name}


# AAC
def aac(
    output_name,
    extension,
    is_keep_video,
    encoding_type,
    bitrate,
    vbr_quality,
):
    if is_keep_video == "yes":
        output_ext = Path(input_filename).suffix

        if encoding_type == "cbr":
            return return_args(
                f"-c:v copy -c:a {aac_encoder} -b:a {bitrate}k",
                f"{output_name}.{output_ext}",
            )
        # VBR was selected.
        return return_args(
            f"-c:v copy -c:a {aac_encoder} {aac_vbr_enabler} {vbr_quality}",
            f"{output_name}.{output_ext}",
        )

    # Keep video was not selected:

    if encoding_type == "cbr":
        return return_args(
            f"-map 0:a -c:a {aac_encoder} -b:a {bitrate}k",
            f"{output_name}.{extension}",
        )
    # VBR was selected.
    return return_args(
        f"-map 0:a -c:a {aac_encoder} {aac_vbr_enabler} {vbr_quality}",
        f"{output_name}.{extension}",
    )


# AC3
def ac3(output_name, is_keep_video, ac3_bitrate):
    if is_keep_video == "yes":
        output_ext = Path(input_filename).suffix
        return return_args(
            f"-c:v copy -c:a ac3 -b:a {ac3_bitrate}k",
            f"{output_name}.{output_ext}",
        )
    # Audio only output file.
    return return_args(
        f"-c:a ac3 -b:a {ac3_bitrate}k",
        f"{output_name}.ac3",
    )


# ALAC
def alac(output_name, is_keep_video):
    if is_keep_video == "yes":
        return return_args(
            "-c:v copy -c:a alac",
            f"{output_name}.mkv",
        )
    # Audio only output file.
    return return_args(
        "-map 0:a -c:a alac",
        f"{output_name}.m4a",
    )


# CAF
def caf(output_name):
    return return_args("-c:a alac", f"{output_name}.caf")


# DTS
def dts(output_name, is_keep_video, dts_bitrate):
    if is_keep_video == "yes":
        output_ext = Path(input_filename).suffix
        return return_args(
            f"-c:v copy -c:a dca -b:a {dts_bitrate}k " f"-strict -2",
            f"{output_name}.{output_ext}",
        )
    # Audio only output file.
    return return_args(
        f"-c:a dca -b:a {dts_bitrate}k -strict -2",
        f"{output_name}.dts",
    )


# FLAC
def flac(output_name, is_keep_video, flac_compression):
    if is_keep_video == "yes":
        return return_args(
            f"-map 0 -c:v copy -c:s copy -c:a flac " f"-compression_level {flac_compression}",
            f"{output_name}.mkv",
        )
    # Audio only output file.
    return return_args(
        f"-c:a flac -compression_level {flac_compression}",
        f"{output_name}.flac",
    )


# MKA
def mka(output_name):
    return return_args(
        "-map 0:a -c:a copy",
        f"{output_name}.mka",
    )


# MKV
def mkv(output_name, video_mode, crf_value):
    # No transcoding, simply change the container to MKV.
    if video_mode == "keep_codecs":
        return return_args(
            f"-map 0 -c copy",
            f"{output_name}.mkv",
        )
    # Keep the video as-is, encode the audio.
    elif video_mode == "keep_video_codec":
        return return_args(
            f"-map 0 -c:v copy -c:s copy -c:a {aac_encoder} {aac_vbr_enabler} 5",
            f"{output_name}.mkv",
        )
    # Transcode the video, leave the audio as-is.
    elif video_mode == "convert_video_keep_audio":
        return return_args(
            f"-map 0 -c:v libx264 -crf {crf_value} -c:a copy " "-c:s copy",
            f"{output_name}.mkv",
        )
    # Transcode the video and audio.
    else:
        return return_args(
            f"-map 0 -c:v libx264 -preset {video_mode} "
            f"-crf {crf_value} -c:a {aac_encoder}  copy",
            f"{output_name}.mkv",
        )


# MP3
def mp3(
    output_name,
    is_keep_video,
    encoding_type,
    bitrate,
    vbr_setting,
):
    if is_keep_video == "yes":
        output_ext = "mkv" if Path(input_filename).suffix != "mp4" else "mp4"

        if encoding_type == "cbr":
            return return_args(
                "-c:v copy -c:a libmp3lame -b:a {bitrate}k",
                f"{output_name}.{output_ext}",
            )
        elif encoding_type == "abr":
            return return_args(
                f"-c:v copy -c:a libmp3lame --abr 1 -b:a {bitrate}k",
                f"{output_name}.{output_ext}",
            )
        # VBR was selected.
        else:
            return return_args(
                "-c:v copy -c:a libmp3lame " f"-q:a {vbr_setting}",
                f"{output_name}.{output_ext}",
            )

    # Keep the video was not selected - audio only output file:

    if encoding_type == "cbr":
        return return_args(
            f"-c:a libmp3lame -b:a {bitrate}k",
            f"{output_name}.mp3",
        )
    elif encoding_type == "abr":
        return return_args(
            f"-c:a libmp3lame --abr 1 -b:a {bitrate}k",
            f"{output_name}.mp3",
        )
    # VBR was selected.
    else:
        return return_args(
            f"-c:a libmp3lame -q:a {vbr_setting}",
            f"{output_name}.mp3",
        )


# MP4
def mp4(output_name, video_mode, crf_value):
    constant_options = "-map 0:V? -map 0:a? -map 0:s? -c:s mov_text -movflags faststart"
    # No transcoding, simply change the container to MP4.
    if video_mode == "keep_codecs":
        return return_args(
            f"{constant_options} -c copy",
            f"{output_name}.mp4",
        )
    # Keep the video as-is, encode the audio.
    elif video_mode == "keep_video_codec":
        return return_args(
            f"{constant_options} -c:V copy -c:a {aac_encoder} {aac_vbr_enabler} 5",
            f"{output_name}.mp4",
        )
    # Transcode the video, keep the audio as-is.
    elif video_mode == "convert_video_keep_audio":
        return return_args(
            f"{constant_options} -c:V libx264 -crf {crf_value} -c:a copy",
            f"{output_name}.mp4",
        )
    # Transcode the video and audio.
    else:
        return return_args(
            f"{constant_options} -c:V libx264 -preset {video_mode}"
            f" -crf {crf_value} -c:a {aac_encoder} {aac_vbr_enabler} 5",
            f"{output_name}.mp4",
        )


# Opus
def opus(output_name, encoding_type, bitrate):
    # Opus does not support >256 kbps per channel.
    if is_mono_audio(input_filename):
        bitrate = "256" if int(bitrate) > 256 else bitrate
    # VBR
    if encoding_type == "opus_vbr":
        return return_args(
            f"-c:a libopus -b:a {bitrate}k",
            f"{output_name}.opus",
        )
    # CBR
    return return_args(
        f"-c:a libopus -vbr off -b:a {bitrate}k",
        f"{output_name}.opus",
    )


# Vorbis
def vorbis(output_name, encoding_type, quality_level, bitrate):
    if encoding_type == "abr":
        return return_args(
            f"-c:a libvorbis -b:a {bitrate}k",
            f"{output_name}.ogg",
        )
    # Constant quality mode.
    return return_args(
        f"-c:a libvorbis -q:a {quality_level}",
        f"{output_name}.ogg",
    )


# WAV
def wav(output_name, is_keep_video, wav_bit_depth):
    if is_keep_video == "yes":
        return return_args(
            f"-c:v copy -c:a pcm_s{wav_bit_depth}le",
            f"{output_name}.mkv",
        )
    # Audio only output file.
    return return_args(
        f"-c:a pcm_s{wav_bit_depth}le",
        f"{output_name}.wav",
    )
