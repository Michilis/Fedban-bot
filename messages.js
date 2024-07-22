module.exports = {
  helpMain: `
    **Federations**

    Ah, group management. It's all fun and games, until you start getting spammers in, and you need to ban them. Then you need to start banning more, and more, and it gets painful.
    But then you have multiple groups, and you don't want these spammers in any of your groups - how can you deal? Do you have to ban them manually, in all your groups?

    No more! With federations, you can make a ban in one chat overlap to all your other chats.
    You can even appoint federation admins, so that your trustworthiest admins can ban across all the chats that you want to protect.

    **Use the buttons below to navigate through the commands.**
  `,

  helpFedAdminCommands: `
    **Fed Admin Commands**

    The following is the list of all fed admin commands. To run these, you have to be a federation admin in the current federation.

    Commands:
    - /fban: Bans a user from the current chat's federation
    - /unfban: Unbans a user from the current chat's federation
    - /feddemoteme <fedID>: Demote yourself from a fed.
    - /myfeds: List all feds you are an admin in.
  `,

  helpFedOwnerCommands: `
    **Federation Owner Commands**

    These are the list of available fed owner commands. To run these, you have to own the current federation.

    Owner Commands:
    - /newfed <fedname>: Creates a new federation with the given name. Only one federation per user.
    - /renamefed <fedname>: Rename your federation.
    - /delfed: Deletes your federation, and any information related to it. Will not unban any banned users.
    - /fedtransfer <reply/username/mention/userid>: Transfer your federation to another user.
    - /fedpromote: Promote a user to fedadmin in your fed. To avoid unwanted fedadmin, the user will get a message to confirm this.
    - /feddemote: Demote a federation admin in your fed.
    - /fednotif <yes/no/on/off>: Whether or not to receive PM notifications of every fed action.
    - /fedreason <yes/no/on/off>: Whether or not fedbans should require a reason.
    - /subfed <FedId>: Subscribe your federation to another. Users banned in the subscribed fed will also be banned in this one.
      Note: This does not affect your banlist. You just inherit any bans.
    - /unsubfed <FedId>: Unsubscribes your federation from another. Bans from the other fed will no longer take effect.
    - /fedexport <csv/minicsv/json/human>: Get the list of currently banned users. Default output is CSV.
    - /fedimport <overwrite/keep> <csv/minicsv/json/human>: Import a list of banned users.
    - /setfedlog: Sets the current chat as the federation log. All federation events will be logged here.
    - /unsetfedlog: Unset the federation log. Events will no longer be logged.
    - /setfedlang: Change the language of the federation log. Note: This does not change the language of Rose's replies to fed commands, only the log channel.
  `,

  helpUserCommands: `
    **User Commands**

    These commands do not require you to be admin of a federation. These commands are for general commands, such as looking up information on a fed, or checking a user's fbans.

    Commands:
    - /fedinfo <FedID>: Information about a federation.
    - /fedadmins <FedID>: List the admins in a federation.
    - /fedsubs <FedID>: List all federations your federation is subscribed to.
    - /joinfed <FedID>: Join the current chat to a federation. A chat can only join one federation. Chat owners only.
    - /leavefed: Leave the current federation. Only chat owners can do this.
    - /fedstat: List all the federations that you have been banned in.
    - /fedstat <user ID>: List all the federations that a user has been banned in.
    - /fedstat <FedID>: Gives information about your ban in a federation.
    - /fedstat <user ID> <FedID>: Gives information about a user's ban in a federation.
    - /chatfed: Information about the federation the current chat is in.
    - /quietfed <yes/no/on/off>: Whether or not to send ban notifications when fedbanned users join the chat.
  `,

  startMessage: `
    Welcome to the Federation Ban Bot!
    Use /help to see the list of available commands.
  `
};
