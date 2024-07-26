MESSAGES = {
    "create_fed_private": "Federations can only be created by privately messaging me.",
    "provide_fed_name": "Please write the name of the federation!",
    "new_fed_created": "New federation created!\nName: {fed_name}\nID: {fed_id}",
    "delete_fed_private": "Federations can only be deleted by privately messaging me.",
    "provide_fed_id": "Please provide the federation ID.",
    "fed_does_not_exist": "This federation does not exist.",
    "only_fed_owners_can_delete": "Only federation owners can delete federations.",
    "fed_deleted": "Federation {fed_name} deleted.",
    "transfer_fed_private": "Federations can only be transferred by privately messaging me.",
    "transfer_fed_usage": "Usage: /fedtransfer @username fed_id",
    "only_fed_owners_can_transfer": "Only federation owners can transfer federations.",
    "fed_transferred": "Federation {fed_name} transferred to {user_id}.",
    "no_federations_created": "You haven't created any federations.",
    "your_federations": "Your federations:\n{fed_list}",
    "rename_fed_usage": "Usage: /renamefed fed_id new_name",
    "only_fed_owners_can_rename": "Only federation owners can rename federations.",
    "fed_renamed": "Federation renamed to {new_name}.",
    "set_unset_fed_log_private": "Usage:\n\n /{command} [channel_id] [fed_id].",
    "only_fed_owners_can_set_unset_log": "Only federation owners can set/unset log channels.",
    "log_channel_set": "Log channel set.",
    "log_channel_unset": "Log channel unset.",
    "chat_fed_private": "This command is specific to groups.",
    "group_not_in_federation": "This group is not in any federation.",
    "group_in_federation": "This group is part of the federation:\nName: {fed_name}\nID: {fed_id}",
    "join_fed_private": "This command is specific to groups.",
    "provide_fed_id_join": "Please provide the federation ID.",
    "only_group_admins_can_join": "Only group admins can join federations.",
    "group_joined_federation": "This group has joined the federation: {fed_name}.",
    "leave_fed_private": "This command is specific to groups.",
    "only_group_admins_can_leave": "Only group admins can leave federations.",
    "group_left_federation": "This group has left the federation: {fed_name}.",
    "fedchats_private": "Fedchats can only be checked by privately messaging me.",
    "provide_fed_id_fedchats": "Please provide the federation ID.",
    "only_fed_admins_can_check_fedchats": "You need to be a Fed Admin to use this command.",
    "fed_chats_list": "Chats in the federation {fed_name}:\n{chat_list}",
    "fed_info_list": "**Federation Information:**\nName: {fed_name}\nOwner: {owner_mention}\nAdmins: {admins}\nBanned Users: {banned_users}\nChats: {chats}",
    "fed_admins_list": "**Federation Admins:**\nOwner: {owner_mention}\n{admins_list}",
    "fpromote_private": "This command is specific to groups.",
    "only_fed_owners_can_promote": "Only federation owners can promote admins.",
    "user_promoted": "User promoted to federation admin.",
    "fdemote_private": "This command is specific to groups.",
    "only_fed_owners_can_demote": "Only federation owners can demote admins.",
    "user_demoted": "User demoted from federation admin.",
    "fban_private": "This command is specific to groups.",
    "only_fed_admins_can_ban": "Only federation owners and admins can ban users.",
    "user_banned": "User has been banned in the federation.",
    "unfban_private": "This command is specific to groups.",
    "only_fed_admins_can_unban": "Only federation owners and admins can unban users.",
    "user_unbanned": "User has been unbanned in the federation.",
    "fedstat_private": "Federation Ban status can only be checked by privately messaging me.",
    "user_fed_status": "**Here is the list of federations that {user} were banned in:**\n\n{status_list}",
    "user_not_banned": "**{user} is not banned in any federations.**",
    "fbroadcast_private": "This command is specific to groups.",
    "reply_to_broadcast": "You need to reply to a message to broadcast it.",
    "only_fed_admins_can_broadcast": "Only federation owners and admins can broadcast messages.",
    "broadcast_in_progress": "Broadcast in progress, will take {seconds} seconds.",
    "broadcast_done": "Broadcasted message in {count} chats.",
    "start_message": "Welcome to the Fedban Bot! Use /fedhelp to see the available commands.",
    "help_menu": (
        "Federations\n\n"
        "Ah, group management. It's all fun and games, until you start getting spammers in, and you need to ban them. "
        "Then you need to start banning more, and more, and it gets painful. "
        "But then you have multiple groups, and you don't want these spammers in any of your groups - how can you deal? "
        "Do you have to ban them manually, in all your groups?\n\n"
        "No more! With federations, you can make a ban in one chat overlap to all your other chats. "
        "You can even appoint federation admins, so that your trustworthiest admins can ban across all the chats that you want to protect."
    ),
    "fed_admin_commands": (
        "Fed Admin Commands\n\n"
        "The following is the list of all fed admin commands. To run these, you have to be a federation admin in the current federation.\n\n"
        "Commands:\n"
        "- /fban: Bans a user from the current chat's federation\n"
        "- /unfban: Unbans a user from the current chat's federation\n"
        "- /feddemoteme <fedID>: Demote yourself from a fed.\n"
        "- /myfeds: List all feds you are an admin in.\n"
    ),
    "fed_owner_commands": (
        "Federation Owner Commands\n\n"
        "These are the list of available fed owner commands. To run these, you have to own the current federation.\n\n"
        "Owner Commands:\n"
        "- /newfed <fedname>: Creates a new federation with the given name. Only one federation per user.\n"
        "- /renamefed <fedname>: Rename your federation.\n"
        "- /delfed: Deletes your federation, and any information related to it. Will not unban any banned users.\n"
        "- /fedtransfer <reply/username/mention/userid>: Transfer your federation to another user.\n"
        "- /fedpromote: Promote a user to fedadmin in your fed. To avoid unwanted fedadmin, the user will get a message to confirm this.\n"
        "- /feddemote: Demote a federation admin in your fed.\n"
        "- /fednotif <yes/no/on/off>: Whether or not to receive PM notifications of every fed action.\n"
        "- /fedreason <yes/no/on/off>: Whether or not fedbans should require a reason.\n"
        "- /subfed <FedId>: Subscribe your federation to another. Users banned in the subscribed fed will also be banned in this one.\n"
        "  Note: This does not affect your banlist. You just inherit any bans.\n"
        "- /unsubfed <FedId>: Unsubscribes your federation from another. Bans from the other fed will no longer take effect.\n"
        "- /fedexport <csv/minicsv/json/human>: Get the list of currently banned users. Default output is CSV.\n"
        "- /fedimport <overwrite/keep> <csv/minicsv/json/human>: Import a list of banned users.\n"
        "- /setfedlog: Sets the current chat as the federation log. All federation events will be logged here.\n"
        "- /unsetfedlog: Unset the federation log. Events will no longer be logged.\n"
        "- /setfedlang: Change the language of the federation log. Note: This does not change the language of Rose's replies to fed commands, only the log channel.\n"
    ),
    "user_commands": (
        "User Commands\n\n"
        "These commands do not require you to be admin of a federation. These commands are for general commands, such as looking up information on a fed, or checking a user's fbans.\n\n"
        "Commands:\n"
        "- /fedinfo <FedID>: Information about a federation.\n"
        "- /fedadmins <FedID>: List the admins in a federation.\n"
        "- /fedsubs <FedID>: List all federations your federation is subscribed to.\n"
        "- /joinfed <FedID>: Join the current chat to a federation. A chat can only join one federation. Chat owners only.\n"
        "- /leavefed: Leave the current federation. Only chat owners can do this.\n"
        "- /fedstat: List all the federations that you have been banned in.\n"
        "- /fedstat <user ID>: List all the federations that a user has been banned in.\n"
        "- /fedstat <FedID>: Gives information about your ban in a federation.\n"
        "- /fedstat <user ID> <FedID>: Gives information about a user's ban in a federation.\n"
        "- /chatfed: Information about the federation the current chat is in.\n"
        "- /quietfed <yes/no/on/off>: Whether or not to send ban notifications when fedbanned users join the chat.\n"
    ),
}
