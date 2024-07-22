const { Sequelize, DataTypes } = require('sequelize');

// Set up the Sequelize instance
const sequelize = new Sequelize(process.env.DATABASE_URL, {
  dialect: 'postgres',
  logging: false,
});

// Define the User model
const User = sequelize.define('User', {
  id: {
    type: DataTypes.BIGINT,
    primaryKey: true,
  },
  username: {
    type: DataTypes.STRING,
    allowNull: false,
  },
}, {
  timestamps: true,
});

// Define the Federation model
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
    type: DataTypes.BIGINT,
    allowNull: true,
  },
}, {
  timestamps: true,
});

// Define the Chat model
const Chat = sequelize.define('Chat', {
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
  timestamps: true,
});

// Define the FederationAdmin model
const FederationAdmin = sequelize.define('FederationAdmin', {
  federationId: {
    type: DataTypes.UUID,
    allowNull: false,
    primaryKey: true,
  },
  userId: {
    type: DataTypes.BIGINT,
    allowNull: false,
    primaryKey: true,
  },
}, {
  timestamps: true,
});

// Define the FederationBan model
const FederationBan = sequelize.define('FederationBan', {
  federationId: {
    type: DataTypes.UUID,
    allowNull: false,
    primaryKey: true,
  },
  userId: {
    type: DataTypes.BIGINT,
    allowNull: false,
    primaryKey: true,
  },
  reason: {
    type: DataTypes.TEXT,
    allowNull: true,
  },
}, {
  timestamps: true,
});

// Sync all models
sequelize.sync().then(() => {
  console.log('Database & tables created!');
}).catch(err => {
  console.error('Error creating database:', err);
});

module.exports = {
  sequelize,
  User,
  Federation,
  Chat,
  FederationAdmin,
  FederationBan,
};
