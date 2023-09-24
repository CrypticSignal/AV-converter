import { FFmpeg } from "@ffmpeg/ffmpeg";
import { toBlobURL, fetchFile } from "@ffmpeg/util";
import { Dispatch, SetStateAction } from "react";
import showAlert from "./showAlert";

const ffmpegCoreVersion = "0.12.3";

export const convertFile = async (
  ffmpeg: FFmpeg,
  file: File,
  ffmpegArgs: string[],
  inputFilename: string,
  outputFilename: string,
  setProgress: Dispatch<SetStateAction<number>>
) => {
  showAlert(`Loading @ffmpeg/core v${ffmpegCoreVersion}`, "warning");

  const baseURL = `https://unpkg.com/@ffmpeg/core-mt@${ffmpegCoreVersion}/dist/umd`;

  await ffmpeg.load({
    coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, "text/javascript"),
    wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, "application/wasm"),
    workerURL: await toBlobURL(`${baseURL}/ffmpeg-core.worker.js`, "text/javascript"),
  });

  ffmpeg.on("log", ({ message }) => {
    showAlert(message, "info");
    console.log(message);
  });

  ffmpeg.on("progress", ({ progress }) => {
    progress = Math.round(progress * 100 * 10) / 10;
    setProgress(progress);
  });

  await ffmpeg.writeFile(inputFilename, await fetchFile(file));

  const startTime = Date.now() / 1000;
  // Run FFmpeg
  document.getElementById("converting_spinner")!.style.display = "block";
  document.getElementById("conversion_progress")!.style.display = "block";
  await ffmpeg.exec([...ffmpegArgs]);
  document.getElementById("converting_spinner")!.style.display = "none";
  document.getElementById("conversion_progress")!.style.display = "none";
  console.log(`Conversion took ${(Date.now() / 1000 - startTime).toFixed(1)} seconds.`);
  // // Reset the value of progress.
  // setProgress(0);

  const fileData = await ffmpeg.readFile(outputFilename);
  const data = new Uint8Array(fileData as ArrayBuffer);
  const objectURL = URL.createObjectURL(new Blob([data.buffer]));

  const anchorTag = document.createElement("a");
  anchorTag.href = objectURL;
  anchorTag.download = outputFilename;
  anchorTag.click();

  // Delete file from MEMFS
  //ffmpeg.memfs

  showAlert(
    `Conversion complete. The converted file should be downloading :)<br>If it isn't, click <a href="${objectURL}" download="${outputFilename}">here</a> to start the download.`,
    "success"
  );

  document.getElementById("converting_spinner")!.style.display = "none";
  document.getElementById("conversion_progress")!.style.display = "none";
  document.getElementById("convert_btn")!.style.display = "block";
};
