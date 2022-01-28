const fs = require("fs/promises");

class Logger {
  async debug(msg) {
    await fs.appendFile("../logs.txt", `\n[DEBUG]: ${msg}`);
  }
  async info(msg) {
    await fs.appendFile("../logs.txt", `\n${msg}`);
  }
  async error(msg) {
    await fs.appendFile("../logs.txt", `\n[ERROR]: ${msg}`);
  }
}

module.exports = { Logger };
