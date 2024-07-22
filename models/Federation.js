const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Federation = sequelize.define('Federation', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    ownerId: {
      type: DataTypes.BIGINT,
      allowNull: false,
    },
    logChannelId: {
      type: DataTypes.STRING,
      allowNull: true,
    },
  });

  return Federation;
};
