const messages = require('../messages');

async function handleHelpCallback(bot, message) {
  if (message.chat.type !== 'private') {
    await bot.sendMessage(message.chat.id, 'The help command is only available in direct messages with the bot.');
    return;
  }

  const opts = {
    chat_id: message.chat.id,
    message_id: message.message_id,
    reply_markup: {
      inline_keyboard: [
        [{ text: 'Admin Commands', callback_data: 'help_admin' }],
        [{ text: 'Owner Commands', callback_data: 'help_owner' }],
        [{ text: 'User Commands', callback_data: 'help_user' }]
      ]
    }
  };
  try {
    await bot.editMessageText(messages.helpMenu.main, opts);
  } catch (error) {
    console.error('Error handling help callback:', error);
    await bot.sendMessage(message.chat.id, 'An error occurred while processing the help command.');
  }
}

async function handleHelpSectionCallback(bot, message, section) {
  if (message.chat.type !== 'private') {
    await bot.sendMessage(message.chat.id, 'The help command is only available in direct messages with the bot.');
    return;
  }

  const sectionMessage = messages.helpMenu[section];
  const opts = {
    chat_id: message.chat.id,
    message_id: message.message_id,
    reply_markup: {
      inline_keyboard: [
        [{ text: 'Back', callback_data: 'help' }]
      ]
    }
  };
  try {
    await bot.editMessageText(sectionMessage, opts);
  } catch (error) {
    console.error('Error handling help section callback:', error);
    await bot.sendMessage(message.chat.id, 'An error occurred while processing the help command.');
  }
}

module.exports = {
  handleHelpCallback,
  handleHelpSectionCallback
};
