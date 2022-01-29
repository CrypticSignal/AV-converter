const conversionData = (encodingArgs, outputFilename) => {
  encodingArgs = encodingArgs.split(" ");
  console.log(encodingArgs);

  const ffmpegArgs = [
    "-metadata",
    "encoded_by=av-converter.com",
    "-id3v2_version",
    "3",
    "-write_id3v1",
    "true",
    ...encodingArgs,
  ];

  return {
    ffmpegArgs: ffmpegArgs,
    outputFilename: outputFilename,
  };
};

export const createFFmpegArgs = (
  aacEncodingType,
  aacExtension,
  aacVbrMode,
  ac3Bitrate,
  codec,
  crfValue,
  dtsBitrate,
  flacCompression,
  isKeepVideo,
  inputFilename,
  mp3EncodingType,
  mp3VbrSetting,
  numLogicalProcessors,
  opusEncodingType,
  outputName,
  qValue,
  sliderValue,
  transcodeVideo,
  transcodeVideosAudio,
  videoBitrate,
  videoContainer,
  videoEncodingType,
  vorbisEncodingType,
  wavBitDepth,
  x264Preset
) => {
  // AAC
  if (codec === "AAC") {
    const args = `-map 0:a -c:a libfdk_aac`;

    if (isKeepVideo === "yes") {
      args += " -map 0:V -c:V copy";
      const ext = inputFilename.split(".").slice(0, -1).join(".");

      if (aacEncodingType === "cbr") {
        return conversionData(`${args} -b:a ${sliderValue}k`, `${outputName}.${ext}`);
      }
      return conversionData(`${args} -vbr ${aacVbrMode}`, `${outputName}.${ext}`);
    }
    // Audio only output file.
    if (aacEncodingType === "cbr") {
      return conversionData(`${args} -b:a ${sliderValue}`, `${outputName}.${aacExtension}`);
    }
    // VBR
    return conversionData(`${args} -vbr ${aacVbrMode}`, `${outputName}.${aacExtension}`);

    // AC3
  } else if (codec === "AC3") {
    const ext = inputFilename.split(".").slice(0, -1).join(".");
    if (isKeepVideo === "yes") {
      return conversionData(`-c:v copy -c:a ac3 -b:a ${ac3Bitrate}k`, `${outputName}.${ext}`);
    }
    // Audio only output file.
    return conversionData(`-c:a ac3 -b:a ${ac3Bitrate}k`, `${outputName}.${ext}`);

    // ALAC
  } else if (codec === "ALAC") {
    if (isKeepVideo === "yes") {
      return conversionData(`-c:v copy -c:a alac`, `${outputName}.mkv`);
    }
    // Audio only output file.
    return conversionData(`-map 0:a -c:a alac`, `${outputName}.m4a`);

    // CAF
  } else if (codec === "CAF") {
    return conversionData(`-c:a alac`, `${outputName}.caf`);

    // DTS
  } else if (codec === "DTS") {
    const ext = inputFilename.split(".").slice(0, -1).join(".");
    if (isKeepVideo === "yes") {
      return conversionData(
        `-c:v copy -c:a dca -b:a ${dtsBitrate}k -strict -2`,
        `${outputName}.${ext}`
      );
    }
    // Audio only output file.
    return conversionData(`-c:a dca -b:a ${dtsBitrate}k -strict -2`, `${outputName}.${ext}`);

    // FLAC
  } else if (codec === "FLAC") {
    if (isKeepVideo === "yes") {
      return conversionData(
        `-map 0 -c:v copy -c:s copy -c:a flac -compression_level ${flacCompression}`,
        `${outputName}.mkv`
      );
    }
    // Audio only output file.
    return conversionData(`-c:a flac -compression_level ${flacCompression}`, `${outputName}.flac`);

    // H.264
  } else if (codec === "H264") {
    const outputFilename = `${outputName}.${videoContainer}`;
    const args = "-map 0:V? -map 0:a? -map 0:s?";

    if (videoContainer === "mp4") {
      args += " -c:a libfdk_aac -vbr 5";
    }

    if (transcodeVideosAudio) {
      args += " -c:a libfdk_aac -vbr 5";
    } else {
      args += " -c:a copy";
    }

    if (transcodeVideo === "no") {
      if (videoContainer === "mp4") {
        args += " -c:V copy -f mp4";
        return conversionData(args, outputFilename);
      }
      // MKV container.
      args += " -c:V copy -c:s copy -f matroska";
      return conversionData(args, outputFilename);
    } else {
      const threads = numLogicalProcessors * 1.5;
      // A value of 12+ causes "null function or function signature mismatch" error.
      threads = threads < 12 ? threads : 11;
      args += ` -c:V libx264 -x264-params threads=${threads} -preset ${x264Preset}`;
      // CRF
      if (videoEncodingType === "crf") {
        args += ` -crf ${crfValue}`;
        return conversionData(args, outputFilename);
      }
      // Target a bitrate.
      args += ` -b:v ${videoBitrate}M`;
      return conversionData(args, outputFilename);
    }

    // MKA
  } else if (codec === "MKA") {
    return conversionData(`-map 0:a -c:a copy`, `${outputName}.mka`);

    // MP3
  } else if (codec === "MP3") {
    if (isKeepVideo === "yes") {
      const inputExt = inputFilename.split(".").slice(0, -1).join(".");
      const outputExt = inputExt === "mp4" ? inputExt : "mkv";
      // CBR
      if (mp3EncodingType === "cbr") {
        return conversionData(
          `-c:v copy -c:a libmp3lame -b:a ${sliderValue}k`,
          `${outputName}.${outputExt}`
        );
        // ABR
      } else if (mp3EncodingType === "abr") {
        return conversionData(
          `-c:v copy -c:a libmp3lame --abr 1 -b:a ${sliderValue}k`,
          `${outputName}.${outputExt}`
        );
      }
      // VBR
      return conversionData(
        `-c:v copy -c:a libmp3lame -q:a ${mp3VbrSetting}`,
        `${outputName}.${outputExt}`
      );
    }
    // Audio only output file.
    if (mp3EncodingType === "cbr") {
      return conversionData(`-c:a libmp3lame -b:a ${sliderValue}k`, `${outputName}.mp3`);
      // ABR
    } else if (mp3EncodingType === "abr") {
      return conversionData(`-c:a libmp3lame --abr 1 -b:a ${sliderValue}k`, `${outputName}.mp3`);
    }
    // VBR
    return conversionData(`-c:a libmp3lame -q:a ${mp3VbrSetting}`, `${outputName}.mp3`);

    // Opus
  } else if (codec === "Opus") {
    if (opusEncodingType === "abr") {
      return conversionData(`-c:a libopus -b:a ${sliderValue}k`, `${outputName}.opus`);
    }
    // CBR
    return conversionData(`-c:a libopus -vbr off -b:a ${sliderValue}k`, `${outputName}.opus`);

    // Vorbis
  } else if (codec === "Vorbis") {
    // ABR
    if (vorbisEncodingType == "abr") {
      return conversionData(`-map 0:a -c:a libvorbis -b:a ${sliderValue}k`, `${outputName}.ogg`);
    }
    // Target a quality level.
    return conversionData(`-map 0:a -c:a libvorbis -q:a ${qValue}`, `${outputName}.ogg`);

    // WAV
  } else if (codec === "WAV") {
    if (isKeepVideo === "yes") {
      return conversionData(`-c:v copy -c:a pcm_s${wavBitDepth}le`, `${outputName}.wav`);
    }
    // Audio only output file.
    return conversionData(`-c:a pcm_s${wavBitDepth}le`, `${outputName}.wav`);
  }
};
