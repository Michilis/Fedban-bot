def extract_user(message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    return user_id

def extract_user_and_reason(message):
    user_id, reason = None, None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if len(message.command) > 2:
        reason = ' '.join(message.command[2:])
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            reason = ' '.join(message.command[1:])
    return user_id, reason
