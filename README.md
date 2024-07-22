# Fedban Bot

Fedban Bot is a Telegram bot designed to manage federations of groups, enabling efficient and centralized management of bans and admin promotions across multiple groups.

## Features

- Federation Management
- User Management
- Information Retrieval

## Commands

### Federation Management Commands

- /newfed <fedname>
- /joinfed <FedID>
- /leavefed <FedID>
- /renamefed <FedID> <newname>
- /fedtransfer <user> <FedID>
- /delfed <FedID>
- /setfedlog <channel_id> <FedID>
- /unsetfedlog <FedID>

### User Management Commands

- /fpromote <user>
- /fdemote <user>
- /fban <user> <reason>
- /sfban <user> <reason>
- /unfban <user> <reason>
- /sunfban <user> <reason>

### Information Retrieval Commands

- /fedinfo <FedID>
- /fedadmins <FedID>
- /fedchats <FedID>
- /fedstat
- /fedstat <userID>
- /fedstat <FedID>
- /fedstat <userID> <FedID>
- /chatfed
- /fbroadcast
