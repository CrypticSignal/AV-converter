import { ChildProcess } from "child_process";
import { createWriteStream, readdirSync } from "fs";
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
    if (data.toString() !== "\n") {
      createWriteStream(progressFilename).write(data.toString().trim());
    }
  });

  process.stderr?.on("data", (data: Buffer) => {
    createWriteStream(progressFilename).write(data.toString().trim());
    log.error(data.toString().trim());
  });

  process.on("close", (code: number) => {
    if (code === 0) {
      const filename = readdirSync(__dirname + "/../").filter((file: string) =>
        file.includes(filenameWithoutExt)
      )[0];

      log.info(filename);
      sendFile(res, filename);
    }
    deleteFile(progressFilename);
    purgeUnwantedFiles();
  });
}
