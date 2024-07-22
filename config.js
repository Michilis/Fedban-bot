require('dotenv').config();

module.exports = {
  telegramToken: process.env.TELEGRAM_TOKEN,
  databaseUrl: process.env.DATABASE_URL,
  logGroupId: process.env.LOG_GROUP_ID,
};
