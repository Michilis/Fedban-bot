const TelegramBot = require('node-telegram-bot-api');
const { connectDb } = require('./db');
const { handleCommands, handleHelpCallback, handleHelpSectionCallback } = require('./commands');
require('dotenv').config();

const bot = new TelegramBot(process.env.TELEGRAM_TOKEN, { polling: true });

bot.on('message', async (msg) => {
  try {
    await handleCommands(bot, msg);
  } catch (error) {
    console.error('Error handling message:', error);
    await bot.sendMessage(msg.chat.id, 'An error occurred while processing your request.');
  }
});

bot.on('callback_query', async (callbackQuery) => {
  const { message, data } = callbackQuery;
  try {
    if (data === 'help') {
      await handleHelpCallback(bot, message);
    } else if (data.startsWith('help_')) {
      const section = data.split('_')[1];
      await handleHelpSectionCallback(bot, message, section);
    }
  } catch (error) {
    console.error('Error handling callback query:', error);
    await bot.sendMessage(message.chat.id, 'An error occurred while processing your request.');
  }
});

connectDb().then(() => {
  console.log('Bot is running...');
}).catch(error => {
  console.error('Database connection error:', error);
});
