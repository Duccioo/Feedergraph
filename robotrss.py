# /bin/bash/python
# encoding: utf-8

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    Updater,
    ContextTypes,
)

from utils.filehandler import FileHandler
from utils.database import DatabaseHandler
from utils.processing import BatchProcess
from utils.feedhandler import FeedHandler
import os
import telegram


TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


class RobotRss(object):
    def __init__(self, telegram_token, update_interval):

        # Initialize bot internals
        self.db = DatabaseHandler("database/datastore.db")
        self.fh = FileHandler("database/setub.sql")

        self.updater = Application.builder().token(telegram_token).build()

        # Add Commands to bot
        self._addCommand(CommandHandler("start", self.start))
        self._addCommand(CommandHandler("stop", self.stop))
        self._addCommand(CommandHandler("help", self.help))
        self._addCommand(CommandHandler("list", self.list))
        self._addCommand(CommandHandler("about", self.about))
        self._addCommand(CommandHandler("add", self.add))
        self._addCommand(CommandHandler("get", self.get))
        self._addCommand(CommandHandler("remove", self.remove))

        # Start the Bot
        self.processing = BatchProcess(
            database=self.db, update_interval=update_interval, bot=self.updater.bot
        )

        self.processing.start()
        self.updater.run_polling()

    def _addCommand(self, command):

        """
        Registers a new command to the bot
        """

        self.updater.add_handler(command)

    async def start(self, update, context: ContextTypes.DEFAULT_TYPE):
        """
        Send a message when the command /start is issued.
        """
        telegram_user = update.message.from_user

        await context.bot.send_message(
            update.message.chat.id, text="Beep! seconds are over!"
        )
        print("asd", self.db.get_user(telegram_id=telegram_user.id))

        # Add new User if not exists
        if not self.db.get_user(telegram_id=telegram_user.id):

            message = "Ciao! It's your first time? Well... Eeveryone has had a first time, so for start add a new Feeeed in your list with /add or instantly grab a feedgraph with the /get command "
            await update.message.reply_text(message)

            self.db.add_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                firstname=telegram_user.first_name,
                lastname=telegram_user.last_name,
                language_code=telegram_user.language_code,
                is_bot=telegram_user.is_bot,
                is_active=1,
            )

        self.db.update_user(telegram_id=telegram_user.id, is_active=1)

        message = "You will now receive news! Use /help if you need some tips how to tell me what to do!"
        await update.message.reply_text(message)

    async def add(self, update, context):
        # Adds a rss subscription to user

        telegram_user = update.message.from_user
        args = update.message.text.split()
        print(len(args))
        if len(args) != 3:
            message = "Sorry! I could not add the entry! Please use the the command passing the following arguments:\n\n /add <url> <entryname> \n\n Here is a short example: \n\n /add http://www.feedforall.com/sample.xml ExampleEntry"
            await update.message.reply_text(message)
            return

        arg_url = FeedHandler.format_url_string(string=args[1])
        arg_entry = args[2]

        # Check if argument matches url format
        if not FeedHandler.is_parsable(url=arg_url):
            message = (
                "Sorry! It seems like '"
                + str(arg_url)
                + "' doesn't provide an RSS news feed.. Have you tried another URL from that provider?"
            )
            await update.message.reply_text(message)
            return

        # Check if entry does not exists
        entries = self.db.get_urls_for_user(telegram_id=telegram_user.id)
        print(entries)

        if any(arg_url.lower() in entry for entry in entries):
            message = (
                "Sorry, "
                + telegram_user.first_name
                + "! I already have that url with stored in your subscriptions."
            )
            await update.message.reply_text(message)
            return

        if any(arg_entry in entry for entry in entries):
            message = (
                "Sorry! I already have an entry with name "
                + arg_entry
                + " stored in your subscriptions.. Please choose another entry name or delete the entry using '/remove "
                + arg_entry
                + "'"
            )
            await update.message.reply_text(message)
            return

        self.db.add_user_bookmark(
            telegram_id=telegram_user.id, url=arg_url.lower(), alias=arg_entry
        )
        message = "I successfully added " + arg_entry + " to your subscriptions!"
        await update.message.reply_text(message)

    async def get(self, update, context):
        """
        Manually parses an rss feed
        """

        telegram_user = update.message.from_user
        args = update.message.text.split()

        if len(args) > 3 or len(args) <= 1:
            message = "To get the last news of your subscription please use /get <entryname> [optional: <count 1-10>]. Make sure you first add a feed using the /add command."
            await update.message.reply_text(message)
            return

        if len(args) == 3:
            args_entry = args[1].lower()
            args_count = int(args[2])
        else:
            args_entry = args[1]
            args_count = 1

        url = self.db.get_user_bookmark(telegram_id=telegram_user.id, alias=args_entry)

        if url is None:
            message = (
                "I can not find an entry with label "
                + args_entry
                + " in your subscriptions! Please check your subscriptions using /list and use the delete command again!"
            )
            await update.message.reply_text(message)
            return

        entries = FeedHandler.parse_feed(url[0], args_count)
        for entry in entries.entries[:args_count]:
            message = (
                "["
                + url[1]
                + "] <a href='"
                + entry.link
                + "'>"
                + entry.title
                + str(entries.feed.updated)
                + "</a>"
            )

            try:
                await update.message.reply_text(message, parse_mode="HTML")

            except:
                print("qowkoedkasopdkasopdkasopdkaspod")
                # handle all other telegram related errors
                pass

    async def remove(self, update, context):
        """
        Removes an rss subscription from user
        """

        args = context.args
        print(args)

        telegram_user = update.message.from_user

        if len(args) != 1:
            message = "To remove a subscriptions from your list please use /remove <entryname>. To see all your subscriptions along with their entry names use /list !"
            await update.message.reply_text(message)
            return

        entry = self.db.get_user_bookmark(telegram_id=telegram_user.id, alias=args[0])

        if entry:
            self.db.remove_user_bookmark(telegram_id=telegram_user.id, url=entry[0])
            message = "I removed " + args[0] + " from your subscriptions!"
            await update.message.reply_text(message)
        else:
            message = (
                "I can not find an entry with label "
                + args[0]
                + " in your subscriptions! Please check your subscriptions using /list and use the delete command again!"
            )
            await update.message.reply_text(message)

    async def list(self, update, context):
        """
        Displays a list of all user subscriptions
        """

        telegram_user = update.message.from_user

        message = "Here is a list of all subscriptions I stored for you!"
        await update.message.reply_text(message)

        entries = self.db.get_urls_for_user(telegram_id=telegram_user.id)

        for entry in entries:
            message = "-->" + entry[1] + "\n " + entry[0]
            await update.message.reply_text(message)

    def help(self, update):
        """
        Send a message when the command /help is issued.
        """

        message = "If you need help with handling the commands, please have a look at my <a href='https://github.com/cbrgm/telegram-robot-rss'>Github</a> page. There I have summarized everything necessary for you!"
        update.message.reply_text(message, parse_mode="HTML")

    def stop(self, update):
        """
        Stops the bot from working
        """

        telegram_user = update.message.from_user
        self.db.update_user(telegram_id=telegram_user.id, is_active=0)

        message = "Oh.. Okay, I will not send you any more news updates! If you change your mind and you want to receive messages from me again use /start command again!"
        update.message.reply_text(message)

    def about(self, bot, update):
        """
        Shows about information
        """

        message = "Thank you for using <b>RobotRSS</b>! \n\n If you like the bot, please recommend it to others! \n\nDo you have problems, ideas or suggestions about what the bot should be able to do? Then contact my developer <a href='http://cbrgm.de'>@cbrgm</a> or create an issue on <a href='https://github.com/cbrgm/telegram-robot-rss'>Github</a>. There you will also find my source code, if you are interested in how I work!"
        update.message.reply_text(message, parse_mode="HTML")


if __name__ == "__main__":
    # Load Credentials
    RobotRss(telegram_token=TELEGRAM_TOKEN, update_interval=300)
