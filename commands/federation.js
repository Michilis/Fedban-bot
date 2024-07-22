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

// Implement other federation commands like handleJoinFed, handleLeaveFed, handleFedInfo, handleFedAdmins similarly

module.exports = {
  handleNewFed,
  handleMyFeds,
  // Export other handlers like handleJoinFed, handleLeaveFed, handleFedInfo, handleFedAdmins
};
