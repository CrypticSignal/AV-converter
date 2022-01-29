const fs = require("fs");
const { Logger } = require("./logger");

const log = new Logger();

const sendFile = (res, filename) => {
  res.download(filename, (err) => {
    if (err) {
      log.error(`Unable to send ${filename} to the browser: \n${err}`);
      return;
    }
    deleteFile(filename);
  });
};

const deleteFile = async (filepath) => {
  try {
    await fs.promises.unlink(filepath);
  } catch (err) {
    log.error(`Unable to delete ${filepath}: \n${err}`);
  }
};

exports.handleDownloadEvents = (res, process, progressFilename, filenameWithoutExt) => {
  process.stdout.on("data", async (data) => {
    fs.writeFileSync(progressFilename, data.toString().trim());
  });

  process.stderr.on("data", (data) => {
    log.error(`yt-dlp stderr: \n${data}`);
  });

  process.on("error", (error) => {
    log.error(`yt-dlp error: \n${error.message}`);
  });

  process.on("close", (code) => {
    if (code !== 0) {
      log.error("The yt-dlp process encountered an error.");
      log.error(`The output of yt-dlp can be found in ${progressFilename}`);
      return;
    }

    const filename = fs
      .readdirSync(__dirname)
      .filter((file) => file.includes(filenameWithoutExt))[0];

    log.info(filename);
    sendFile(res, filename);
    deleteFile(progressFilename);
  });
};
