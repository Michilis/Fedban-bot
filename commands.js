const { User, Federation, Chat, FederationAdmin, FederationBan } = require('./db');
const messages = require('./messages');

// Handle /start command
async function handleStart(bot, msg) {
  const chatId = msg.chat.id;
  await bot.sendMessage(chatId, messages.startMessage);
}

// Handle /help command
async function handleHelp(bot, msg) {
  const chatId = msg.chat.id;
  await bot.sendMessage(chatId, messages.helpMessage, {
    reply_markup: {
      inline_keyboard: [
        [{ text: 'Federations', callback_data: 'help_federations' }],
        [{ text: 'Fed Admin Commands', callback_data: 'help_fed_admin_commands' }],
        [{ text: 'Federation Owner Commands', callback_data: 'help_federation_owner_commands' }],
        [{ text: 'User Commands', callback_data: 'help_user_commands' }],
      ],
    },
  });
}

// Handle callback queries for help menu
async function handleHelpCallback(bot, query) {
  const chatId = query.message.chat.id;
  const messageId = query.message.message_id;
  let responseText;

  switch (query.data) {
    case 'help_federations':
      responseText = messages.federationsHelp;
      break;
    case 'help_fed_admin_commands':
      responseText = messages.fedAdminCommandsHelp;
      break;
    case 'help_federation_owner_commands':
      responseText = messages.federationOwnerCommandsHelp;
      break;
    case 'help_user_commands':
      responseText = messages.userCommandsHelp;
      break;
    default:
      responseText = messages.helpMessage;
  }

  await bot.editMessageText(responseText, {
    chat_id: chatId,
    message_id: messageId,
    reply_markup: {
      inline_keyboard: [
        [{ text: 'Back', callback_data: 'help_back' }],
      ],
    },
  });
}

// Handle /newfed command
async function handleNewFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'private') {
    return bot.sendMessage(chatId, 'Please create federations via private message.');
  }

  const fedName = msg.text.split(' ').slice(1).join(' ');
  if (!fedName) {
    return bot.sendMessage(chatId, 'Please provide a name for the federation.');
  }

  try {
    const federation = await Federation.create({
      name: fedName,
      ownerId: userId,
    });

    await bot.sendMessage(chatId, `Federation created successfully!\n\nName: ${federation.name}\nID: ${federation.id}`);
  } catch (error) {
    console.error('Error creating federation:', error);
    await bot.sendMessage(chatId, 'Failed to create federation. Please try again later.');
  }
}

// Handle /delfed command
async function handleDelFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'private') {
    return bot.sendMessage(chatId, 'Please delete federations via private message.');
  }

  const fedId = msg.text.split(' ')[1];
  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    await Federation.destroy({ where: { id: fedId } });
    await bot.sendMessage(chatId, 'Federation deleted successfully.');
  } catch (error) {
    console.error('Error deleting federation:', error);
    await bot.sendMessage(chatId, 'Failed to delete federation. Please try again later.');
  }
}

// Handle /fedtransfer command
async function handleFedTransfer(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'private') {
    return bot.sendMessage(chatId, 'Please transfer federations via private message.');
  }

  const [_, newOwnerUsername] = msg.text.split(' ');
  const newOwner = await bot.getChat(newOwnerUsername);

  if (!newOwner) {
    return bot.sendMessage(chatId, 'User not found.');
  }

  const fedId = msg.text.split(' ')[2];
  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    federation.ownerId = newOwner.id;
    await federation.save();

    await bot.sendMessage(chatId, `Federation ownership transferred to ${newOwner.username}.`);
  } catch (error) {
    console.error('Error transferring federation:', error);
    await bot.sendMessage(chatId, 'Failed to transfer federation. Please try again later.');
  }
}

// Handle /myfeds command
async function handleMyFeds(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const federations = await Federation.findAll({ where: { ownerId: userId } });
    if (federations.length === 0) {
      return bot.sendMessage(chatId, 'You have not created any federations.');
    }

    const response = federations.map(fed => `Name: ${fed.name}\nID: ${fed.id}`).join('\n\n');
    await bot.sendMessage(chatId, response);
  } catch (error) {
    console.error('Error fetching federations:', error);
    await bot.sendMessage(chatId, 'Failed to fetch federations. Please try again later.');
  }
}

// Handle /renamefed command
async function handleRenameFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'private') {
    return bot.sendMessage(chatId, 'Please rename federations via private message.');
  }

  const [fedId, ...newNameParts] = msg.text.split(' ').slice(1);
  const newName = newNameParts.join(' ');

  if (!fedId || !newName) {
    return bot.sendMessage(chatId, 'Please provide the federation ID and the new name.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    federation.name = newName;
    await federation.save();

    await bot.sendMessage(chatId, `Federation renamed successfully to ${newName}.`);
  } catch (error) {
    console.error('Error renaming federation:', error);
    await bot.sendMessage(chatId, 'Failed to rename federation. Please try again later.');
  }
}

