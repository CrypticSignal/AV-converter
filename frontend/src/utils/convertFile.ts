import { FFmpeg } from '@ffmpeg/ffmpeg';
import { toBlobURL, fetchFile } from '@ffmpeg/util';
import { Dispatch, SetStateAction } from 'react';
import showAlert from './showAlert';
import reset from './reset';

export const convertFile = async (
  ffmpeg: FFmpeg,
  file: File,
  ffmpegArgs: string[],
  inputFilename: string,
  outputFilename: string,
  setProgress: Dispatch<SetStateAction<number>>
) => {
  showAlert('Loading @ffmpeg/core-mt...', 'warning');

  // Relative to the public folder
  const ffmpegFolder = '/ffmpeg';

  await ffmpeg.load({
    coreURL: await toBlobURL(`${ffmpegFolder}/ffmpeg-core.js`, 'text/javascript'),
    wasmURL: await toBlobURL(`${ffmpegFolder}/ffmpeg-core.wasm`, 'application/wasm'),
    workerURL: await toBlobURL(
      `${ffmpegFolder}/ffmpeg-core.worker.js`,
      'text/javascript'
    ),
  });

  ffmpeg.on('log', ({ message }) => {
    if (message === 'Aborted()') {
      reset();
      showAlert('Unable to convert file.', 'danger');
      return;
    }

    showAlert(message, 'info');
    console.log(message);
  });

  ffmpeg.on('progress', ({ progress }) => {
    progress = Math.round(progress * 100 * 10) / 10;
    setProgress(progress);
  });

  await ffmpeg.writeFile(inputFilename, await fetchFile(file));

  document.getElementById('converting_spinner')!.style.display = 'block';
  document.getElementById('conversion_progress')!.style.display = 'block';

  console.log(ffmpegArgs);
  const startTime = Date.now() / 1000;
  await ffmpeg.exec(ffmpegArgs);

  console.log(
    `Conversion took ${(Date.now() / 1000 - startTime).toFixed(1)} seconds.`
  );
  setProgress(0);

  const fileData = await ffmpeg.readFile(outputFilename);
  const data = new Uint8Array(fileData as ArrayBuffer);
  const objectURL = URL.createObjectURL(new Blob([data.buffer]));

  const anchorTag = document.createElement('a');
  anchorTag.href = objectURL;
  anchorTag.download = outputFilename;
  anchorTag.click();

  showAlert(
    `The converted file should have downloaded to your device.<br>If it hasn't, click <a href="${objectURL}" download="${outputFilename}">here</a>`,
    'success'
  );

  reset();
};
