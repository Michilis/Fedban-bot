const TelegramBot = require('node-telegram-bot-api');
const { sequelize } = require('./db');
const { telegramToken } = require('./config');
const { handleCommands } = require('./commands');

const bot = new TelegramBot(telegramToken, { polling: true });

bot.on('message', (msg) => handleCommands(bot, msg));

(async () => {
  try {
    await sequelize.authenticate();
    console.log('Database connected.');
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
})();
