export {};

const fs = require("fs/promises");

class Logger {
  async debug(msg: string) {
    console.log(msg);
    await fs.appendFile("../logs.txt", `\n[DEBUG]: ${msg}`);
  }
  async info(msg: string) {
    console.log(msg);
    await fs.appendFile("../logs.txt", `\n${msg}`);
  }
  async error(msg: string) {
    console.log(msg);
    await fs.appendFile("../logs.txt", `\n[ERROR]: ${msg}`);
  }
}

module.exports = { Logger };
