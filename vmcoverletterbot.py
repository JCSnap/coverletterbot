# -*- coding: utf-8 -*-
"""VMCoverLetterBot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OkpOvPy0TXnURibsJI-ze8C227V76BF5
"""

import logging 
import math
import telegram
from telegram import Update, ForceReply, ReplyKeyboardMarkup
import nest_asyncio
nest_asyncio.apply()
from telegram.ext import (Updater, 
                          CommandHandler, 
                          ConversationHandler, 
                          Application,
                          filters, 
                          MessageHandler,  
                          ContextTypes)
from telegram import __version__ as TG_VER
import requests
from bs4 import BeautifulSoup
import wandb
import os
import openai


try:
    from telegram import __version_info__
except ImportError:
     __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]
 
if __version_info__ < (20, 0, 0, "alpha", 5):
     raise RuntimeError(
         f"This example is not compatible with your current PTB version {TG_VER}. To view the "
         f"{TG_VER} version of this example, "
         f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
     )

logging.basicConfig(
    format='%(asctime)s - %(name)s - $(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

token1 = '5943071283:AAHBvhDH0GS7FkcJoOHKfZHR3-AsP_TQai8'
openai.api_key = "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"
## openai.api_key = os.environ['OPENAI_KEY']


async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s caused error "%s', update, context.error)

(NAME1, COURSE1, YEAR1, UNIVERSITY1, COMMENTS1, ADDCOMMENTS1, MODEL1, REPORT1,
 COMPANY1, COMPANY2, FINAL1, SETTINGSOPT1, FINETUNE1, LENGTH1, CREATIVITY1) = range(15)

## Global ##

class Person:
  def __init__(self, userid, name, course, year, university, comments, summ):
    self.userid = userid
    self.name = name
    self.course = course
    self.year = year
    self.university = university
    self.comments = comments
    self.summ = summ

person = Person(12343, "JC", "Computer Science", "Year 1", "National University of Singapore", "I lack experience but I am willing to learn", "empty")
GPT_prompt = ""
company_summary = ""
intro = "Please generate a cover letter for an internship application"

## Editable ##

finetune = ("The writeup has to incorporates the provided personal details (course, school, name, year)" 
"and company information (what they do, their values and mission) in a sincere, humble" 
"and natural-sounding manner"
"that highlights the applicant's enthusiasm and interest in the company. Focus on our admiration"
"towards the company's values but do it subtly instead of explicitly. Emphasise that even though "
"I lack experience, I am willing to learn. Elaborate on what I hope to achieve during the internship - learn "
"through real life projects under the company's culture. ")
length = str(400)
temp = 0.8
AI_version = True

default_finetune = finetune
default_length = length
default_temp = temp

## General Commands ##

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  await update.message.reply_text("Hi, thank you for using Cover Letter Bot! \n " +
  "/register for first time users. \n" +  "/start to begin. \n" + 
  "/settings to edit settings. \n"
  "/default to restore settings to default. \n"
  "/report to report any bugs or issues. \n"
  "/model to switch model. ")
  return ConversationHandler.END

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  await update.message.reply_text('What is your full name? ')
  return NAME1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if person.summ == "empty":
    await update.message.reply_text("/register to create a profile first! ")
    return ConversationHandler.END
  else:
    await update.message.reply_text("Name of company? ")
    if AI_version:
      return COMPANY2
    else:
      return COMPANY1

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  keyboard = [["Finetune", "Length", "Creativity"]]
  reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
  await update.message.reply_text('Finetune: edit default prompts \n'
  'Length: Edit letter length \n'
  'Creativity: Edit response creativity', reply_markup=reply_markup)
  return SETTINGSOPT1

async def default(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  finetune = default_finetune
  length = default_length
  temp = default_temp
  await update.message.reply_text("Settings restored to default. ")
  return ConversationHandler.END

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  keyboard = [["AI", "Web"]]
  reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
  await update.message.reply_text("AI: company details retrieved from AI \n"
  "Web: company details retrieved from Web \n"
  "Select a model. ", reply_markup=reply_markup)
  return MODEL1

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  await update.message.reply_text("Whar is the issue? ")
  return REPORT1

## Profile creation ##

async def name1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  person.userid = update.message.from_user.id
  person.name = update.message.text
  await update.message.reply_text("What is your course? ")
  return COURSE1

async def course1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  person.course = update.message.text
  await update.message.reply_text("What is your year of study? ")
  return YEAR1

async def year1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  person.year = update.message.text
  await update.message.reply_text("What university are you from? ")
  return UNIVERSITY1

async def university1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  person.university = update.message.text
  keyboard = [["YES", "NO"]]
  reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
  await update.message.reply_text(
      "Almost done! Do wish wish to add additional comments to refine your "
      "cover letter? "
      "To maximize the personalization of the writeup, you are encouraged to add "
      "your profile \n"
      "It is good to include skillsets, experiences, qualities. Here are some examples. \n\n"
      "It can be about you: \n"
      "I have completed [specific course or classes] related to [specific field]. \n"
      "I am passionate about [area]. \n"
      "I am familiar with [specific software or tools]. \n"
      "I have [specific experience/achievements]. \n\n"
      "Or how you want the writing to be done: \n"
      "Show enthusiasm and eagerness to learn and grow through the internship. \n"
      "Show your understanding of the company and its mission and how you can align with it. \n"
      "Use specific examples from your past experiences to demonstrate your qualifications and skills. \n"
      "Use a confident, but humble tone to express your qualifications. \n"
      "End the letter by expressing gratitude for the opportunity and your readiness to begin the internship.",
      reply_markup = reply_markup
  )
  return COMMENTS1

async def comments1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  response = update.message.text
  if response == "YES":
    await update.message.reply_text("Comments: ")
    return ADDCOMMENTS1 
  else:
    person.comments = ""
    update.message.reply_text("Profile successfully created! Type /start to begin! ")
    return ConversationHandler.END

async def addcomments1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  person.comments = update.message.text
  person.summ = summary1()
  await update.message.reply_text(person.summ + "\nProfile successfully created! Type /start to begin! ")
  return ConversationHandler.END

## Settings ##

async def settingsopt1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  setting_val = update.message.text
  if setting_val == "Finetune":
    await update.message.reply_text(f"Default prompt: {finetune} \n Enter new default prompt or /cancel to keep default.")
    return FINETUNE1
  elif setting_val == "Length":
    await update.message.reply_text(f"Default words: 400. Enter new length between 150 and 500 or /cancel to keep default.")
    return LENGTH1
  else:
    await update.message.reply_text(f"Default creativity: 0.8 \n"
    f"Current creativity: {temp} \n"
    "Enter a value between 0 and 1. The higher the value the greater the creativity, but "
    "also greater propensity of going off tangent \n" 
    "/cancel to keep default.")
    return CREATIVITY1

async def finetune1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  finetune_val = update.message.text
  if finetune_val == "/cancel":
    return ConversationHandler.END
  else:
    finetune = finetune_val
    await update.message.reply_text("Finetuning is now: \n" + finetune)
    return ConversationHandler.END

async def length1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  length_val = update.message.text
  if length_val == "/cancel":
    return ConversationHandler.END
  elif float(length_val) >= 150 and float(length_val) <= 500:
    length = str(length_val)
    await update.message.reply_text(f"Length changed to {length}")
    return ConversationHandler.END
  else:
    await update.message.reply_text("Invalid input. ")
    return ConversationHandler.END

async def creativity1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  temp_val = update.message.text
  if temp_val == "/cancel":
    return ConversationHandler.END
  elif float(temp_val) >= 0 and float(temp_val) <= 1:
    temp = float(temp_val)
    await update.message.reply_text(f"Creativity set to {temp}")
    return ConversationHandler.END
  else:
    await update.message.reply_text("Invalid input. ")
    return ConversationHandler.END

async def model1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  model_ver = update.message.text
  if model_ver == "AI":
    AI_version = True
  else:
    AI_version = False
  await update.message.reply_text(f"{model_ver} model selected. ")
  return ConversationHandler.END

async def report1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  bug_report = update.message.text
  chat_id = update.message.chat_id
  handler_id = 788752139
  await context.bot.send_message(chat_id=handler_id, text=bug_report)
  await update.message.reply_text("Thanks for the report! I'll look into the issue.")
  return ConversationHandler.END

def summary1():
  summary = ("Profile: \n" + "Name: " + str(person.name) + "\nCourse: " + str(person.course)
  + "\nYear: " + str(person.year) + "\nUniversity: " + str(person.university) + "\nComments: " 
  + str(person.comments))
  return summary

async def company2(update: Update, context: ContextTypes.DEFAULT_TYPE):
  company_name = update.message.text
  prediction_table = wandb.Table(columns=["prompt", "completion"])
  prompt = f"Tell me what the company {company_name} does, their missions and values"

  completions = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=1500,
    n=1,
    stop=None,
    temperature=temp,
  )
  
  company_summary = completions.choices[0].text
  gpt_prompt = f"{intro} \nThis is my {person.summ}\n\nThis is the company. {company_summary}\n{finetune}. Minimum {length} words "
  print(gpt_prompt)
  await update.message.reply_text("Processing... It may take up to 20 seconds! ")
  writeup = gpt_writeup(gpt_prompt)
  await update.message.reply_text(writeup)
  return ConversationHandler.END

## Company details ##
async def company1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  company_name = update.message.text
  query = company_name + " company values"
  api_key = "AIzaSyC0JQVxZqGtsLqdWjROUyb8fA7mLI_vrmM"
  cx = '3787a9ff3fbea4fcc'
  search_results = await search(query, api_key, cx)
  first_result_url = None
  if search_results.get('items'):
    for item in search_results['items']:
        if item['kind'] != 'customsearch#promotion':
            first_result_url = item['link']
            break
  print(first_result_url)
  response = requests.get(first_result_url)
  soup = BeautifulSoup(response.text, 'html.parser')
  p_tags = soup.find_all('p')
  text = ' '.join([tag.get_text() for tag in p_tags])
  company_summary = gpt_summary(text, query)
  return FINAL1

async def final1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  gpt_prompt = f"{intro} \nThis is my {person.summ}\n\nThis is the company. {company_summary}\n{finetune}. Minimum {length} words"
  print(gpt_prompt)
  await update.message.reply_text("Processing... It may take up to 20 seconds! ")
  writeup = gpt_writeup(gpt_prompt)
  await update.message.reply_text(writeup)
  return ConversationHandler.END

async def search(query: str, api_key: str, cx: str):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {'q': query, 'key': api_key, 'cx': cx}
    response = requests.get(url, params=params)
    data = response.json()
    return data

## OPENAI ##
def gpt_summary(para, company_name):
  prediction_table = wandb.Table(columns=["prompt", "completion"])
  prompt = f"Summarise this webpage to show the values of the company {company_name} "
  "and what makes the company stands out over other company. Ignore irrelevant information \n {para}"

  completions = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=2040,
    n=1,
    stop=None,
    temperature=0.5,
  )

  summarized_webpage = completions.choices[0].text
  return summarized_webpage

