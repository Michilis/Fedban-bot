const { Model, DataTypes } = require('sequelize');
const sequelize = require('../database');

class Chat extends Model {}

Chat.init({
  id: {
    type: DataTypes.BIGINT,
    primaryKey: true,
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  federationId: {
    type: DataTypes.UUID,
    allowNull: true,
  },
}, {
  sequelize,
  modelName: 'Chat',
});

module.exports = Chat;
