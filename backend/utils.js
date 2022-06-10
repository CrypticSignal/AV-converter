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

module.exports = { updateDatabase };
