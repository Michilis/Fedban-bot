const TelegramBot = require('node-telegram-bot-api');
const { connectDb } = require('./db');
const { handleCommands } = require('./commands/index');

require('dotenv').config();

const bot = new TelegramBot(process.env.TELEGRAM_TOKEN, { polling: true });

bot.on('message', (msg) => {
  handleCommands(bot, msg);
});

bot.on('callback_query', (callbackQuery) => {
  const { message, data } = callbackQuery;
  const chatId = message.chat.id;
  
  if (data === 'help') {
    handleHelpCallback(bot, message);
  } else if (data.startsWith('help_')) {
    const section = data.split('_')[1];
    handleHelpSectionCallback(bot, message, section);
  }
});

connectDb().then(() => {
  console.log('Bot is running...');
});
