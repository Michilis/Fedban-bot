const messages = {
  start: "Welcome to the Federation Bot! Use /help to see available commands.",
  help: `
Here are the available commands:

- /start - Show the welcome message
- /help - Show this help message
- /newfed <name> - Create a new federation
- /myfeds - List federations you own
- /joinfed <id> - Join a federation
- /leavefed <id> - Leave a federation
- /fedinfo <id> - Get information about a federation
- /fedadmins <id> - List federation admins
- /fpromote <id> - Promote a federation admin
- /fdemote <id> - Demote a federation admin
- /fban <id> - Ban a user from a federation
- /unfban <id> - Unban a user from a federation
  `,

  helpMenu: {
    main: `
Here are the available commands:

- /start - Show the welcome message
- /help - Show this help message
- /newfed <name> - Create a new federation
- /myfeds - List federations you own
- /joinfed <id> - Join a federation
- /leavefed <id> - Leave a federation
- /fedinfo <id> - Get information about a federation
- /fedadmins <id> - List federation admins
- /fpromote <id> - Promote a federation admin
- /fdemote <id> - Demote a federation admin
- /fban <id> - Ban a user from a federation
- /unfban <id> - Unban a user from a federation
    `,
    admin: `
Admin Commands:
- /fpromote <id> - Promote a federation admin
- /fdemote <id> - Demote a federation admin
- /fban <id> - Ban a user from a federation
- /unfban <id> - Unban a user from a federation
    `,
    owner: `
Owner Commands:
- /newfed <name> - Create a new federation
- /renamefed <id> <newname> - Rename your federation
- /delfed <id> - Delete your federation
- /fedtransfer <id> <newowner> - Transfer federation ownership
    `,
    user: `
User Commands:
- /joinfed <id> - Join a federation
- /leavefed <id> - Leave a federation
- /fedinfo <id> - Get information about a federation
- /fedadmins <id> - List federation admins
    `
  }
};

module.exports = messages;
