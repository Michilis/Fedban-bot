const { handleStart, handleHelp } = require('./general');
const { handleNewFed, handleMyFeds } = require('./federation');
const { handleFPromote, handleFDemote, handleFBan, handleUnFBan } = require('./admin');
const { handleHelpCallback, handleHelpSectionCallback } = require('./help');

async function handleCommands(bot, msg) {
  if (msg.text) {
    const command = msg.text.split(' ')[0].toLowerCase();
    
    switch (command) {
      case '/start':
        await handleStart(bot, msg);
        break;
      case '/help':
        await handleHelp(bot, msg);
        break;
      case '/newfed':
        await handleNewFed(bot, msg);
        break;
      case '/myfeds':
        await handleMyFeds(bot, msg);
        break;
      case '/fpromote':
        await handleFPromote(bot, msg);
        break;
      case '/fdemote':
        await handleFDemote(bot, msg);
        break;
      case '/fban':
        await handleFBan(bot, msg);
        break;
      case '/unfban':
        await handleUnFBan(bot, msg);
        break;
      default:
        await bot.sendMessage(msg.chat.id, 'Unknown command. Use /help to see the available commands.');
        break;
    }
  }
}

module.exports = {
  handleCommands,
  handleHelpCallback,
  handleHelpSectionCallback,
};
