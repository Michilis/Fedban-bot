const { User, Federation, FederationAdmin, FederationBan, Chat, Log } = require('./db');
const { logGroupId } = require('./config');
const { v4: uuidv4 } = require('uuid');

// Extract user and reason utility function
async function extractUserAndReason(msg) {
  const parts = msg.text.split(' ');
  if (parts.length < 2) return [null, null];
  const userId = parseInt(parts[1].replace('@', ''), 10);
  const reason = parts.slice(2).join(' ');
  return [userId, reason];
}

// Command Handlers
async function handleNewFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const federationName = msg.text.split(' ').slice(1).join(' ').trim();

  if (!federationName) {
    return bot.sendMessage(chatId, 'Please provide a name for the federation.');
  }

  try {
    const newFederation = await Federation.create({
      name: federationName,
      ownerId: userId,
    });

    await User.upsert({ id: userId, username: msg.from.username });

    bot.sendMessage(chatId, `Federation "${federationName}" created with ID ${newFederation.id}`);
  } catch (error) {
    console.error('Error creating federation:', error);
    bot.sendMessage(chatId, 'Failed to create federation. Please try again later.');
  }
}

async function handleDelFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const args = msg.text.split(' ');
  if (args.length < 2) {
    return bot.sendMessage(chatId, 'Please provide the federation ID.');
  }
  const federationId = args[1].trim();

  try {
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    if (federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'Only the federation owner can delete the federation.');
    }
    await Federation.destroy({ where: { id: federationId } });
    bot.sendMessage(chatId, 'Federation deleted successfully.');
  } catch (error) {
    console.error('Error deleting federation:', error);
    bot.sendMessage(chatId, 'Failed to delete federation. Please try again later.');
  }
}

async function handleFedTransfer(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const args = msg.text.split(' ');
  if (args.length < 3) {
    return bot.sendMessage(chatId, 'Usage: /fedtransfer <user_id> <federation_id>');
  }
  const newOwnerId = parseInt(args[1], 10);
  const federationId = args[2].trim();

  try {
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    if (federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'Only the federation owner can transfer ownership.');
    }
    federation.ownerId = newOwnerId;
    await federation.save();
    bot.sendMessage(chatId, 'Federation ownership transferred successfully.');
  } catch (error) {
    console.error('Error transferring federation ownership:', error);
    bot.sendMessage(chatId, 'Failed to transfer ownership. Please try again later.');
  }
}

async function handleMyFeds(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const federations = await Federation.findAll({ where: { ownerId: userId } });
    if (federations.length === 0) {
      return bot.sendMessage(chatId, 'You have not created any federations.');
    }
    const responseText = federations.map(fed => `Name: ${fed.name}\nID: ${fed.id}`).join('\n\n');
    bot.sendMessage(chatId, `Your federations:\n\n${responseText}`);
  } catch (error) {
    console.error('Error retrieving federations:', error);
    bot.sendMessage(chatId, 'Failed to retrieve federations. Please try again later.');
  }
}

async function handleRenameFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const args = msg.text.split(' ');
  if (args.length < 3) {
    return bot.sendMessage(chatId, 'Usage: /renamefed <federation_id> <new_name>');
  }
  const federationId = args[1].trim();
  const newName = args.slice(2).join(' ');

  try {
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    if (federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'Only the federation owner can rename the federation.');
    }
    federation.name = newName;
    await federation.save();
    bot.sendMessage(chatId, `Federation renamed to "${newName}".`);
  } catch (error) {
    console.error('Error renaming federation:', error);
    bot.sendMessage(chatId, 'Failed to rename federation. Please try again later.');
  }
}

async function handleSetFedLog(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const args = msg.text.split(' ');
  if (args.length < 3) {
    return bot.sendMessage(chatId, 'Usage: /setfedlog <channel_id> <federation_id>');
  }
  const channelId = args[1].trim();
  const federationId = args[2].trim();

  try {
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    if (federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'Only the federation owner can set the log channel.');
    }
    federation.logChannelId = channelId;
    await federation.save();
    bot.sendMessage(chatId, 'Log channel set successfully.');
  } catch (error) {
    console.error('Error setting log channel:', error);
    bot.sendMessage(chatId, 'Failed to set log channel. Please try again later.');
  }
}

async function handleUnsetFedLog(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const args = msg.text.split(' ');
  if (args.length < 2) {
    return bot.sendMessage(chatId, 'Usage: /unsetfedlog <federation_id>');
  }
  const federationId = args[1].trim();

  try {
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    if (federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'Only the federation owner can unset the log channel.');
    }
    federation.logChannelId = null;
    await federation.save();
    bot.sendMessage(chatId, 'Log channel unset successfully.');
  } catch (error) {
    console.error('Error unsetting log channel:', error);
    bot.sendMessage(chatId, 'Failed to unset log channel. Please try again later.');
  }
}

