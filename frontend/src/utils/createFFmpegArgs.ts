interface ConversionData {
  ffmpegArgs: string[];
  outputFilename: string;
}

const createConversionData = (encodingArgs: string, outputFilename: string): ConversionData => {
  const encodingArgsArray = encodingArgs.split(" ");

  const ffmpegArgs = [
    "-metadata",
    "encoded_by=av-converter.com",
    "-id3v2_version",
    "3",
    "-write_id3v1",
    "true",
    ...encodingArgsArray,
  ];

  return {
    ffmpegArgs: ffmpegArgs,
    outputFilename: outputFilename,
  };
};

export const createFFmpegArgs = (
  ac3Bitrate: string,
  bitrateSliderValue: string,
  codec: string,
  crfValue: string,
  flacCompression: string,
  isKeepVideo: boolean,
  inputFilename: string,
  mp3EncodingType: string,
  mp3VbrSetting: string,
  numLogicalProcessors: number,
  opusEncodingType: string,
  outputName: string,
  qValue: string,
  transcodeVideo: boolean,
  transcodeAudio: boolean,
  videoBitrate: string,
  videoContainer: string,
  videoEncodingType: string,
  vorbisEncodingType: string,
  wavBitDepth: string,
  x264Preset: string
) => {
  // AAC
  if (codec === "AAC") {
    let args = `-map 0:a -c:a aac`;

    if (isKeepVideo) {
      args += " -map 0:V -c:V copy";
      const ext = inputFilename.substring(inputFilename.lastIndexOf("."))
      return createConversionData(`${args} -b:a ${bitrateSliderValue}k`, `${outputName}${ext}`);
    }
    // Audio only output file.
    return createConversionData(`${args} -b:a ${bitrateSliderValue}k`, `${outputName}.aac`);

    // AC3
  } else if (codec === "AC3") {
    const ext = inputFilename.substring(inputFilename.lastIndexOf("."))
    
    if (isKeepVideo) {
      return createConversionData(`-c:v copy -c:a ac3 -b:a ${ac3Bitrate}k`, `${outputName}${ext}`);
    }
    // Audio only output file.
    return createConversionData(`-c:a ac3 -b:a ${ac3Bitrate}k`, `${outputName}.ac3`);

    // ALAC
  } else if (codec === "ALAC") {
    if (isKeepVideo) {
      return createConversionData(`-c:v copy -c:a alac`, `${outputName}.mkv`);
    }
    // Audio only output file.
    return createConversionData(`-map 0:a -c:a alac`, `${outputName}.m4a`);

    // CAF
  } else if (codec === "CAF") {
    return createConversionData(`-c:a alac`, `${outputName}.caf`);

    // DTS
  } else if (codec === "DTS") {
    const ext = inputFilename.substring(inputFilename.lastIndexOf("."))
    if (isKeepVideo) {
      return createConversionData(
        `-c:v copy -c:a dca -b:a ${bitrateSliderValue}k -strict -2`,
        `${outputName}${ext}`
      );
    }
    // Audio only output file.
    return createConversionData(
      `-c:a dca -b:a ${bitrateSliderValue}k -strict -2`,
      `${outputName}.dts`
    );

    // FLAC
  } else if (codec === "FLAC") {
    if (isKeepVideo) {
      return createConversionData(
        `-map 0 -c:v copy -c:s copy -c:a flac -compression_level ${flacCompression}`,
        `${outputName}.mkv`
      );
    }
    // Audio only output file.
    return createConversionData(
      `-map 0:a -c:a flac -compression_level ${flacCompression}`,
      `${outputName}.flac`
    );

    // H.264
  } else if (codec === "H264") {
    const outputFilename = `${outputName}.${videoContainer}`;
    let args = "-map 0:V? -map 0:a? -map 0:s?";
    transcodeAudio ? (args += " -c:a aac -b:a 256k") : (args += " -c:a copy");

    if (!transcodeVideo) {
      videoContainer === "mp4"
        ? (args += " -c:V copy -f mp4")
        : (args += " -c:V copy -c:s copy -f matroska");
      return createConversionData(args, outputFilename);
    }

    // MP4 doesn't support all subtitle formats. Convert the subtitle tracks to mov_text which MP4 supports.
    if (videoContainer === "mp4") {
      args += " -c:s mov_text";
    }

    let threads = numLogicalProcessors * 1.5;
    // A value of 12+ causes "null function or function signature mismatch" error.
    threads = threads < 12 ? threads : 11;
    args += ` -c:V libx264 -x264-params threads=${threads} -preset ${x264Preset}`;
    // CRF
    if (videoEncodingType === "crf") {
      args += ` -crf ${crfValue}`;
      return createConversionData(args, outputFilename);
    }
    // Target a bitrate.
    args += ` -b:v ${videoBitrate}M`;
    return createConversionData(args, outputFilename);

    // MKA
  } else if (codec === "MKA") {
    return createConversionData(`-map 0:a -c:a copy`, `${outputName}.mka`);

    // MP3
  } else if (codec === "MP3") {
    if (isKeepVideo) {
      const inputExt = inputFilename.substring(inputFilename.lastIndexOf("."))
      const outputExt = inputExt === ".mp4" ? inputExt : ".mkv";
      // CBR
      if (mp3EncodingType === "cbr") {
        return createConversionData(
          `-c:v copy -c:a libmp3lame -b:a ${bitrateSliderValue}k`,
          `${outputName}${outputExt}`
        );
        // ABR
      } else if (mp3EncodingType === "abr") {
        return createConversionData(
          `-c:v copy -c:a libmp3lame --abr 1 -b:a ${bitrateSliderValue}k`,
          `${outputName}${outputExt}`
        );
      }
      // VBR
      return createConversionData(
        `-c:v copy -c:a libmp3lame -q:a ${mp3VbrSetting}`,
        `${outputName}${outputExt}`
      );
    }
    // Audio only output file.
    if (mp3EncodingType === "cbr") {
      return createConversionData(
        `-c:a libmp3lame -b:a ${bitrateSliderValue}k`,
        `${outputName}.mp3`
      );
      // ABR
    } else if (mp3EncodingType === "abr") {
      return createConversionData(
        `-c:a libmp3lame --abr 1 -b:a ${bitrateSliderValue}k`,
        `${outputName}.mp3`
      );
    }
    // VBR
    return createConversionData(`-c:a libmp3lame -q:a ${mp3VbrSetting}`, `${outputName}.mp3`);

    // Opus
  } else if (codec === "Opus") {
    return createConversionData(
      `-c:a libopus ${opusEncodingType === "cbr" ? "-vbr off " : ""}-b:a ${bitrateSliderValue}k`,
      `${outputName}.opus`
    );

    // Vorbis
  } else if (codec === "Vorbis") {
    // ABR
    if (vorbisEncodingType === "abr") {
      return createConversionData(
        `-map 0:a -c:a libvorbis -b:a ${bitrateSliderValue}k`,
        `${outputName}.ogg`
      );
    }
    // Target a quality level.
    return createConversionData(`-map 0:a -c:a libvorbis -q:a ${qValue}`, `${outputName}.ogg`);

    // WAV
  } else {
    if (isKeepVideo) {
      return createConversionData(`-c:v copy -c:a pcm_s${wavBitDepth}le`, `${outputName}.wav`);
    }
    // Audio only output file.
    return createConversionData(`-c:a pcm_s${wavBitDepth}le`, `${outputName}.wav`);
  }
};
