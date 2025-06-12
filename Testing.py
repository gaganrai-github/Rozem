from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import subprocess
import time
import keyboard as kb
import psutil
import pyautogui
import cv2
import webbrowser
import pyperclip
import random
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from telegram.constants import ParseMode # Import ParseMode for explicit MarkdownV2 parsing
import uuid # Import uuid for generating unique IDs
import shutil # Import shutil for file operations (copy, move)
import json # For structured LLM responses
import httpx # For making asynchronous HTTP requests for LLM API
import re # For regular expressions in Markdown escaping

# Configuration
# It's recommended to set your bot token as an environment variable for security.
# Example: BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# For demonstration, a placeholder token is used, but it should be replaced.
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7928754707:AAEhMxWrGW06wdGuGPgdrL2oayYianOFjKY")
ALLOWED_USER_ID = 7854612472  # Replace with your Telegram user ID for authorization
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB max file size for file transfers

# Define specific target directories for categorized file saving
BASE_PROGRAMS_DIR = "C:\\Programs"
CODE_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Code Files")
PDF_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "PDF Files")
IMAGE_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Image Files")
VIDEO_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Video Files")
AUDIO_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Audio Files")
OTHER_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Other Files")

# Ensure base directories exist
os.makedirs(BASE_PROGRAMS_DIR, exist_ok=True)
os.makedirs(CODE_FILES_DIR, exist_ok=True)
os.makedirs(PDF_FILES_DIR, exist_ok=True)
os.makedirs(IMAGE_FILES_DIR, exist_ok=True)
os.makedirs(VIDEO_FILES_DIR, exist_ok=True)
os.makedirs(AUDIO_FILES_DIR, exist_ok=True)
os.makedirs(OTHER_FILES_DIR, exist_ok=True)

# LLM API configuration
API_KEY = "" # If you want to use models other than gemini-2.0-flash or imagen-3.0-generate-002, provide an API key here. Otherwise, leave this as-is.
API_URL_TEXT_GEN = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# ==================== HELPER FUNCTIONS ====================

