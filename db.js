const { Sequelize, DataTypes } = require('sequelize');
const config = require('./config');

const sequelize = new Sequelize(config.databaseUrl, {
  dialect: 'postgres',
});

const User = sequelize.define('User', {
  id: { type: DataTypes.INTEGER, primaryKey: true },
  username: DataTypes.STRING,
});

const Federation = sequelize.define('Federation', {
  id: { type: DataTypes.UUID, primaryKey: true, defaultValue: Sequelize.UUIDV4 },
  name: DataTypes.STRING,
  ownerId: DataTypes.INTEGER,
});

const FederationAdmin = sequelize.define('FederationAdmin', {
  federationId: { type: DataTypes.UUID, references: { model: Federation, key: 'id' } },
  userId: { type: DataTypes.INTEGER, references: { model: User, key: 'id' } },
});

const FederationBan = sequelize.define('FederationBan', {
  federationId: { type: DataTypes.UUID, references: { model: Federation, key: 'id' } },
  userId: { type: DataTypes.INTEGER, references: { model: User, key: 'id' } },
  reason: DataTypes.STRING,
});

const Chat = sequelize.define('Chat', {
  id: { type: DataTypes.INTEGER, primaryKey: true },
  title: DataTypes.STRING,
  federationId: { type: DataTypes.UUID, references: { model: Federation, key: 'id' } },
});

const Log = sequelize.define('Log', {
  federationId: { type: DataTypes.UUID, references: { model: Federation, key: 'id' } },
  message: DataTypes.STRING,
});

sequelize.sync();

module.exports = { User, Federation, FederationAdmin, FederationBan, Chat, Log, sequelize };
