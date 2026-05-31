import os
from telegram import Update,ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from telegram.request import HTTPXRequest

from config import TOKEN, UPLOAD_DIR, ALLOWED_EXTENSIONS
from state import (
    user_states,
    create_user_state,
    WAITING_LEVEL,
    WAITING_FEEDBACK_LANG,
    WAITING_TASK,
    WAITING_CV,
    WAITING_CV_CONFIRMATION,
    WAITING_JD,
)
from keyboards import build_keyboard

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_allowed_file(filename:str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


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

async def handle_document(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_states:
        await update.message.reply_text("Please type /start to begin")
        return

    phase = user_states[user_id]["phase"]
    document = update.message.document

    if phase !=WAITING_CV:
        await update.message.reply_text(
            "I was not expecting a document right now."
        )
        return
    filename = document.file_name or "uploaded_file"

    if not is_allowed_file(filename):
        await update.message.reply_text(
        "Unsupported file type. Please upload a PDF or TXT file."
        )
        return
    

    ensure_upload_dir()

    safe_filename = f"{user_id}_cv_{filename}"
    file_path = os.path.join(UPLOAD_DIR,safe_filename)

    telegram_file = await document.get_file()
    await telegram_file.download_to_drive(file_path)

    user_states[user_id]["cv_file_path"] = file_path
    user_states[user_id]["phase"] = WAITING_CV_CONFIRMATION

    # await update.message.reply_text(
    #     "CV received successfully ✅\n\nNow please upload the job description (PDF or TXT)."
    # )




    
    

def main():
    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=20.0,
        write_timeout=20.0,
        pool_timeout=20.0,
    )
    app = ApplicationBuilder().token(TOKEN).request(request).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.Document.ALL,handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running ...")
    app.run_polling()


if __name__== "__main__":
    main()