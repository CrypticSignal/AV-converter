import { appendFile } from "fs/promises";

export class Logger {
  async debug(msg: string) {
    await appendFile("../logs.txt", `\n[DEBUG]: ${msg}`);
  }
  async info(msg: string) {
    await appendFile("../logs.txt", `\n${msg}`);
  }
  async error(msg: string) {
    await appendFile("../logs.txt", `\n[ERROR]: ${msg}`);
  }
}
