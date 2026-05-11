from telegram import Update,ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters

from config import TOKEN
from state import (
    user_states,
    create_user_state,
    WAITING_LEVEL,
    WAITING_FEEDBACK_LANG,
    WAITING_TASK,
    WAITING_CV
)
from keyboards import build_keyboard




async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Initialize user state 
    user_states[user_id]= create_user_state()
    
    reply_markup = build_keyboard([
        ["A2","B1"],
        ["B2","C1"],
    ])
    await update.message.reply_text(
        "Hello 👋 I am NoElephant.\n\n What is your Italian level?",
        reply_markup=reply_markup,
        )
    
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text=update.message.text.strip().upper()

    if user_id not in user_states:
        await update.message.reply_text("Please type /start to begin.")
        return

    phase = user_states[user_id]["phase"]

    if phase == "WAITING_LEVEL":
        if text in {"A2", "B1", "B2", "C1"}:
            user_states[user_id]["italian_level"] = text
            user_states[user_id]["phase"] = "WAITING_FEEDBACK_LANG"

            reply_markup = build_keyboard([
                ["IT"],
                ["IT+EN"]
            ])
            

            await update.message.reply_text(
                "Thank you.\n\n"
                "Preferred feedback language?\n",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Please choose a valid option using the buttons.")

    #---- Waiting for feedback Language--------        
    elif phase == "WAITING_FEEDBACK_LANG":

        if text in ["IT","IT+EN"]:
            user_states[user_id]["feedback_language"] = text
            user_states[user_id]["phase"] = "WAITING_TASK"

            reply_markup = build_keyboard([
               ["INTERVIEW"],
               ["EXTRA (Coming Soon)"], 
            ])
            

            await update.message.reply_text(
                "Greate! Now choose your task:",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                "Please choose a valid option using the buttons."
            )
    #-----Waiting for task selection-----
    elif phase =="WAITING_TASK":
        if text== "INTERVIEW":
            user_states[user_id]["task"] = "INTERVIEW"
            user_states[user_id]["phase"] = "WAITING_CV"

            await update.message.reply_text(
                "Please upload your CV (PDF or text).",
                reply_markup=ReplyKeyboardRemove(),
            )
        elif text.startswith("EXTRA"):
            await update.message.reply_text(
                "This feature is coming soon 🙂"
            )
        else:
            await update.message.reply_text(
                "Please choose a valid option using the buttons."
            )
    #------ Waiting for CV (placeholder)----
    elif phase=="WAITING_CV":
        await update.message.reply_text(
            "Please upload your CV."
        )
    else:
        await update.message.reply_text(
            "Unexpected state. Please type /start."
        )

    

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running ...")
    app.run_polling()


if __name__== "__main__":
    main()