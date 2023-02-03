const fs = require("fs");
import { sendFile, deleteFile, purgeUnwantedFiles } from "./utils";
const { Logger } = require("./logger");

const log = new Logger();

exports.handleDownloadEvents = (
  res: Response,
  process: any,
  progressFilename: string,
  filenameWithoutExt: string
) => {
  process.stdout.on("data", (data: Buffer) => {
    fs.createWriteStream(progressFilename).write(data);
  });

  process.stderr.on("data", (data: Buffer) => {
    fs.createWriteStream(progressFilename).write(data);
    log.error(data);
  });

  process.on("close", (code: number) => {
    if (code == 0) {
      const filename = fs
        .readdirSync(__dirname + "/../")
        .filter((file: string) => file.includes(filenameWithoutExt))[0];

      log.info(filename);
      sendFile(res, filename);
    }
    deleteFile(progressFilename);
    purgeUnwantedFiles()
  });
};
