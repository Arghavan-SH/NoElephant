import os
from telegram import Update,ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from telegram.request import HTTPXRequest

from pypdf import PdfReader
from docx import Document

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

def extract_text_from_file(file_path:str) -> str:
    _, ext = os.path.splitext(file_path.lower())

    
        
    if ext == ".pdf":
        reader = PdfReader(file_path)
        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)

        return "\n".join(pages_text)
    
    elif ext == ".docx":
        doc = Document(file_path)
        paragraphs = []

        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip()) 
        
        return "\n".join(paragraphs)

    else:
        raise ValueError(f"Unsupported file type for extraction: {ext}")

def validate_extracted_text(text:str) -> tuple[bool,str]:
    cleaned = text.strip()

    if not cleaned:
        return False, "The file was read, but no text could be extracted."
    
    if len (cleaned) < 200:
        return False, "The extracted text is too short to be a usable CV."
    
    return True, "Text extraction successful."
    


async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Initialize user state 
    user_states[user_id]= create_user_state()
    
    reply_markup = build_keyboard([
        ["A2","B1"],
        ["B2","C1"],
    ])
    await update.message.reply_text(
        "Hello 👋 I am NoElephant.\n\nWhat is your Italian level?",
        reply_markup=reply_markup,
        )
    
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    raw_text = update.message.text.strip()
    text = raw_text.upper()

    if user_id not in user_states:
        await update.message.reply_text("Please type /start to begin.")
        return

    phase = user_states[user_id]["phase"]

    if phase == WAITING_LEVEL:
        if text in {"A2", "B1", "B2", "C1"}:
            user_states[user_id]["italian_level"] = text
            user_states[user_id]["phase"] = WAITING_FEEDBACK_LANG

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
    elif phase == WAITING_FEEDBACK_LANG:

        if text in ["IT","IT+EN"]:
            user_states[user_id]["feedback_language"] = text
            user_states[user_id]["phase"] = WAITING_TASK

            reply_markup = build_keyboard([
               ["INTERVIEW"],
               ["EXTRA (Coming Soon)"], 
            ])
            

            await update.message.reply_text(
                "Great! Now choose your task:",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                "Please choose a valid option using the buttons."
            )
    #-----Waiting for task selection-----
    elif phase == WAITING_TASK:
        if text== "INTERVIEW":
            user_states[user_id]["task"] = "INTERVIEW"
            user_states[user_id]["phase"] = WAITING_CV

            await update.message.reply_text(
                "Please upload your CV (PDF or DOCX).",
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
    #------ Waiting for CV ----
    elif phase== WAITING_CV:
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
        await update.message.reply_text("Please type /start to begin.")
        return

    phase = user_states[user_id]["phase"]
    document = update.message.document

    if phase != WAITING_CV:
        await update.message.reply_text(
            "I was not expecting a document right now."
        )
        return
    if not document:
        await update.message.reply_text("No document detected.")
        return
    filename = document.file_name or "uploaded_file"

    if not is_allowed_file(filename):
        await update.message.reply_text(
        "Unsupported file type. Please upload a PDF or DOCX file."
        )
        return
    

    ensure_upload_dir()

    safe_filename = f"{user_id}_cv_{filename}"
    file_path = os.path.join(UPLOAD_DIR,safe_filename)

    telegram_file = await document.get_file()
    await telegram_file.download_to_drive(file_path)

    try:
        extracted_text = extract_text_from_file(file_path)
    except Exception as e:
        await update.message.reply_text(
            f"I received the file, but I could not extract text from it.\nError: {e}"
        )
        return
    
    is_valid, validation_message = validate_extracted_text(extracted_text)

    if not is_valid:
        await update.message.reply_text(
            f"CV technical validation failed.\n{validation_message}\nPlease upload another file. "
        )
        return

    user_states[user_id]["cv_file_path"] = file_path
    user_states[user_id]["cv_text"] = extracted_text
    user_states[user_id]["cv_validation_result"] = {
        "status": "technical_pass",
        "message": validation_message,
    }
    #user_states[user_id]["phase"] = WAITING_CV_CONFIRMATION

    preview = extracted_text[:500].strip()

    await update.message.reply_text(
        "CV received and read successfully ✅\n\n"
        f"Technical validation: {validation_message}\n\n"
        f"Preview:\n{preview}\n\n"
        "Next step: LLM CV confirmation."
    )



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in user_states:
        await update.message.reply_text("Please type /start to begin.")
        return
    
    phase = user_states[user_id]["phase"]

    if phase == WAITING_CV:
        await update.message.reply_text(
            "Images are not supported for CV upload. Please upload your CV as a PDF or DOCX document."
        )
    else:
        await update.message.reply_text(
            "I was not expecting an image right now."
        )
        

    
    

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
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running ...")
    app.run_polling()


if __name__== "__main__":
    main()