// Handle /setfedlog command
async function handleSetFedLog(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'private') {
    return bot.sendMessage(chatId, 'Please set federation log via private message.');
  }

  const [fedId, logChannelId] = msg.text.split(' ').slice(1);

  if (!fedId || !logChannelId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID and the log channel ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    federation.logChannelId = logChannelId;
    await federation.save();

    await bot.sendMessage(chatId, `Federation log channel set to ${logChannelId}.`);
  } catch (error) {
    console.error('Error setting federation log:', error);
    await bot.sendMessage(chatId, 'Failed to set federation log. Please try again later.');
  }
}

// Handle /unsetfedlog command
async function handleUnsetFedLog(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'private') {
    return bot.sendMessage(chatId, 'Please unset federation log via private message.');
  }

  const fedId = msg.text.split(' ')[1];

  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    federation.logChannelId = null;
    await federation.save();

    await bot.sendMessage(chatId, 'Federation log channel unset.');
  } catch (error) {
    console.error('Error unsetting federation log:', error);
    await bot.sendMessage(chatId, 'Failed to unset federation log. Please try again later.');
  }
}

// Handle /joinfed command
async function handleJoinFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'supergroup') {
    return bot.sendMessage(chatId, 'Only supergroups can join federations.');
  }

  const fedId = msg.text.split(' ')[1];
  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }

    const chatMember = await bot.getChatMember(chatId, userId);
    if (chatMember.status !== 'creator') {
      return bot.sendMessage(chatId, 'Only the group creator can join the federation.');
    }

    await Chat.upsert({ id: chatId, title: msg.chat.title, federationId: fedId });
    await bot.sendMessage(chatId, `Successfully joined the "${federation.name}" federation!`);
  } catch (error) {
    console.error('Error joining federation:', error);
    await bot.sendMessage(chatId, 'Failed to join federation. Please try again later.');
  }
}

// Handle /leavefed command
async function handleLeaveFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (msg.chat.type !== 'supergroup') {
    return bot.sendMessage(chatId, 'Only supergroups can leave federations.');
  }

  const fedId = msg.text.split(' ')[1];
  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const chatMember = await bot.getChatMember(chatId, userId);
    if (chatMember.status !== 'creator') {
      return bot.sendMessage(chatId, 'Only the group creator can leave the federation.');
    }

    const chat = await Chat.findOne({ where: { id: chatId, federationId: fedId } });
    if (!chat) {
      return bot.sendMessage(chatId, 'This chat is not part of the specified federation.');
    }

    await chat.destroy();
    await bot.sendMessage(chatId, 'Successfully left the federation.');
  } catch (error) {
    console.error('Error leaving federation:', error);
    await bot.sendMessage(chatId, 'Failed to leave federation. Please try again later.');
  }
}

// Handle /fedinfo command
async function handleFedInfo(bot, msg) {
  const chatId = msg.chat.id;

  const fedId = msg.text.split(' ')[1];
  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }

    const chats = await Chat.findAll({ where: { federationId: fedId } });
    const response = `
      Federation info:
      Name: ${federation.name}
      ID: ${federation.id}
      Chats in the federation: ${chats.length}
    `;
    await bot.sendMessage(chatId, response);
  } catch (error) {
    console.error('Error fetching federation info:', error);
    await bot.sendMessage(chatId, 'Failed to fetch federation info. Please try again later.');
  }
}

// Handle /fedadmins command
async function handleFedAdmins(bot, msg) {
  const chatId = msg.chat.id;

  const fedId = msg.text.split(' ')[1];
  if (!fedId) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }

    const admins = await FederationAdmin.findAll({ where: { federationId: fedId } });
    const adminUserIds = admins.map(admin => admin.userId);
    const adminUsers = await Promise.all(adminUserIds.map(id => bot.getChat(id)));
    const response = adminUsers.map(user => user.username).join('\n');
    await bot.sendMessage(chatId, `Federation Admins:\n${response}`);
  } catch (error) {
    console.error('Error fetching federation admins:', error);
    await bot.sendMessage(chatId, 'Failed to fetch federation admins. Please try again later.');
  }
}

