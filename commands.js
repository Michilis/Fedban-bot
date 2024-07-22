const { Federation } = require('./db');
const messages = require('./messages');
const { handleStart, handleHelp } = require('./commands/general');
const { handleNewFed, handleMyFeds, handleJoinFed, handleLeaveFed } = require('./commands/federation');
const { handleFPromote, handleFDemote, handleFBan, handleUnFBan } = require('./commands/admin');
const { handleHelpCallback, handleHelpSectionCallback } = require('./commands/help');

async function handleCommands(bot, msg) {
  const chatId = msg.chat.id;
  const text = msg.text ? msg.text.toLowerCase() : '';

  if (text.startsWith('/start')) {
    await handleStart(bot, msg);
  } else if (text.startsWith('/help')) {
    await handleHelp(bot, msg);
  } else if (text.startsWith('/newfed')) {
    await handleNewFed(bot, msg);
  } else if (text.startsWith('/myfeds')) {
    await handleMyFeds(bot, msg);
  } else if (text.startsWith('/joinfed')) {
    await handleJoinFed(bot, msg);
  } else if (text.startsWith('/leavefed')) {
    await handleLeaveFed(bot, msg);
  } else if (text.startsWith('/fpromote')) {
    await handleFPromote(bot, msg);
  } else if (text.startsWith('/fdemote')) {
    await handleFDemote(bot, msg);
  } else if (text.startsWith('/fban')) {
    await handleFBan(bot, msg);
  } else if (text.startsWith('/unfban')) {
    await handleUnFBan(bot, msg);
  } else {
    await bot.sendMessage(chatId, 'Unknown command. Type /help for a list of commands.');
  }
}

module.exports = {
  handleCommands,
  handleHelpCallback,
  handleHelpSectionCallback
};
