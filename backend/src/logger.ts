import { appendFile } from "fs/promises";

export class Logger {
  async debug(msg: string) {
    await appendFile("debug.log", `\n[DEBUG]: ${msg}`);
  }
  async info(msg: string) {
    await appendFile("info.log", `\n${msg}`);
  }
  async error(msg: string) {
    await appendFile("error.log", `\n[ERROR]: ${msg}`);
  }
}
