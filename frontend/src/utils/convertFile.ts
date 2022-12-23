import { createFFmpeg, fetchFile } from "@ffmpeg/ffmpeg";
import { Dispatch, SetStateAction } from "react";
import showAlert from "./showAlert";

export const convertFile = async (
  file: File,
  ffmpegArgs: string[],
  inputFilename: string,
  outputFilename: string,
  setProgress: Dispatch<SetStateAction<number>>
) => {
  document.getElementById("converting_spinner")!.style.display = "block";
  document.getElementById("conversion_progress")!.style.display = "block";

  const getProgress = ({ ratio }: { ratio: number }) => {
    setProgress(parseInt((ratio * 100).toFixed(1)));
  };

  const ffmpeg = createFFmpeg({
    log: true,
    progress: getProgress,
  });

  ffmpeg.setLogger(({ message }: { message: string }) => {
    showAlert(message, "info");
  });

  await ffmpeg.load();
  ffmpeg.FS("writeFile", inputFilename, await fetchFile(file));

  const startTime = Date.now() / 1000;
  // Run FFmpeg
  await ffmpeg.run(...ffmpegArgs);
  console.log(`Conversion took ${(Date.now() / 1000 - startTime).toFixed(1)} seconds.`);
  // Reset the value of progress.
  setProgress(0);

  const data = ffmpeg.FS("readFile", outputFilename);
  const objectURL = URL.createObjectURL(new Blob([data.buffer]));

  const anchorTag = document.createElement("a");
  anchorTag.href = objectURL;
  anchorTag.download = outputFilename;
  anchorTag.click();

  // Delete file from MEMFS
  ffmpeg.FS("unlink", outputFilename);

  showAlert(
    `Conversion complete. The converted file should be downloading :)<br>If it isn't, click <a href="${objectURL}" download="${outputFilename}">here</a> to start the download.`,
    "success"
  );

  document.getElementById("converting_spinner")!.style.display = "none";
  document.getElementById("conversion_progress")!.style.display = "none";
  document.getElementById("convert_btn")!.style.display = "block";
};
