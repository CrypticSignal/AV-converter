const fs = require("fs");
const { sendFile, deleteFile } = require("./utils");
const { Logger } = require("./logger");

const log = new Logger();

exports.handleDownloadEvents = (res, process, progressFilename, filenameWithoutExt) => {
  process.stdout.on("data", (data) => {
    fs.createWriteStream(progressFilename).write(data);
  });

  process.stderr.on("data", (data) => {
    fs.createWriteStream(progressFilename).write(data);
    log.error(data);
  });

  process.on("close", (code) => {
    if (code == 0) {
      const filename = fs
        .readdirSync(__dirname)
        .filter((file) => file.includes(filenameWithoutExt))[0];

      log.info(filename);
      sendFile(res, filename);
    }
    deleteFile(progressFilename);
  });
};