// Handle /fpromote command
async function handleFPromote(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  const [_, username] = msg.text.split(' ');
  const user = await bot.getChat(username);

  if (!user) {
    return bot.sendMessage(chatId, 'User not found.');
  }

  const fedId = await getFedIdFromChat(chatId);
  if (!fedId) {
    return bot.sendMessage(chatId, 'This chat is not part of any federation.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    await FederationAdmin.create({ federationId: fedId, userId: user.id });
    await bot.sendMessage(chatId, `Successfully promoted ${user.username} to federation admin.`);
  } catch (error) {
    console.error('Error promoting federation admin:', error);
    await bot.sendMessage(chatId, 'Failed to promote federation admin. Please try again later.');
  }
}

// Handle /fdemote command
async function handleFDemote(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  const [_, username] = msg.text.split(' ');
  const user = await bot.getChat(username);

  if (!user) {
    return bot.sendMessage(chatId, 'User not found.');
  }

  const fedId = await getFedIdFromChat(chatId);
  if (!fedId) {
    return bot.sendMessage(chatId, 'This chat is not part of any federation.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId, ownerId: userId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found or you are not the owner.');
    }

    await FederationAdmin.destroy({ where: { federationId: fedId, userId: user.id } });
    await bot.sendMessage(chatId, `Successfully demoted ${user.username} from federation admin.`);
  } catch (error) {
    console.error('Error demoting federation admin:', error);
    await bot.sendMessage(chatId, 'Failed to demote federation admin. Please try again later.');
  }
}

// Handle /fban command
async function handleFBan(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  const [_, username, ...reasonParts] = msg.text.split(' ');
  const user = await bot.getChat(username);
  const reason = reasonParts.join(' ') || 'No reason provided';

  if (!user) {
    return bot.sendMessage(chatId, 'User not found.');
  }

  const fedId = await getFedIdFromChat(chatId);
  if (!fedId) {
    return bot.sendMessage(chatId, 'This chat is not part of any federation.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    const admins = await FederationAdmin.findAll({ where: { federationId: fedId } });
    const isAdmin = admins.some(admin => admin.userId === userId);

    if (!isAdmin && federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'You are not an admin of this federation.');
    }

    await FederationBan.create({ federationId: fedId, userId: user.id, reason });
    const chats = await Chat.findAll({ where: { federationId: fedId } });

    for (const chat of chats) {
      try {
        await bot.kickChatMember(chat.id, user.id);
      } catch (err) {
        console.error(`Error banning user in chat ${chat.id}:`, err);
      }
    }

    await bot.sendMessage(chatId, `User ${user.username} banned from the federation for: ${reason}`);
  } catch (error) {
    console.error('Error banning user from federation:', error);
    await bot.sendMessage(chatId, 'Failed to ban user from federation. Please try again later.');
  }
}

// Handle /unfban command
async function handleUnFBan(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  const [_, username, ...reasonParts] = msg.text.split(' ');
  const user = await bot.getChat(username);
  const reason = reasonParts.join(' ') || 'No reason provided';

  if (!user) {
    return bot.sendMessage(chatId, 'User not found.');
  }

  const fedId = await getFedIdFromChat(chatId);
  if (!fedId) {
    return bot.sendMessage(chatId, 'This chat is not part of any federation.');
  }

  try {
    const federation = await Federation.findOne({ where: { id: fedId } });
    const admins = await FederationAdmin.findAll({ where: { federationId: fedId } });
    const isAdmin = admins.some(admin => admin.userId === userId);

    if (!isAdmin && federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'You are not an admin of this federation.');
    }

    await FederationBan.destroy({ where: { federationId: fedId, userId: user.id } });
    const chats = await Chat.findAll({ where: { federationId: fedId } });

    for (const chat of chats) {
      try {
        await bot.unbanChatMember(chat.id, user.id);
      } catch (err) {
        console.error(`Error unbanning user in chat ${chat.id}:`, err);
      }
    }

    await bot.sendMessage(chatId, `User ${user.username} unbanned from the federation.`);
  } catch (error) {
    console.error('Error unbanning user from federation:', error);
    await bot.sendMessage(chatId, 'Failed to unban user from federation. Please try again later.');
  }
}

async function handleCommands(bot, msg) {
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
    case '/delfed':
      await handleDelFed(bot, msg);
      break;
    case '/fedtransfer':
      await handleFedTransfer(bot, msg);
      break;
    case '/myfeds':
      await handleMyFeds(bot, msg);
      break;
    case '/renamefed':
      await handleRenameFed(bot, msg);
      break;
    case '/setfedlog':
      await handleSetFedLog(bot, msg);
      break;
    case '/unsetfedlog':
      await handleUnsetFedLog(bot, msg);
      break;
    case '/joinfed':
      await handleJoinFed(bot, msg);
      break;
    case '/leavefed':
      await handleLeaveFed(bot, msg);
      break;
    case '/fedinfo':
      await handleFedInfo(bot, msg);
      break;
    case '/fedadmins':
      await handleFedAdmins(bot, msg);
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
      await bot.sendMessage(msg.chat.id, 'Unknown command.');
  }
}

module.exports = {
  handleCommands,
  handleHelpCallback,
};
