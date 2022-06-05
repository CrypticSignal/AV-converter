const cors = require("cors");
const express = require("express");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const { handleDownloadEvents } = require("./handleDownloadEvents");
const { Logger } = require("./logger");

app = express();
app.use(cors());
app.use(express.json());
app.use(express.static("../frontend/src/game"));

const port = 9090;

const log = new Logger();

app.post("/api/download", async (req, res) => {
  const { buttonClicked, link, progressFilename } = req.body;
  await fs.promises.writeFile(progressFilename, "");

  const dateAndTime = new Date().toLocaleString("en-gb");

  log.info("-------------------------------------------------------------------------------------");
  log.info(`[${dateAndTime}] ${req.headers["x-real-ip"]} chose ${buttonClicked}`);
  log.info(req.headers["user-agent"]);
  log.info(link);

  let opts = [link];

  if (buttonClicked === "video_best") {
    opts.push(...["-f", "bv*+ba/b"]);
  } else if (buttonClicked === "audio_best") {
    opts.push("-x");
  } else if (buttonClicked === "mp4") {
    opts.push(...["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b"]);
  } else if (buttonClicked === "audio_mp3") {
    opts.push(...["-x", "--audio-format", "mp3", "--audio-quality", "0"]);
  }

  const filenameProcess = spawn("/usr/local/bin/yt-dlp", ["--get-filename", link]);
  let filenameWithoutExt;

  filenameProcess.stdout.on("data", (data) => {
    const outputFilename = data.toString().trim();
    filenameWithoutExt = outputFilename.split(".").slice(0, -1).join(".");
  });

  filenameProcess.stderr.on("data", (data) => {
    log.info(`filenameProcess stderr: \n${data}`);
  });

  filenameProcess.on("error", (error) => {
    log.error(`filenameProcess error: \n${error.message}`);
  });

  filenameProcess.stdout.on("close", () => {
    try {
      const downloadProcess = spawn("/usr/local/bin/yt-dlp", [...opts]);
      handleDownloadEvents(res, downloadProcess, progressFilename, filenameWithoutExt);
    } catch (err) {
      log.error(err);
    }
  });
});

app.get("/api/:progressFilename", async (req, res) => {
  const data = await fs.promises.readFile(req.params.progressFilename);
  res.send(data);
});

app.get("/game", (req, res) => {
  res.sendFile(path.resolve("../frontend/src/game/game.html"));
});

app.listen(port);