def gpt_writeup(para):
  prediction_table = wandb.Table(columns=["prompt", "completion"])
  
  completions = openai.Completion.create(
    engine="text-davinci-003",
    prompt=para,
    max_tokens=2040,
    n=1,
    stop=None,
    temperature=temp,
  )

  writeup_generated = completions.choices[0].text
  return writeup_generated

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please try again.')
    return ConversationHandler.END

def main() -> None:

  # Create the Application and pass it your bot's token.
  application = Application.builder().token(token1).build()

  # on different commands - answer in Telegram

  conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), 
            CommandHandler('register', register),
            CommandHandler('info', info),
            CommandHandler('settings', settings),
            CommandHandler('default', default),
            CommandHandler('report', report),
            CommandHandler('model', model),
            ],
        states={
            NAME1: [MessageHandler(filters.TEXT, name1)],
            COURSE1: [MessageHandler(filters.TEXT, course1)],
            YEAR1: [MessageHandler(filters.TEXT, year1)],
            UNIVERSITY1: [MessageHandler(filters.TEXT, university1)],
            COMMENTS1: [MessageHandler(filters.TEXT, comments1)],
            ADDCOMMENTS1: [MessageHandler(filters.TEXT, addcomments1)],
            COMPANY1: [MessageHandler(filters.TEXT, company1)],
            COMPANY2: [MessageHandler(filters.TEXT, company2)],
            FINAL1: [MessageHandler(filters.TEXT, final1)],
            SETTINGSOPT1: [MessageHandler(filters.TEXT, settingsopt1)],
            FINETUNE1: [MessageHandler(filters.TEXT, finetune1)],
            LENGTH1: [MessageHandler(filters.TEXT, length1)],
            CREATIVITY1: [MessageHandler(filters.TEXT, creativity1)],
            MODEL1: [MessageHandler(filters.TEXT, model1)],
            REPORT1: [MessageHandler(filters.TEXT, report1)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
  
  application.add_handler(conv_handler)

  # Run the bot
  application.run_polling()

if __name__ == '__main__':
    main()
