DROP DATABASE IF EXISTS av_converter;
CREATE DATABASE av_converter;

\c av_converter

DROP TABLE IF EXISTS users;

CREATE TABLE users (
  ip VARCHAR(15),
  country CHAR(2),
  times_used SMALLINT,
  first_used TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
);