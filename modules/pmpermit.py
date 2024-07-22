from pyrogram import filters

from wbb import (
    BOT_ID,
    PM_PERMIT,
    app,
    eor,
)
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    approve_pmpermit,
    disapprove_pmpermit,
    is_pmpermit_approved,
)

flood = {}

@app.on_message(
    filters.private
    & filters.incoming
    & ~filters.service
    & ~filters.bot
)
@capture_err
async def pmpermit_func(_, message):
    user_id = message.from_user.id
    if not PM_PERMIT or await is_pmpermit_approved(user_id):
        return
    if str(user_id) in flood:
        flood[str(user_id)] += 1
    else:
        flood[str(user_id)] = 1
    if flood[str(user_id)] > 5:
        await message.reply_text("SPAM DETECTED, BLOCKED USER AUTOMATICALLY!")
        return await app.block_user(user_id)
    results = await app.get_inline_bot_results(BOT_ID, f"pmpermit {user_id}")
    await app.send_inline_bot_result(
        user_id,
        results.query_id,
        results.results[0].id,
    )

@app.on_message(
    filters.command("approve")
)
@capture_err
async def pm_approve(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Reply to a user's message to approve.")
    user_id = message.reply_to_message.from_user.id
    if await is_pmpermit_approved(user_id):
        return await eor(message, text="User is already approved to pm")
    await approve_pmpermit(user_id)
    await eor(message, text="User is approved to pm")

@app.on_message(
    filters.command("disapprove")
)
async def pm_disapprove(_, message):
    if not message.reply_to_message:
        return await eor(
            message, text="Reply to a user's message to disapprove."
        )
    user_id = message.reply_to_message.from_user.id
    if not await is_pmpermit_approved(user_id):
        await eor(message, text="User is already disapproved to pm")
        return
    await disapprove_pmpermit(user_id)
    await eor(message, text="User is disapproved to pm")

@app.on_message(
    filters.command("block")
)
@capture_err
async def block_user_func(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Reply to a user's message to block.")
    user_id = message.reply_to_message.from_user.id
    await eor(message, text="Successfully blocked the user")
    await app.block_user(user_id)

@app.on_message(
    filters.command("unblock")
)
async def unblock_user_func(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Reply to a user's message to unblock.")
    user_id = message.reply_to_message.from_user.id
    await app.unblock_user(user_id)
    await eor(message, text="Successfully Unblocked the user")