def escape_markdown_v2(text: str) -> str:
    """Helper function to escape special characters for MarkdownV2."""
    # List of special characters in MarkdownV2 that need to be escaped
    # Reference: https://core.telegram.org/bots/api#markdownv2-style
    # The order matters for some characters (e.g., \ before _, *, etc.)
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and prompts to open the menu."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    await update.message.reply_text(
        "Welcome! I am your PC remote control bot. Use /menu to see available commands."
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the main menu with various bot functionalities."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    keyboard = [
        [InlineKeyboardButton("🖥️ System Info", callback_data="system_info"),
         InlineKeyboardButton("📸 Take Screenshot", callback_data="screenshot")],
        [InlineKeyboardButton("📷 Click Photo", callback_data="click_photo"),
         InlineKeyboardButton("🌐 Browse Files (C:\\)", callback_data="browse_dir:C:\\")],
        [InlineKeyboardButton("💡 Brightness", callback_data="set_brightness"),
         InlineKeyboardButton("🔊 Volume", callback_data="set_volume")],
        [InlineKeyboardButton("⏯️ Media Controls", callback_data="media_controls"),
         InlineKeyboardButton("🔗 Shortcuts", callback_data="shortcuts")],
        [InlineKeyboardButton("⏬ Shutdown PC", callback_data="shutdown"),
         InlineKeyboardButton("🚫 Cancel Shutdown", callback_data="cancel_shutdown")],
        [InlineKeyboardButton("🔗 Open YouTube", callback_data="youtube"),
         InlineKeyboardButton("💬 Open WhatsApp", callback_data="open_whatsapp")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Check if the update is from a callback query (e.g., "Back to Main Menu")
    if update.callback_query:
        await update.callback_query.edit_message_text("Please choose from the menu:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please choose from the menu:", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message listing all available commands and features."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    help_text = """
    Here are the commands you can use:

    /start \- Start the bot\.
    /menu \- Show the main menu with various options\.
    /help \- Display this help message\.
    /youtube \- Open YouTube in the default browser\.
    /open\_whatsapp \- Open WhatsApp Web in the default browser\.
    /system\_info \- Get detailed system information\.
    /screenshot \- Take a screenshot of the current screen\.
    /click\_photo \- Take a photo using the default webcam\.
    /browse \- Browse files starting from C:\.\\
    /shutdown \- Schedule PC shutdown in 60 seconds\.
    /cancel\_shutdown \- Cancel a scheduled shutdown\.
    /shortcuts \- Show a list of common Windows shortcuts\.

    You can also send text messages to chat with the bot \(AI chatbot\)\.
    """
    # Escape help_text manually here as it's a fixed string
    help_text = escape_markdown_v2(help_text) # This might cause double escaping if not careful
    # For fixed text like this, it's better to manually escape when writing it.
    # The example above is manually escaped already.
    
    if update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)

async def youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Opens YouTube in the default web browser."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    webbrowser.open("https://www.youtube.com")
    await update.message.reply_text("YouTube opened in your default browser.")

async def open_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Opens WhatsApp Web in the default web browser."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    webbrowser.open("https://web.whatsapp.com")
    await update.message.reply_text("WhatsApp Web opened in your default browser.")

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieves and sends basic system information."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    info = (
        f"**Operating System:** {escape_markdown_v2(os.sys.platform)}\n"
        f"**CPU Usage:** {escape_markdown_v2(str(psutil.cpu_percent()))}%\n"
        f"**Memory Usage:** {escape_markdown_v2(str(psutil.virtual_memory().percent))}% \n"
        f"**Disk Usage (C:\!):** {escape_markdown_v2(str(psutil.disk_usage('C:\\').percent))}% \n"
        f"**Boot Time:** {escape_markdown_v2(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time())))}\n"
    )
    # Check if the update is from a callback query to edit the message
    if update.callback_query:
        await update.callback_query.edit_message_text(info, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(info, parse_mode=ParseMode.MARKDOWN_V2)

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Takes a screenshot of the primary display and sends it to the user."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    try:
        screenshot = pyautogui.screenshot()
        # Use a unique ID for the filename to prevent conflicts
        screenshot_path = f"screenshot_{uuid.uuid4()}.png"
        screenshot.save(screenshot_path)
        await update.message.reply_photo(photo=open(screenshot_path, 'rb'))
        os.remove(screenshot_path) # Clean up the screenshot file
    except Exception as e:
        await update.message.reply_text(f"Error taking screenshot: {e}")

async def click_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Takes a photo using the default webcam and sends it to the user."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    try:
        cap = cv2.VideoCapture(0) # Open the default camera
        if not cap.isOpened():
            raise IOError("Cannot open webcam. Make sure it's connected and not in use.")
        
        ret, frame = cap.read() # Read a frame from the camera
        if not ret:
            raise IOError("Failed to grab frame from webcam.")
        
        photo_path = f"webcam_photo_{uuid.uuid4()}.png"
        cv2.imwrite(photo_path, frame) # Save the captured frame to a file
        cap.release() # Release the camera
        
        await update.message.reply_photo(photo=open(photo_path, 'rb'))
        os.remove(photo_path) # Clean up the photo file
    except Exception as e:
        await update.message.reply_text(f"Error clicking photo: {e}")

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Sends a specified file from the PC to the Telegram user."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.callback_query.answer("You are not authorized to use this bot.")
        return
    
    if not os.path.exists(file_path):
        await update.callback_query.edit_message_text(f"File not found: `{escape_markdown_v2(file_path)}`", parse_mode=ParseMode.MARKDOWN_V2)
        return

    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await update.callback_query.edit_message_text(
                f"File size \({escape_markdown_v2(f'{file_size / (1024*1024):.2f}')}MB\) exceeds limit of {escape_markdown_v2(f'{MAX_FILE_SIZE / (1024*1024):.2f}')}MB\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        await update.callback_query.answer(f"Sending file: {os.path.basename(file_path)}...")
        # Use effective_message to ensure reply is sent to the correct chat, whether from message or callback
        await update.effective_message.reply_document(document=open(file_path, 'rb'))
    except PermissionError:
        await update.callback_query.edit_message_text(f"Permission denied to access `{escape_markdown_v2(file_path)}`.", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await update.callback_query.edit_message_text(f"Error sending file `{escape_markdown_v2(file_path)}`: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)


async def browse_files(update: Update, context: ContextTypes.DEFAULT_TYPE, path: str):
    """
    Allows the user to browse files and folders on the PC,
    with options to create folders, copy, cut, paste, and download files.
    """
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        if update.callback_query:
            await update.callback_query.answer("You are not authorized to use this bot.")
        else:
            await update.message.reply_text("You are not authorized to use this bot.")
        return

    current_path = os.path.abspath(path)
    if not os.path.isdir(current_path):
        error_msg = f"Invalid directory: `{escape_markdown_v2(current_path)}`"
        if update.callback_query:
            await update.callback_query.answer(error_msg)
            await update.callback_query.edit_message_text(
                f"Error: `{error_msg}`",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN_V2)
        return

    # Store current path in user_data for "Create Folder" and "Paste" operations
    context.user_data['current_browse_path'] = current_path

    keyboard = []
    files_list = []
    dirs_list = []

    try:
        # Sort directories and files for better display
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                dirs_list.append(item)
            else:
                files_list.append(item)

        # Add directories to keyboard
        for item in sorted(dirs_list):
            callback_data = f"browse_dir:{os.path.join(current_path, item)}"
            keyboard.append([InlineKeyboardButton(f"📁 {item}", callback_data=callback_data)])

        # Add files to keyboard with Copy/Cut/Download options
        for item in sorted(files_list):
            file_path = os.path.join(current_path, item)
            copy_cb = f"copy_file:{file_path}"
            cut_cb = f"cut_file:{file_path}"
            download_cb = f"download_file:{file_path}"

            keyboard.append([
                InlineKeyboardButton(f"📄 {item}", callback_data="do_nothing"), # A dummy button for file name
                InlineKeyboardButton("✂️ Cut", callback_data=cut_cb),
                InlineKeyboardButton("📋 Copy", callback_data=copy_cb),
                InlineKeyboardButton("⬇️ Download", callback_data=download_cb)
            ])


        # Add "Go Up" button if not at root of a drive
        # os.path.splitdrive returns ('C:', '\\') for 'C:\\' and ('', 'folder') for 'folder'
        # os.path.dirname returns 'C:\\' for 'C:\\Users' and 'C:\\Users' for 'C:\\Users\\User'
        # This condition checks if current_path is NOT a drive root or system root (like 'C:\\')
        if os.path.splitdrive(current_path)[1] != os.sep and os.path.dirname(current_path) != current_path:
            parent_dir = os.path.dirname(current_path)
            keyboard.append([InlineKeyboardButton("⬆️ Go Up", callback_data=f"browse_dir:{parent_dir}")])
        else: # If at a root (e.g., C:\), show available drives
            drives = [d for d in psutil.disk_partitions() if 'cdrom' not in d.opts and d.device]
            for drive in drives:
                keyboard.append([InlineKeyboardButton(f"💽 {drive.device}", callback_data=f"browse_dir:{drive.mountpoint}")])


        # Add "Create Folder" button
        keyboard.append([InlineKeyboardButton("➕ Create New Folder", callback_data="create_folder_prompt")])

        # Add "Paste" button if something is in clipboard
        if 'clipboard' in context.user_data and context.user_data['clipboard']:
            keyboard.append([InlineKeyboardButton("✅ Paste", callback_data="paste_file")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        # Escape current_path for display in the message
        display_path = escape_markdown_v2(current_path)

        # Check if the update is from a message or a callback query to update the message accordingly
        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"Browsing: `{display_path}`\n\nChoose an action:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(
                f"Browsing: `{display_path}`\n\nChoose an action:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )

    except PermissionError:
        error_msg = f"Permission denied to access `{escape_markdown_v2(current_path)}`. Please try another directory."
        if update.callback_query:
            await update.callback_query.answer(error_msg, show_alert=True) # Show a pop-up alert
            await update.callback_query.edit_message_text(
                f"Error: `{error_msg}`",
                reply_markup=reply_markup, # Keep the current keyboard if possible
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(f"Error: `{error_msg}`", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        error_msg = f"An error occurred while browsing `{escape_markdown_v2(current_path)}`: {escape_markdown_v2(str(e))}"
        if update.callback_query:
            await update.callback_query.answer(error_msg, show_alert=True)
            await update.callback_query.edit_message_text(
                f"Error: `{error_msg}`",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(f"Error: `{error_msg}`", parse_mode=ParseMode.MARKDOWN_V2)


async def send_shortcut_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends inline keyboard buttons for common Windows shortcuts."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    keyboard = [
        [InlineKeyboardButton("🔒 Lock PC (Win+L)", callback_data="shortcut_lock")],
        [InlineKeyboardButton("📋 Task Manager (Ctrl+Shift+Esc)", callback_data="shortcut_task_manager")],
        [InlineKeyboardButton("🏃 Run Dialog (Win+R)", callback_data="shortcut_run")],
        [InlineKeyboardButton("🖼️ Show Desktop (Win+D)", callback_data="shortcut_show_desktop")],
        [InlineKeyboardButton("⬆️ Maximize Window (Win+Up)", callback_data="shortcut_maximize_window")],
        [InlineKeyboardButton("⬇️ Minimize Window (Win+Down)", callback_data="shortcut_minimize_window")],
        [InlineKeyboardButton("🔇 Toggle Mute", callback_data="shortcut_toggle_mute")],
        [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("Choose a shortcut:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Choose a shortcut:", reply_markup=reply_markup)


async def shutdown_pc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initiates a PC shutdown with a 60-second delay."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    subprocess.run(["shutdown", "/s", "/t", "60"])
    await update.message.reply_text("PC will shut down in 60 seconds\. Use /cancel\_shutdown to stop\.", parse_mode=ParseMode.MARKDOWN_V2)

async def cancel_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancels any pending PC shutdown."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    subprocess.run(["shutdown", "/a"])
    await update.message.reply_text("Shutdown cancelled\.", parse_mode=ParseMode.MARKDOWN_V2)

async def handle_incoming_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming document (file) uploads from the user and saves them to categorized directories."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    document = update.message.document
    file_id = document.file_id
    file_name = document.file_name
    file_size = document.file_size

    if file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            f"File size \({escape_markdown_v2(f'{file_size / (1024*1024):.2f}')}MB\) exceeds limit of {escape_markdown_v2(f'{MAX_FILE_SIZE / (1024*1024):.2f}')}MB\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    file = await context.bot.get_file(file_id)

    # Determine destination directory based on file extension
    file_extension = os.path.splitext(file_name)[1].lower()
    destination_dir = OTHER_FILES_DIR # Default to 'Other Files'

    if file_extension in ['.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.cs', '.go', '.rb', '.php', '.swift', '.kt']:
        destination_dir = CODE_FILES_DIR
    elif file_extension == '.pdf':
        destination_dir = PDF_FILES_DIR
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        destination_dir = IMAGE_FILES_DIR
    elif file_extension in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']:
        destination_dir = VIDEO_FILES_DIR
    elif file_extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
        destination_dir = AUDIO_FILES_DIR

    save_path = os.path.join(destination_dir, file_name)

    try:
        # Ensure the destination directory exists before downloading
        os.makedirs(destination_dir, exist_ok=True)
        await file.download_to_drive(custom_path=save_path)
        await update.message.reply_text(f"Document '{escape_markdown_v2(file_name)}' saved to `{escape_markdown_v2(destination_dir)}` successfully\.", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await update.message.reply_text(f"Error saving document: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)


async def chatbot_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles general text messages and uses a language model for responses."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    # If the bot is awaiting specific input (e.g., folder name, brightness),
    # this message should be handled by 'handle_specific_user_input'
    if 'awaiting_input' in context.user_data:
        return

    user_message = update.message.text
    chat_history = []
    chat_history.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {"contents": chat_history}
    
    try:
        await update.message.reply_text("Thinking\.\.\.", parse_mode=ParseMode.MARKDOWN_V2) # Provide immediate feedback

        # Use httpx for asynchronous HTTP requests
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL_TEXT_GEN,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            result = response.json()
        
        # Parse the response from the LLM
        if result.get("candidates") and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts"):
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            await update.message.reply_text(escape_markdown_v2(text), parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text("Sorry, I could not generate a response\. Please try again\.", parse_mode=ParseMode.MARKDOWN_V2)

    except httpx.RequestError as exc:
        await update.message.reply_text(f"An error occurred while connecting to the LLM: {escape_markdown_v2(str(exc))}", parse_mode=ParseMode.MARKDOWN_V2)
    except httpx.HTTPStatusError as exc:
        await update.message.reply_text(f"LLM API returned an error {escape_markdown_v2(str(exc.response.status_code))}: {escape_markdown_v2(exc.response.text)}", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await update.message.reply_text(f"An unexpected error occurred while generating response: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)


async def handle_specific_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user input when the bot is in a specific waiting state
    (e.g., waiting for new folder name, brightness, or volume value).
    """
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if 'awaiting_input' in context.user_data:
        input_type = context.user_data.pop('awaiting_input') # Remove the flag after getting input

        if input_type == 'new_folder_name':
            new_folder_name = update.message.text.strip()
            current_path = context.user_data.get('current_browse_path')

            if not current_path or not new_folder_name:
                await update.message.reply_text("Error: Missing folder name or current path\. Please try again\.", parse_mode=ParseMode.MARKDOWN_V2)
                return

            new_folder_path = os.path.join(current_path, new_folder_name)

            try:
                os.makedirs(new_folder_path) # Create the new directory
                await update.message.reply_text(f"Folder `{escape_markdown_v2(new_folder_name)}` created successfully in `{escape_markdown_v2(current_path)}`\.",
                                                parse_mode=ParseMode.MARKDOWN_V2)
                # Re-browse the current directory to show the new folder
                await browse_files(update, context, current_path)
            except OSError as e:
                await update.message.reply_text(f"Error creating folder: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                await update.message.reply_text(f"An unexpected error occurred: {escape_markdown_v2(str(e))}", parse_mode=ParseMode.MARKDOWN_V2)
            return # IMPORTANT: Stop processing here for this specific input

        elif input_type == 'brightness':
            try:
                brightness_val = int(update.message.text)
                if 0 <= brightness_val <= 100:
                    sbc.set_brightness(brightness_val)
                    await update.message.reply_text(f"Brightness set to {escape_markdown_v2(str(brightness_val))}%", parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    await update.message.reply_text("Brightness value must be between 0 and 100\.", parse_mode=ParseMode.MARKDOWN_V2)
            except ValueError:
                await update.message.reply_text("Invalid input\. Please send a number for brightness \(0-100\)\.", parse_mode=ParseMode.MARKDOWN_V2)
            return # IMPORTANT: Stop processing here

        elif input_type == 'volume':
            try:
                volume_val = int(update.message.text)
                if 0 <= volume_val <= 100:
                    sessions = AudioUtilities.GetAllSessions()
                    # Iterate through sessions to find the master volume control
                    for session in sessions:
                        volume = session._ctl.QueryInterface(IAudioEndpointVolume)
                        if volume:
                            # Set master volume directly.
                            volume.SetMasterVolumeLevelScalar(volume_val / 100.0, None)
                            break # Assuming setting one master volume is sufficient.
                    await update.message.reply_text(f"Volume set to {escape_markdown_v2(str(volume_val))}%", parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    await update.message.reply_text("Volume value must be between 0 and 100\.", parse_mode=ParseMode.MARKDOWN_V2)
            except ValueError:
                await update.message.reply_text("Invalid input\. Please send a number for volume \(0-100\)\.", parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                await update.message.reply_text(f"Error setting volume: {escape_markdown_v2(str(e))}\. Make sure pycaw is installed and accessible\.", parse_mode=ParseMode.MARKDOWN_V2)
            return # IMPORTANT: Stop processing here

# ==================== CALLBACK QUERY HANDLERS ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all inline keyboard button presses."""
    query = update.callback_query
    user_id = query.from_user.id
    if user_id != ALLOWED_USER_ID:
        await query.answer("You are not authorized to use this bot.", show_alert=True) # Show alert for unauthorized
        return

    await query.answer() # Acknowledge the query immediately

    data = query.data

    if data == "main_menu":
        await main_menu(update, context) # Call main_menu to re-render the menu
    elif data == "system_info":
        await system_info(update, context)
    elif data == "screenshot":
        await take_screenshot(update, context)
    elif data == "click_photo":
        await click_photo(update, context)
    elif data == "youtube":
        await youtube_url(update, context)
    elif data == "open_whatsapp":
        await open_whatsapp(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data == "media_controls":
        media_keyboard = [
            [InlineKeyboardButton("▶️ Play/Pause", callback_data="media_play_pause"),
             InlineKeyboardButton("⏩ Next Track", callback_data="media_next_track")],
            [InlineKeyboardButton("⏪ Previous Track", callback_data="media_prev_track"),
             InlineKeyboardButton("⏹️ Stop", callback_data="media_stop")],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(media_keyboard)
        await query.edit_message_text("Media Controls:", reply_markup=reply_markup)
    elif data == "media_play_pause":
        kb.press_and_release('play/pause media')
        await query.message.reply_text("Media Play/Pause toggled\.", parse_mode=ParseMode.MARKDOWN_V2)
    elif data == "media_next_track":
        kb.press_and_release('next track')
        await query.message.reply_text("Next track skipped\.", parse_mode=ParseMode.MARKDOWN_V2)
    elif data == "media_prev_track":
        kb.press_and_release('prev track')
        await query.message.reply_text("Previous track skipped\.", parse_mode=ParseMode.MARKDOWN_V2)
    elif data == "media_stop":
        kb.press_and_release('stop media')
        await query.message.reply_text("Media stopped\.", parse_mode=ParseMode.MARKDOWN_V2)
    elif data.startswith("browse_dir:"):
        path = data.split(":", 1)[1] # Use split with maxsplit=1 for paths that might contain colons (e.g., drive letters)
        await browse_files(update, context, path)
    elif data.startswith("download_file:"):
        file_path = data.split(":", 1)[1]
        await send_file(update, context, file_path)
    elif data == "set_brightness":
        await query.edit_message_text("Send desired brightness \(0-100\)\:", parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data['awaiting_input'] = 'brightness'
    elif data == "set_volume":
        await query.edit_message_text("Send desired volume \(0-100\)\:", parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data['awaiting_input'] = 'volume'
    elif data == "shutdown":
        await query.message.reply_text("PC will shut down in 60 seconds\. Use /cancel\_shutdown to stop\.", parse_mode=ParseMode.MARKDOWN_V2)
        subprocess.run(["shutdown", "/s", "/t", "60"])
    elif data == "cancel_shutdown":
        subprocess.run(["shutdown", "/a"])
        await query.message.reply_text("Shutdown cancelled\.", parse_mode=ParseMode.MARKDOWN_V2)
    elif data.startswith("shortcut_"):
        shortcut_name = data.split("_")[1]
        if shortcut_name == "lock":
            kb.press_and_release('windows+l')
            await query.message.reply_text("PC locked\.", parse_mode=ParseMode.MARKDOWN_V2)
        elif shortcut_name == "task_manager":
            kb.press_and_release('ctrl+shift+esc')
            await query.message.reply_text("Task Manager opened\.", parse_mode=ParseMode.MARKDOWN_V2)
        elif shortcut_name == "run":
            kb.press_and_release('windows+r')
            await query.message.reply_text("Run dialog opened\.", parse_mode=ParseMode.MARKDOWN_V2)
        elif shortcut_name == "show_desktop":
            kb.press_and_release('windows+d')
            await query.message.reply_text("Desktop shown\.", parse_mode=ParseMode.MARKDOWN_V2)
        elif shortcut_name == "maximize_window":
            kb.press_and_release('windows+up')
            await query.message.reply_text("Window maximized\.", parse_mode=ParseMode.MARKDOWN_V2)
        elif shortcut_name == "minimize_window":
            kb.press_and_release('windows+down')
            await query.message.reply_text("Window minimized\.", parse_mode=ParseMode.MARKDOWN_V2)
        elif shortcut_name == "toggle_mute":
            # Using pycaw for more reliable mute toggle
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(IAudioEndpointVolume)
                if volume:
                    current_mute = volume.GetMute()
                    volume.SetMute(not current_mute, None)
                    break
            await query.message.reply_text("Volume muted/unmuted\.", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await query.message.reply_text("Unknown shortcut\.", parse_mode=ParseMode.MARKDOWN_V2)

    elif data == "create_folder_prompt":
        current_path = context.user_data.get('current_browse_path')
        if current_path:
            await query.edit_message_text(f"Please send the name for the new folder to be created in `{escape_markdown_v2(current_path)}`:", parse_mode=ParseMode.MARKDOWN_V2)
            context.user_data['awaiting_input'] = 'new_folder_name'
        else:
            await query.answer("Could not determine current directory\. Please browse again\.", show_alert=True)
            await query.message.reply_text("Please use /browse command first to select a directory\.", parse_mode=ParseMode.MARKDOWN_V2)

    elif data.startswith("copy_file:"):
        file_path = data.split(":", 1)[1] # Use split with maxsplit=1 for paths with colons
        context.user_data['clipboard'] = {'operation': 'copy', 'file_path': file_path}
        await query.edit_message_text(
            f"File marked for Copy: `{escape_markdown_v2(os.path.basename(file_path))}`\.\n\nNow navigate to the destination and use 'Paste'\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go Back to Browse", callback_data=f"browse_dir:{os.path.dirname(file_path)}")]])
        )

    elif data.startswith("cut_file:"):
        file_path = data.split(":", 1)[1]
        context.user_data['clipboard'] = {'operation': 'cut', 'file_path': file_path}
        await query.edit_message_text(
            f"File marked for Cut: `{escape_markdown_v2(os.path.basename(file_path))}`\.\n\nNow navigate to the destination and use 'Paste'\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go Back to Browse", callback_data=f"browse_dir:{os.path.dirname(file_path)}")]])
        )


    elif data == "paste_file":
        if 'clipboard' in context.user_data and context.user_data['clipboard']:
            clipboard_data = context.user_data['clipboard']
            operation = clipboard_data['operation']
            source_path = clipboard_data['file_path']
            destination_dir = context.user_data.get('current_browse_path')

            if not destination_dir:
                await query.edit_message_text("Error: Could not determine destination directory for paste\.", parse_mode=ParseMode.MARKDOWN_V2)
                # Clear clipboard if destination is unknown
                if 'clipboard' in context.user_data: # Ensure it exists before attempting to delete
                    del context.user_data['clipboard']
                return

            try:
                dest_file_name = os.path.basename(source_path)
                destination_path = os.path.join(destination_dir, dest_file_name)

                if operation == 'copy':
                    shutil.copy2(source_path, destination_path) # copy2 preserves metadata
                    await query.edit_message_text(
                        f"Copied `{escape_markdown_v2(os.path.basename(source_path))}` to `{escape_markdown_v2(destination_dir)}`\.",
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                elif operation == 'cut':
                    shutil.move(source_path, destination_path) # move is equivalent to cut-paste
                    await query.edit_message_text(
                        f"Moved `{escape_markdown_v2(os.path.basename(source_path))}` to `{escape_markdown_v2(destination_dir)}`\.",
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                
                # Clear clipboard after successful operation
                del context.user_data['clipboard']
                # Re-browse the current directory to show changes
                await browse_files(update, context, destination_dir)

            except FileNotFoundError:
                await query.edit_message_text(f"Error: Source file not found: `{escape_markdown_v2(os.path.basename(source_path))}`\.",
                                              parse_mode=ParseMode.MARKDOWN_V2)
            except PermissionError:
                await query.edit_message_text(f"Error: Permission denied for file operation\. Could not {operation} `{escape_markdown_v2(os.path.basename(source_path))}`\.",
                                              parse_mode=ParseMode.MARKDOWN_V2)
            except shutil.SameFileError:
                 await query.edit_message_text(f"Error: Cannot {operation} file onto itself\. Source and destination are the same\.",
                                              parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                await query.edit_message_text(f"An error occurred during {operation} operation: {escape_markdown_v2(str(e))}",
                                              parse_mode=ParseMode.MARKDOWN_V2)
                
            # Always clear clipboard after attempting paste, even on error, to prevent stale state
            if 'clipboard' in context.user_data:
                del context.user_data['clipboard']
        else:
            await query.edit_message_text("No file selected for paste\. Use 'Copy' or 'Cut' first\.", parse_mode=ParseMode.MARKDOWN_V2)
            # Ensure clipboard is clear if paste was attempted without selection
            if 'clipboard' in context.user_data:
                del context.user_data['clipboard']


    elif data == "do_nothing":
        # This callback is for the file name button itself in browse_files, to provide feedback
        await query.answer("This is a file, use download, copy or cut options.", show_alert=True)

# ==================== MAIN APPLICATION SETUP ====================

def main():
    """Sets up and runs the Telegram bot application."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handlers: Respond to commands starting with '/'
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", main_menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("youtube", youtube_url))
    application.add_handler(CommandHandler("open_whatsapp", open_whatsapp))
    application.add_handler(CommandHandler("system_info", system_info))
    application.add_handler(CommandHandler("screenshot", take_screenshot))
    application.add_handler(CommandHandler("click_photo", click_photo))
    # Initial browse to C drive when /browse command is used
    application.add_handler(CommandHandler("browse", lambda u,c: browse_files(u,c,"C:\\"))) 
    application.add_handler(CommandHandler("shutdown", shutdown_pc))
    application.add_handler(CommandHandler("cancel_shutdown", cancel_shutdown))
    application.add_handler(CommandHandler("shortcuts", send_shortcut_buttons))

    # Message Handler: For incoming documents (files)
    application.add_handler(MessageHandler(filters.Document.ALL, handle_incoming_document))

    # Message Handler: For specific user inputs (like new folder name, brightness, volume)
    # This handler should have higher precedence for text messages when awaiting_input is set.
    # It catches all text messages that are NOT commands.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_specific_user_input))

    # Message Handler: For general text messages that are NOT commands and not specific inputs.
    # This should be added AFTER handle_specific_user_input so specific inputs are prioritized.
    # If handle_specific_user_input processes the message, it returns, and chatbot_response is not called.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_response))
    
    # Callback Query Handler: For all inline keyboard button presses
    application.add_handler(CallbackQueryHandler(button_handler))

    # ==================== START THE BOT ====================
    print("Bot polling started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
