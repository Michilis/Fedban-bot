const messages = require('../messages');

async function handleHelpCallback(bot, message) {
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
    await bot.sendMessage(message.chat.id, messages.helpMenu.main, opts);
  } catch (error) {
    console.error('Error handling help callback:', error);
    await bot.sendMessage(message.chat.id, 'An error occurred while processing the help command.');
  }
}

async function handleHelpSectionCallback(bot, message, section) {
  try {
    await bot.sendMessage(message.chat.id, messages.helpMenu[section]);
  } catch (error) {
    console.error('Error handling help section callback:', error);
    await bot.sendMessage(message.chat.id, 'An error occurred while processing the help command.');
  }
}

module.exports = {
  handleHelpCallback,
  handleHelpSectionCallback
};
