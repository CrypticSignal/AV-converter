const fs = require("fs");
const { Logger } = require("./logger");
const { Pool } = require("pg"); // node-postgres

const log = new Logger();

require("dotenv").config();

const pool = new Pool({
  user: process.env.PGUSER,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  password: process.env.PGPASSWORD,
  port: process.env.PGPORT,
});

async function updateDatabase(ip) {
  const { rows } = await pool.query(`SELECT * FROM users WHERE ip=$1`, [ip]);

  if (rows[0]) {
    const timesPreviouslyUsed = rows[0].times_used;
    const timeOrTimes = timesPreviouslyUsed > 1 ? "times" : "time";

    log.info(`This user has used the downloader ${timesPreviouslyUsed} ${timeOrTimes} before.`);

    pool.query(
      `UPDATE users
        SET times_used = ${timesPreviouslyUsed + 1}
        WHERE ip=$1`,
      [ip]
    ),
      (err, _) => {
        if (err) log.error(`[Postgres UPDATE] ${err.stack}`);
      };
  } else {
    pool.query(`INSERT into users(ip, times_used) VALUES ('${ip}', 1);`, (err, _) => {
      if (err) log.error(`[Postgres INSERT] ${err.stack}`);
    });
  }
}

function sendFile(res, filename) {
  res.download(filename, (err) => {
    if (err) {
      log.error(`Unable to send ${filename} to the browser: \n${err}`);
      return;
    }
    deleteFile(filename);
  });
}

async function deleteFile(filepath) {
  try {
    await fs.promises.unlink(filepath);
  } catch (err) {
    log.error(`Unable to delete ${filepath}: \n${err}`);
  }
}

module.exports = { updateDatabase, sendFile, deleteFile };
