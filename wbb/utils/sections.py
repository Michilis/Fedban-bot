def section(title, body):
    msg = f"**{title}**\n"
    for key, value in body.items():
        msg += f"**{key}**: {' '.join(value)}\n"
    return msg
