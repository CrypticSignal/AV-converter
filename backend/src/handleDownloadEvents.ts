import { ChildProcess } from "child_process";
import { createWriteStream, readdir } from "fs";
import { Logger } from "./logger";
import { Response } from "express";
import { sendFile, deleteFile, purgeUnwantedFiles } from "./utils";

const log = new Logger();

export function handleDownloadEvents(
  res: Response,
  process: ChildProcess,
  progressFilename: string,
  filenameWithoutExt: string
) {
  process.stdout?.on("data", (data: Buffer) => {
    const dataTrimmed = data.toString().trim();

    if (dataTrimmed.startsWith("[download]")) {
      const downloadInfo = dataTrimmed.split(" ").filter((n) => n);

      const customDownloadProgress = `Downloaded ${downloadInfo[1]} of ${downloadInfo[3]} | ETA: ${downloadInfo[7]} @ ${downloadInfo[5]}`;

      createWriteStream(progressFilename).write(customDownloadProgress);
    } else {
      createWriteStream(progressFilename).write(dataTrimmed);
    }
  });

  process.stderr?.on("data", (data: Buffer) => {
    createWriteStream(progressFilename).write(data.toString().trim());
    log.error(data.toString().trim());
  });

  process.on("close", (code: number) => {
    if (code === 0) {
      readdir(__dirname + "/../", (err, files) => {
        if (!err) {
          const filename = files.filter((file: string) => file.includes(filenameWithoutExt))[0];
          log.info(filename);
          sendFile(res, filename);
        }
      });
    }
    deleteFile(progressFilename);
    purgeUnwantedFiles();
  });
}
