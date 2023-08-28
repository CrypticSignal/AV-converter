import dotenv from "dotenv";
import { ChildProcess } from "child_process";
import express, { Application, Request, Response } from "express";
import { readFile, writeFile } from "fs/promises";
import { parse, resolve } from "path";
import { handleDownloadEvents } from "./handleDownloadEvents";
import { Logger } from "./logger";
import { updateDatabase } from "./utils";
import geoip from "geoip-country";
import youtubedl from "youtube-dl-exec";

const app: Application = express();
app.use(express.json());
app.use(express.static("../frontend/src/game"));

const port = 8080;
const log = new Logger();

dotenv.config({ path: __dirname + "/../.env" });

app.post("/api/download", async (req: Request, res: Response) => {
  const { buttonClicked, link, progressFilename } = req.body;
  await writeFile(progressFilename, "");

  const dateAndTime = new Date().toLocaleString("en-gb");

  log.info("-------------------------------------------------------------------------------------");
  log.info(`[${dateAndTime}] ${req.headers["x-real-ip"]} chose ${buttonClicked}`);
  log.info(req.headers["user-agent"]!);
  log.info(link);

  let opts: { [key: string]: string | boolean } = {};

  switch (buttonClicked) {
    case "video_best":
      opts["f"] = "bv*+ba/b";
      break;
    case "mp4":
      opts["f"] = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b";
      break;
    case "audio_best":
      opts["x"] = true;
      break;
    case "audio_mp3":
      opts["x"] = true;
      opts["audioFormat"] = "mp3";
      opts["audioQuality"] = "0";
  }

  youtubedl(link, {
    getFilename: true,
  }).then((output) => {
    const filenameWithoutExt = parse(output.toString()).name;
    const downloadProcess: ChildProcess = youtubedl.exec(link, opts);
    handleDownloadEvents(res, downloadProcess, progressFilename, filenameWithoutExt);
    const ip = req.header("x-forwarded-for")!;
    if (process.env.ENVIRONMENT) updateDatabase(ip, geoip.lookup(ip)!.country);
  });
});

app.get("/api/:progressFilename", async (req: Request, res: Response) => {
  try {
    const data = await readFile(req.params.progressFilename);
    res.send(data);
  } catch {
    // Empty catch block because the frontend might request the progress file shortly after it's been deleted
    // as the frontend only checks whether to request the progress file every 500ms.
    // See frontend/src/utils/sendDownloadrequest.ts for further context.
  }
});

app.get("/game", (_, res: Response) => {
  res.sendFile(resolve("../frontend/src/game/game.html"));
});

app.listen(port);
