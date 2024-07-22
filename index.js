require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const { handleCommands, handleHelpCallback } = require('./commands');
const { sequelize } = require('./db');

// Initialize the bot with the token from the environment variables
const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });

// Log database connection status
sequelize.authenticate()
  .then(() => {
    console.log('Database connected.');
  })
  .catch(err => {
    console.error('Unable to connect to the database:', err);
  });

// Handle incoming messages
bot.on('message', (msg) => {
  if (msg.text) {
    handleCommands(bot, msg);
  }
});

// Handle callback queries (e.g., from inline keyboards)
bot.on('callback_query', (query) => {
  handleHelpCallback(bot, query);
});

console.log('Bot is running...');
