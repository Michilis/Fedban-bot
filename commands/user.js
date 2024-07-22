async function handleStart(bot, msg) {
  const chatId = msg.chat.id;
  await bot.sendMessage(chatId, 'Welcome! Use /help to see available commands.');
}

async function handleHelp(bot, msg) {
  const chatId = msg.chat.id;
  await bot.sendMessage(chatId, `
    Available Commands:
    /start - Start the bot
    /help - Show this help message
    /newfed <name> - Create a new federation
    /myfeds - List federations you own
    /joinfed <id> - Join a federation
    /leavefed <id> - Leave a federation
    /fedinfo <id> - Get information about a federation
    /fedadmins <id> - List federation admins
    /fpromote <id> - Promote a federation admin
    /fdemote <id> - Demote a federation admin
    /fban <id> - Ban a user from a federation
    /unfban <id> - Unban a user from a federation
  `);
}

module.exports = {
  handleStart,
  handleHelp,
};
