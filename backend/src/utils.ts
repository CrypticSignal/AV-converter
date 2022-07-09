import dotenv from "dotenv";
import fs from "fs";
const { Logger } = require("./logger");
const { Pool } = require("pg"); // node-postgres

const log = new Logger();

dotenv.config({ path: __dirname + "/../.env" });

const pool = new Pool({
  user: process.env.PGUSER,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  password: process.env.PGPASSWORD,
  port: process.env.PGPORT,
});

async function updateDatabase(ip: string, country: string) {
  const { rows } = await pool.query(`SELECT * FROM users WHERE ip=$1`, [ip]);

  if (rows[0]) {
    const timesPreviouslyUsed = rows[0].times_used;
    const timeOrTimes = timesPreviouslyUsed > 1 ? "times" : "time";

    log.info(`This user has used the downloader ${timesPreviouslyUsed} ${timeOrTimes} before.`);

    pool.query(
      `
      UPDATE users
      SET times_used = $1, last_used = $2
      WHERE ip=$3;
      `,
      [timesPreviouslyUsed + 1, new Date().toLocaleString(), ip]
    ),
      (err: any) => {
        if (err) log.error(`[Postgres UPDATE] ${err.stack}`);
      };
  } else {
    pool.query(
      `INSERT into users(ip, country, times_used) VALUES ('${ip}', '${country}', 1);`,
      (err: any) => {
        if (err) log.error(`[Postgres INSERT] ${err.stack}`);
      }
    );
  }
}

function sendFile(res: any, filename: string) {
  res.download(filename, (err: any) => {
    if (err) {
      log.error(`Unable to send ${filename} to the browser: \n${err}`);
    }
    deleteFile(filename);
  });
}

async function deleteFile(filepath: string) {
  try {
    await fs.promises.unlink(filepath);
  } catch (err) {
    log.error(`Unable to delete ${filepath}: \n${err}`);
  }
}

module.exports = { updateDatabase, sendFile, deleteFile };
