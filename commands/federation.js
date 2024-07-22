const { Federation } = require('../db');
const messages = require('../messages');

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
    await federation.addMember(msg.chat.id);
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
    await federation.removeMember(msg.chat.id);
    await bot.sendMessage(msg.chat.id, `Successfully left federation with ID: ${fedId}`);
  } catch (error) {
    console.error('Error leaving federation:', error);
    await bot.sendMessage(msg.chat.id, 'Error leaving federation.');
  }
}

module.exports = {
  handleNewFed,
  handleMyFeds,
  handleJoinFed,
  handleLeaveFed
};