async function handleJoinFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const args = msg.text.split(' ');
  if (args.length < 2) {
    return bot.sendMessage(chatId, 'Usage: /joinfed <federation_id>');
  }
  const federationId = args[1].trim();

  try {
    const chat = await Chat.findOne({ where: { id: chatId } });
    if (chat && chat.federationId) {
      return bot.sendMessage(chatId, 'This chat is already part of a federation.');
    }
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    await Chat.upsert({ id: chatId, title: msg.chat.title, federationId });
    bot.sendMessage(chatId, 'Chat joined federation successfully.');
  } catch (error) {
    console.error('Error joining federation:', error);
    bot.sendMessage(chatId, 'Failed to join federation. Please try again later.');
  }
}

async function handleLeaveFed(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const chat = await Chat.findOne({ where: { id: chatId } });
    if (!chat || !chat.federationId) {
      return bot.sendMessage(chatId, 'This chat is not part of any federation.');
    }
    const federation = await Federation.findOne({ where: { id: chat.federationId } });
    if (federation.ownerId !== userId) {
      return bot.sendMessage(chatId, 'Only the group owner can leave the federation.');
    }
    chat.federationId = null;
    await chat.save();
    bot.sendMessage(chatId, 'Chat left federation successfully.');
  } catch (error) {
    console.error('Error leaving federation:', error);
    bot.sendMessage(chatId, 'Failed to leave federation. Please try again later.');
  }
}

async function handleFedInfo(bot, msg) {
  const chatId = msg.chat.id;
  const args = msg.text.split(' ');
  if (args.length < 2) {
    return bot.sendMessage(chatId, 'Usage: /fedinfo <federation_id>');
  }
  const federationId = args[1].trim();

  try {
    const federation = await Federation.findOne({ where: { id: federationId } });
    if (!federation) {
      return bot.sendMessage(chatId, 'Federation not found.');
    }
    const responseText = `Federation Name: ${federation.name}\nOwner ID: ${federation.ownerId}`;
    bot.sendMessage(chatId, responseText);
  } catch (error) {
    console.error('Error retrieving federation info:', error);
    bot.sendMessage(chatId, 'Failed to retrieve federation info. Please try again later.');
  }
}

async function handleFedAdmins(bot, msg) {
  const chatId = msg.chat.id;
  const args = msg.text.split(' ');
  if (args.length < 2) {
    return bot.sendMessage(chatId, 'Usage: /fedadmins <federation_id>');
  }
  const federationId = args[1].trim();

  try {
    const admins = await FederationAdmin.findAll({ where: { federationId } });
    if (admins.length === 0) {
      return bot.sendMessage(chatId, 'No admins found for this federation.');
    }
    const responseText = admins.map(admin => `Admin ID: ${admin.userId}`).join('\n');
    bot.sendMessage(chatId, `Federation Admins:\n\n${responseText}`);
  } catch (error) {
    console.error('Error retrieving federation admins:', error);
    bot.sendMessage(chatId, 'Failed to retrieve federation admins. Please try again later.');
  }
}

async function handleFBan(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const [targetUserId, reason] = await extractUserAndReason(msg);
  if (!targetUserId || !reason) {
    return bot.sendMessage(chatId, 'Usage: /fban <user_id> <reason>');
  }

  try {
    const chat = await Chat.findOne({ where: { id: chatId } });
    if (!chat || !chat.federationId) {
      return bot.sendMessage(chatId, 'This chat is not part of any federation.');
    }
    const federation = await Federation.findOne({ where: { id: chat.federationId } });
    const isAdmin = await FederationAdmin.findOne({ where: { federationId: federation.id, userId } });
    if (federation.ownerId !== userId && !isAdmin) {
      return bot.sendMessage(chatId, 'Only federation admins can ban users.');
    }
    await FederationBan.upsert({ federationId: federation.id, userId: targetUserId, reason });
    bot.sendMessage(chatId, 'User banned federation-wide successfully.');
  } catch (error) {
    console.error('Error banning user:', error);
    bot.sendMessage(chatId, 'Failed to ban user. Please try again later.');
  }
}

async function handleUnFBan(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const [targetUserId, reason] = await extractUserAndReason(msg);
  if (!targetUserId || !reason) {
    return bot.sendMessage(chatId, 'Usage: /unfban <user_id> <reason>');
  }

  try {
    const chat = await Chat.findOne({ where: { id: chatId } });
    if (!chat || !chat.federationId) {
      return bot.sendMessage(chatId, 'This chat is not part of any federation.');
    }
    const federation = await Federation.findOne({ where: { id: chat.federationId } });
    const isAdmin = aw
