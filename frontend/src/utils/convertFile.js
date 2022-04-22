import { createFFmpeg, fetchFile } from "@ffmpeg/ffmpeg";
import { showAlert } from "./showAlert";

const getFFmpegWASMLogs = ({ message }) => {
  if (message !== "use ffmpeg.wasm v0.10.1") {
    showAlert(message, "info");
    console.log(message);
  }
};

export const convertFile = async (file, ffmpegArgs, inputFilename, outputFilename, setProgress) => {
  const getProgress = ({ ratio }) => {
    setProgress((ratio * 100).toFixed(1));
  };

  const ffmpeg = createFFmpeg({
    corePath: "https://unpkg.com/@ffmpeg/core@0.10.0/dist/ffmpeg-core.js",
    logger: getFFmpegWASMLogs,
    progress: getProgress,
  });

  await ffmpeg.load();
  ffmpeg.FS("writeFile", inputFilename, await fetchFile(file));

  document.getElementById("converting_spinner").style.display = "block";
  document.getElementById("conversion_progress").style.display = "block";

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

  document.getElementById("converting_spinner").style.display = "none";
  document.getElementById("conversion_progress").style.display = "none";
  document.getElementById("convert_btn").style.display = "block";
};
