const { Sequelize, DataTypes } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(process.env.DATABASE_URL, {
  dialect: 'postgres',
  logging: false,
});

const Federation = sequelize.define('Federation', {
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  ownerId: {
    type: DataTypes.INTEGER,
    allowNull: false
  }
});

const Member = sequelize.define('Member', {
  chatId: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  federationId: {
    type: DataTypes.INTEGER,
    allowNull: false
  }
});

Federation.hasMany(Member, { as: 'members', foreignKey: 'federationId' });
Member.belongsTo(Federation, { foreignKey: 'federationId' });

async function connectDb() {
  await sequelize.authenticate();
  await sequelize.sync({ force: false });
  console.log('Database connected.');
}

module.exports = {
  connectDb,
  Federation,
  Member
};
