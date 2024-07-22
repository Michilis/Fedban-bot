const messages = require('../messages');
const { handleHelpCallback, handleHelpSectionCallback } = require('./callbacks');

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
  await bot.sendMessage(msg.chat.id, messages.helpMenu.main, opts);
}

async function handleHelpCallback(bot, message) {
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
  await bot.editMessageText(messages.helpMenu.main, opts);
}

async function handleHelpSectionCallback(bot, message, section) {
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
  await bot.editMessageText(sectionMessage, opts);
}

module.exports = {
  handleHelp,
  handleHelpCallback,
  handleHelpSectionCallback
};
