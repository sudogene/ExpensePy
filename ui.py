from main import *
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

''' ########## DO NOT TOUCH #########'''
with open('tk.txt') as file:
    TOKEN = file.readline()
filename = 'data.csv'
m = ExpenseManager(filename)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


''' ################### COMMANDS ##################'''


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm Bisky!")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def add_entry(update, context):
    args = context.args
    entries = {
        'breakfast': Breakfast, 'lunch': Lunch,
        'dinner': Dinner, 'coffee': Coffee
    }
    try:
        entry_type = entries[args[0]]
        if len(args) > 2:
            entry = entry_type(float(args[1]), args[2])
        else:
            entry = entry_type(float(args[1]))
        m.add(entry)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Added!")
    except Exception:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error!")


add_entry_handler = CommandHandler('add', add_entry)
dispatcher.add_handler(add_entry_handler)


def view_df(update, context):
    if context.args:
        df = m.view(int(context.args[0]))
    else:
        df = m.view()
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{df}", parse_mode='MarkdownV2')


view_df_handler = CommandHandler('view', view_df)
dispatcher.add_handler(view_df_handler)


def view_balance(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Balance: `{m.balance}`", parse_mode='MarkdownV2')


view_balance_handler = CommandHandler('balance', view_balance)
dispatcher.add_handler(view_balance_handler)

updater.start_polling()
