import re
from pyrogram import filters
from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.sections import section
from wbb.utils.dbfunctions import (
    alpha_to_int,
    get_karma,
    get_karmas,
    int_to_alpha,
    is_karma_on,
    karma_off,
    karma_on,
    update_karma,
)
from wbb.utils.filter_groups import karma_negative_group, karma_positive_group
from wbb.utils.functions import get_user_id_and_usernames

__MODULE__ = "Karma"
__HELP__ = """[UPVOTE] - Use upvote keywords like "+", "+1", "thanks", etc to upvote a message.
[DOWNVOTE] - Use downvote keywords like "-", "-1", etc to downvote a message.
/karma_toggle [ENABLE|DISABLE] - Enable or Disable Karma System In Your Chat.
Reply to a message with /karma to check a user's karma
Send /karma without replying to any message to check karma list of top 10 users"""

regex_upvote = r"^(\++|\+1|thx|tnx|tq|ty|thankyou|thank you|thanx|thanks|pro|cool|good|agree|👍|\++ .+)$"
regex_downvote = r"^(-+|-1|not cool|disagree|worst|bad|👎|-+ .+)$"

# The rest of the code remains the same as previously provided
# ...

