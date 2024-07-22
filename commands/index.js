const federationCommands = require('./federation');
const userCommands = require('./user');
const adminCommands = require('./admin');

function handleCommands(bot, msg) {
  const command = msg.text.split(' ')[0].toLowerCase();

  switch (command) {
    case '/start':
      return userCommands.handleStart(bot, msg);
    case '/help':
      return userCommands.handleHelp(bot, msg);
    case '/newfed':
      return federationCommands.handleNewFed(bot, msg);
    case '/delfed':
      return federationCommands.handleDelFed(bot, msg);
    case '/fedtransfer':
      return federationCommands.handleFedTransfer(bot, msg);
    case '/myfeds':
      return federationCommands.handleMyFeds(bot, msg);
    case '/renamefed':
      return federationCommands.handleRenameFed(bot, msg);
    case '/setfedlog':
      return federationCommands.handleSetFedLog(bot, msg);
    case '/unsetfedlog':
      return federationCommands.handleUnsetFedLog(bot, msg);
    case '/joinfed':
      return federationCommands.handleJoinFed(bot, msg);
    case '/leavefed':
      return federationCommands.handleLeaveFed(bot, msg);
    case '/fedinfo':
      return federationCommands.handleFedInfo(bot, msg);
    case '/fedadmins':
      return federationCommands.handleFedAdmins(bot, msg);
    case '/fpromote':
      return adminCommands.handleFPromote(bot, msg);
    case '/fdemote':
      return adminCommands.handleFDemote(bot, msg);
    case '/fban':
      return adminCommands.handleFBan(bot, msg);
    case '/unfban':
      return adminCommands.handleUnFBan(bot, msg);
    default:
      return bot.sendMessage(msg.chat.id, 'Unknown command.');
  }
}

module.exports = {
  handleCommands,
};
