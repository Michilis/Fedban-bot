const { Federation, Member } = require('./db'); // Assuming Member model exists
const messages = require('./messages'); // Assuming messages.js contains message strings

async function handleCommands(bot, msg) {
  const text = msg.text;
  if (!text) {
    return;
  }

  const command = text.split(' ')[0];
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
    case '/joinfed':
      await handleJoinFed(bot, msg);
      break;
    case '/leavefed':
      await handleLeaveFed(bot, msg);
      break;
    default:
      await bot.sendMessage(msg.chat.id, 'Unknown command. Type /help for a list of commands.');
  }
}

async function handleStart(bot, msg) {
  await bot.sendMessage(msg.chat.id, 'Welcome to the Federation Bot!');
}

async function handleHelp(bot, msg) {
  if (msg.chat.type !== 'private') {
    await bot.sendMessage(msg.chat.id, 'The /help command is only available in direct messages with the bot.');
    return;
  }

  const opts = {
    reply_markup: {
      inline_keyboard: [
        [{ text: 'Admin Commands', callback_data: 'help_admin' }],
        [{ text: 'Owner Commands', callback_data: 'help_owner' }],
        [{ text: 'User Commands', callback_data: 'help_user' }]
      ]
    }
  };
  await bot.sendMessage(msg.chat.id, 'Help Menu:', opts);
}

async function handleNewFed(bot, msg) {
  const args = msg.text.split(' ').slice(1);
  if (args.length === 0) {
    await bot.sendMessage(msg.chat.id, 'Please provide a name for the new federation.');
    return;
  }
  const name = args.join(' ');
  try {
    const federation = await Federation.create({ name, ownerId: msg.from.id });
    await bot.sendMessage(msg.chat.id, `Federation created with ID: ${federation.id}`);
  } catch (error) {
    console.error('Error creating federation:', error);
    await bot.sendMessage(msg.chat.id, 'Error creating federation.');
  }
}

async function handleMyFeds(bot, msg) {
  try {
    const federations = await Federation.findAll({ where: { ownerId: msg.from.id } });
    if (federations.length === 0) {
      await bot.sendMessage(msg.chat.id, 'You do not own any federations.');
    } else {
      const federationList = federations.map(fed => `ID: ${fed.id}, Name: ${fed.name}`).join('\n');
      await bot.sendMessage(msg.chat.id, `Your federations:\n${federationList}`);
    }
  } catch (error) {
    console.error('Error fetching federations:', error);
    await bot.sendMessage(msg.chat.id, 'Error fetching federations.');
  }
}

async function handleJoinFed(bot, msg) {
  const args = msg.text.split(' ').slice(1);
  if (args.length === 0) {
    await bot.sendMessage(msg.chat.id, 'Please provide the ID of the federation you want to join.');
    return;
  }
  const fedId = args[0];
  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    if (!federation) {
      await bot.sendMessage(msg.chat.id, 'Federation not found.');
      return;
    }
    await Member.upsert({ chatId: msg.chat.id, federationId: fedId });
    await bot.sendMessage(msg.chat.id, `Successfully joined federation with ID: ${fedId}`);
  } catch (error) {
    console.error('Error joining federation:', error);
    await bot.sendMessage(msg.chat.id, 'Error joining federation.');
  }
}

async function handleLeaveFed(bot, msg) {
  const args = msg.text.split(' ').slice(1);
  if (args.length === 0) {
    await bot.sendMessage(msg.chat.id, 'Please provide the ID of the federation you want to leave.');
    return;
  }
  const fedId = args[0];
  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    if (!federation) {
      await bot.sendMessage(msg.chat.id, 'Federation not found.');
      return;
    }
    await Member.destroy({ where: { chatId: msg.chat.id, federationId: fedId } });
    await bot.sendMessage(msg.chat.id, `Successfully left federation with ID: ${fedId}`);
  } catch (error) {
    console.error('Error leaving federation:', error);
    await bot.sendMessage(msg.chat.id, 'Error leaving federation.');
  }
}

module.exports = {
  handleCommands,
  handleStart,
  handleHelp,
  handleNewFed,
  handleMyFeds,
  handleJoinFed,
  handleLeaveFed
};
