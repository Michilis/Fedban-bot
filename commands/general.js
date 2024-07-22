const messages = require('../messages');

async function handleStart(bot, msg) {
  try {
    await bot.sendMessage(msg.chat.id, messages.start);
  } catch (error) {
    console.error('Error handling /start command:', error);
    await bot.sendMessage(msg.chat.id, 'An error occurred while processing the /start command.');
  }
}

async function handleHelp(bot, msg) {
  const opts = {
    reply_markup: {
      inline_keyboard: [
        [{ text: 'Admin Commands', callback_data: 'help_admin' }],
        [{ text: 'Owner Commands', callback_data: 'help_owner' }],
        [{ text: 'User Commands', callback_data: 'help_user' }]
      ]
    }
  };
  try {
    await bot.sendMessage(msg.chat.id, messages.helpMenu.main, opts);
  } catch (error) {
    console.error('Error handling /help command:', error);
    await bot.sendMessage(msg.chat.id, 'An error occurred while processing the /help command.');
  }
}

module.exports = {
  handleStart,
  handleHelp
};
