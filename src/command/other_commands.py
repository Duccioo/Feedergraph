from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.make_text import number_to_emoji


def list_handler(db_telegraph, alias, url, index):
    

    if db_telegraph == True:
        new_link = "✳️Normal Link✳️k"
        old_link = "🤙Telegraph Link🤙"
    else:
        new_link = "🤙Telegraph Link🤙"
        old_link = "✳️Normal Link✳️"

    message = (
        number_to_emoji(str(index + 1))
        + " '"
        + alias
        + "' ("
        + url
        + ")"
        + "\n➡️Default link: <b>"
        + old_link
        + "</b>"
    )
    keyboard = [
        [
            InlineKeyboardButton(
                "🔗Change to " + new_link,
                callback_data={
                    "option": "change_database",
                    "alias": alias,
                    "url": url,
                    "set_telegraph": not db_telegraph,
                },
            )
        ],
    ]
    return message, InlineKeyboardMarkup(keyboard)


def help_message():
    return "Da implementare"


def stop_handler(db, telegram_user):
    db.update_user(telegram_id=telegram_user.id, is_active=0)

    return "Oh.. Okay, I will not send you any more news updates! If you change your mind and you want to receive messages from me again use /start command again!"


def about_message(number):
    
    message = "" + "" + "" + "" + "There are currently "+str(number_to_emoji((number[0][0])))+ " active users"
    return message
