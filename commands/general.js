const messages = require('../messages');

async function handleStart(bot, msg) {
  await bot.sendMessage(msg.chat.id, messages.start);
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
  await bot.sendMessage(msg.chat.id, messages.helpMenu.main, opts);
}

module.exports = {
  handleStart,
  handleHelp
};
