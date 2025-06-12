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

# Global dictionary for predefined chatbot responses
response_dict = {
    "hello": "Hello! How are you, sir?",
    "hi": "Hi! How can I assist you today?",
    "how are you": "I'm just a bot, but I'm functioning perfectly!",
    "what is your name": "I am your friendly chatbot. You can call me ROZ!",
    "bye": "Goodbye! Have a great day!"
}

# Advanced shortcuts with descriptions for better user understanding and usability
shortcuts = {
    'copy': {'keys': 'ctrl+c', 'desc': 'Copies selected text or items'},
    'cut': {'keys': 'ctrl+x', 'desc': 'Cuts selected text or items'},
    'paste': {'keys': 'ctrl+v', 'desc': 'Pastes copied/cut content'},
    'undo': {'keys': 'ctrl+z', 'desc': 'Undoes the last action'},
    'redo': {'keys': 'ctrl+y', 'desc': 'Redoes the undone action'},
    'save': {'keys': 'ctrl+s', 'desc': 'Saves the current document'},
    'open': {'keys': 'ctrl+o', 'desc': 'Opens a file dialog'},
    'print': {'keys': 'ctrl+p', 'desc': 'Opens print dialog'},
    'select all': {'keys': 'ctrl+a', 'desc': 'Selects all content'},
    'find': {'keys': 'ctrl+f', 'desc': 'Opens find dialog'},
    'new': {'keys': 'ctrl+n', 'desc': 'Creates a new document/window'},
    'close': {'keys': 'ctrl+w', 'desc': 'Closes current tab/window'},
    'new folder': {'keys': 'ctrl+shift+n', 'desc': 'Creates a new folder'},
    'reopen closed tab': {'keys': 'ctrl+shift+t', 'desc': 'Reopens the last closed browser tab'},
    'next tab': {'keys': 'ctrl+tab', 'desc': 'Switches to the next tab'},
    'previous tab': {'keys': 'ctrl+shift+tab', 'desc': 'Switches to the previous tab'},
    'new tab': {'keys': 'ctrl+t', 'desc': 'Opens a new browser tab'},
    'underline': {'keys': 'ctrl+u', 'desc': 'Underlines selected text'},
    'bold': {'keys': 'ctrl+b', 'desc': 'Bolds selected text'},
    'italic': {'keys': 'ctrl+i', 'desc': 'Italicizes selected text'},
    'open start menu': {'keys': 'windows', 'desc': 'Opens the Start Menu'},
    'close window': {'keys': 'alt+f4', 'desc': 'Closes the active window'},
    'switch apps': {'keys': 'alt+tab', 'desc': 'Switches between open applications'},
    'window menu': {'keys': 'alt+space', 'desc': 'Opens the window system menu'},
    'show desktop': {'keys': 'windows+d', 'desc': 'Minimizes all windows to show desktop'},
    'file explorer': {'keys': 'windows+e', 'desc': 'Opens File Explorer'},
    'run': {'keys': 'windows+r', 'desc': 'Opens the Run dialog'},
    'lock computer': {'keys': 'windows+l', 'desc': 'Locks the computer'},
    'task view': {'keys': 'windows+tab', 'desc': 'Opens Task View'},
    'help': {'keys': 'f1', 'desc': 'Opens help for the active application'},
    'rename': {'keys': 'f2', 'desc': 'Renames selected item'},
    'search': {'keys': 'f3', 'desc': 'Opens search function'},
    'address bar': {'keys': 'f4', 'desc': 'Activates address bar in File Explorer/browser'},
    'refresh': {'keys': 'f5', 'desc': 'Refreshes the active window'},
    'cycle through elements': {'keys': 'f6', 'desc': 'Cycles through elements in a window or desktop'},
    'spell check': {'keys': 'f7', 'desc': 'Performs spell check'},
    'extend selection': {'keys': 'f8', 'desc': 'Enables extend mode in some applications'},
    'update fields': {'keys': 'f9', 'desc': 'Updates selected fields'},
    'activate menu': {'keys': 'f10', 'desc': 'Activates menu bar'},
    'toggle fullscreen': {'keys': 'f11', 'desc': 'Toggles full screen mode'},
    'save as': {'keys': 'f12', 'desc': 'Opens Save As dialog'},
    'cancel': {'keys': 'esc', 'desc': 'Cancels current operation'},
    'hold for uppercase': {'keys': 'shift', 'desc': 'Temporarily capitalizes letters'},
    'right-click': {'keys': 'shift+f10', 'desc': 'Simulates right-click'},
    'change case': {'keys': 'shift+f3', 'desc': 'Changes case of selected text'},
    'shrink selection': {'keys': 'shift+f8', 'desc': 'Shrinks selection in extend mode'},
    'task manager': {'keys': 'ctrl+shift+esc', 'desc': 'Opens Task Manager directly'},
    'zoom in': {'keys': 'ctrl++', 'desc': 'Zooms in'},
    'zoom out': {'keys': 'ctrl+-', 'desc': 'Zooms out'},
    'reset zoom': {'keys': 'ctrl+0', 'desc': 'Resets zoom level'},
    'clear browse data': {'keys': 'ctrl+shift+delete', 'desc': 'Opens clear Browse data dialog'},
    'new incognito window': {'keys': 'ctrl+shift+n', 'desc': 'Opens a new incognito/private browser window'},
    'private browse': {'keys': 'ctrl+shift+p', 'desc': 'Opens a new private browser window (Firefox)'},
    'navigate tabs backward': {'keys': 'ctrl+shift+tab', 'desc': 'Navigates to the previous tab'},
    'switch to next window': {'keys': 'alt+tab', 'desc': 'Switches to next window (Windows)'},
    'switch to previous window': {'keys': 'alt+shift+tab', 'desc': 'Switches to previous window (Windows)'},
    'open new tab': {'keys': 'ctrl+t', 'desc': 'Opens a new tab'},
    'open new private window': {'keys': 'ctrl+shift+p', 'desc': 'Opens a new private window'},
    'open developer tools': {'keys': 'ctrl+shift+i', 'desc': 'Opens browser developer tools'},
    'open console': {'keys': 'ctrl+shift+j', 'desc': 'Opens browser console'},
    'view page source': {'keys': 'ctrl+u', 'desc': 'Views page source'},
    'find in page': {'keys': 'ctrl+f', 'desc': 'Finds text on the current page'},
    'lock screen orientation': {'keys': 'windows+o', 'desc': 'Toggles screen orientation lock (Windows Tablet Mode)'},
    'reload': {'keys': 'f5', 'desc': 'Reloads the page'},
    'save page as': {'keys': 'ctrl+s', 'desc': 'Saves the current webpage'},
    'close current tab': {'keys': 'ctrl+w', 'desc': 'Closes the current tab'},
    'quit browser': {'keys': 'alt+f4', 'desc': 'Quits the browser (closes all windows)'},
    'backslash': {'keys': '\\', 'desc': 'Types a backslash'},
    'enter': {'keys': 'enter', 'desc': 'Confirms an action or new line'},
    'up arrow': {'keys': 'up', 'desc': 'Moves cursor/selection up'},
    'down arrow': {'keys': 'down', 'desc': 'Moves cursor/selection down'},
    'left arrow': {'keys': 'left', 'desc': 'Moves cursor/selection left'},
    'right arrow': {'keys': 'right', 'desc': 'Moves cursor/selection right'},
    'backspace': {'keys': 'backspace', 'desc': 'Deletes character before cursor'},
    'home': {'keys': 'home', 'desc': 'Moves cursor to beginning of line/page'},
    'end': {'keys': 'end', 'desc': 'Moves cursor to end of line/page'}
}

# ==================== UTILITY FUNCTIONS ====================
def escape_markdown_v2(text: str) -> str:
    """Helper function to escape special characters for MarkdownV2."""
    # List of special characters in MarkdownV2 that need to be escaped
    # Reference: https://core.telegram.org/bots/api#markdownv2-style
    # The order matters for some characters (e.g., \ before _, *, etc.)
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Checks if the user interacting with the bot is authorized based on ALLOWED_USER_ID.
    Sends an access denied message if not authorized.
    """
    user_id = update.effective_user.id
    if user_id == ALLOWED_USER_ID:
        return True
    else:
        # Determine the message object from either update.message or update.callback_query.message
        message = update.message or (update.callback_query.message if update.callback_query else None)
        if message:
            await message.reply_text("❌ Access Denied: You are not authorized to use this bot.")
        return False

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    """
    Centralized error handling to send error messages to the user and log to console.
    This helps in debugging and providing user-friendly feedback.
    """
    try:
        # Determine the message object from either update.message or update.callback_query.message
        message = update.message or (update.callback_query.message if update.callback_query else None)
        error_message_to_user = f"❌ An error occurred: {escape_markdown_v2(str(error))}\n" \
                                f"Please try again or use /help."
        if message:
            # Inform the user about the error
            await message.reply_text(error_message_to_user, parse_mode=ParseMode.MARKDOWN_V2)
        # Log the detailed error to the console for developer debugging
        print(f"Error: {error}", flush=True)
    except Exception as e:
        # If even the error handler fails, print a critical error message
        print(f"Critical error handler failure: {e}", flush=True)


# ==================== MAIN MENU & HELP COMMANDS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command, welcoming the user and displaying the main menu.
    Requires user authorization.
    """
    if not await is_authorized(update, context):
        return
        
    await update.message.reply_text(
        escape_markdown_v2("👋 Welcome to ROZ - Your Remote Control Bot! 👋\n\n"
        "I can help you control your computer remotely. "
        "Use the menu buttons below or type /help for a list of commands.\n\n"
        "To get started, try Browse files or checking system info!"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_markup # Displays the main menu keyboard
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the main menu options to the user using a ReplyKeyboardMarkup.
    ReplyKeyboards stay visible until explicitly removed or replaced.
    """
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        await message.reply_text(
            escape_markdown_v2("*Main Menu - Choose an option:*"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_markup # Displays the main menu keyboard
        )
    except Exception as e:
        await handle_error(update, context, e)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provides a comprehensive list of available commands and functionalities to the user.
    Uses MarkdownV2 for rich text formatting.
    """
    if not await is_authorized(update, context):
        return
        
    help_text = r"""*Available Commands & Features:*

*Main Menu Options:*
\- /start: Welcome message and main menu\.
\- /menu: Displays the main menu buttons\.

*File & System:*
\- /browse: Browse files and folders on your PC\.
\- /screenshot: Takes and sends a screenshot\.
\- /click\_photo: Takes and sends a photo from your webcam\.
\- /system\_info: Shows CPU, Memory, and Battery status\.
\- _Send any file to the bot to have it saved in C:\\Programs\._

*Control & Shortcuts:*
\- /shortcuts: Shows a list of common keyboard shortcuts\.
\- /open \[app\_name\]: Opens a specified application \(e\.g\.\, 'open notepad'\)\.
\- /type \[text\]: Types the given text on your PC\.
\- /press \[key\_name\]: Presses a single key \(e\.g\.\, 'press enter', 'press esc'\)\.
\- _Use 'Switch N Apps' button to switch to the Nth application in the Alt\+Tab sequence\._
\- /shutdown: Initiates PC shutdown sequence\.
\- /cancel\_shutdown: Aborts a scheduled shutdown\.

*Quick Actions \(via 'Quick Actions' menu\):*
\- Open Google, Open YouTube, Open WhatsApp, Type Text, Arrow keys, Enter, Backspace, Space, Switch N Apps\.

*System Control \(via 'System Control' menu\):*
\- Brightness adjustment, Volume adjustment, Lock PC, Shutdown PC, Restart PC, Sleep PC\.

*General Chat:*
\- Try typing 'hello', 'hi', 'how are you', 'what is your name' for a quick chat\!
    """
    # help_text is manually escaped in the multiline string above.
    
    if update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=main_menu_markup)
    else:
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=main_menu_markup)


# ==================== FILE BROWSER AND MANAGEMENT ====================
async def browse_files(update: Update, context: ContextTypes.DEFAULT_TYPE, path="C:\\"):
    """
    Allows the user to browse files and folders on the remote computer.
    It dynamically generates inline keyboard buttons for navigation and file actions,
    including creating new folders, copying, cutting, and pasting files.
    Handles permission errors and invalid paths gracefully.
    """
    if not await is_authorized(update, context):
        return
        
    try:
        # Determine the message object (from message or callback query)
        message = update.message or update.callback_query.message
        
        # Validate the provided path
        current_path = os.path.abspath(path)
        if not os.path.exists(current_path) or not os.path.isdir(current_path):
            await message.reply_text(escape_markdown_v2("⚠️ Invalid path or not a directory. Attempting to return to C:\\."), parse_mode=ParseMode.MARKDOWN_V2)
            current_path = "C:\\" # Reset to C drive if path is invalid
            # Ensure the C: drive exists for fallback
            if not os.path.exists(current_path) or not os.path.isdir(current_path):
                 await message.reply_text(escape_markdown_v2("❌ C:\\ drive not found or accessible. Cannot browse files."), parse_mode=ParseMode.MARKDOWN_V2)
                 return
        
        # Store current path in user_data for "Create Folder" and "Paste" operations
        context.user_data['current_browse_path'] = current_path

        items = []
        try:
            items = os.listdir(current_path)
        except PermissionError:
            await message.reply_text(escape_markdown_v2("⛔️ Permission denied to access this directory."), parse_mode=ParseMode.MARKDOWN_V2)
            parent = os.path.dirname(current_path)
            if parent == current_path: # If already at root and still permission denied (e.g., C:\)
                await message.reply_text(escape_markdown_v2("Cannot access any further. Please try another drive or directory."), parse_mode=ParseMode.MARKDOWN_V2)
                return
            else:
                # Recursively call browse_files to go back to the parent directory
                return await browse_files(update, context, parent) 
        except Exception as e:
            await message.reply_text(escape_markdown_v2(f"❌ Error listing directory contents: {e}"), parse_mode=ParseMode.MARKDOWN_V2)
            parent = os.path.dirname(current_path)
            if parent == current_path: # If at root and error, stop
                return
            else:
                return await browse_files(update, context, parent) # Go back to parent on error

        keyboard = []
        
        # Initialize or clear path_map for the current user's session
        if 'path_map' not in context.user_data:
            context.user_data['path_map'] = {}
        # Clear previous paths to prevent it from growing too large over time.
        # This approach assumes 'path_map' stores transient data for the current browsing session.
        # For persistent state across sessions, a more sophisticated data management approach (e.g., a database) would be needed.
        context.user_data['path_map'].clear()

        # Add drive buttons at the root level (C:\) for easy navigation between drives
        # This check is slightly refined to catch actual root drives like C:\, D:\
        is_root_drive = os.path.splitdrive(current_path)[1] == os.sep
        if is_root_drive and current_path == os.path.abspath(current_path): # Check if it's a drive root and absolute
            drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\") and os.path.isdir(f"{d}:\\")]
            if drives:
                drive_buttons = []
                for drive in drives:
                    unique_id = str(uuid.uuid4()) # Generate unique ID
                    context.user_data['path_map'][unique_id] = drive # Store mapping
                    drive_buttons.append(InlineKeyboardButton(f"💿 Drive {escape_markdown_v2(drive)}", callback_data=f"browse_id_{unique_id}"))
                keyboard.append(drive_buttons)
            else:
                keyboard.append([InlineKeyboardButton("🤷‍♂️ No drives found", callback_data="no_action")])
        
        # Add folder buttons, sorted alphabetically, with a maximum of 2 buttons per row
        folder_buttons = []
        for item in sorted(items):
            full_path = os.path.join(current_path, item)
            if os.path.isdir(full_path):
                unique_id = str(uuid.uuid4()) # Generate unique ID
                context.user_data['path_map'][unique_id] = full_path # Store mapping
                folder_buttons.append(InlineKeyboardButton(f"📁 {escape_markdown_v2(item)}", callback_data=f"browse_id_{unique_id}"))
                if len(folder_buttons) == 2: # Max 2 buttons per row for better readability
                    keyboard.append(folder_buttons)
                    folder_buttons = []
        if folder_buttons: # Add any remaining folder buttons
            keyboard.append(folder_buttons)
            
        # Add file buttons, sorted alphabetically, with appropriate icons, and Copy/Cut/Download options
        file_buttons_rows = []
        for item in sorted(items):
            full_path = os.path.join(current_path, item)
            if os.path.isfile(full_path):
                icon = "📄" # Default file icon
                ext = os.path.splitext(item)[1].lower()
                # Assign specific icons based on file extension
                if ext in ['.png', '.jpg', '.jpeg', '.gif']: icon = "🖼️"
                elif ext in ['.mp4', '.avi', '.mov', '.mkv']: icon = "🎬"
                elif ext in ['.mp3', '.wav', '.flac', '.ogg']: icon = "🎵"
                elif ext in ['.pdf']: icon = "📄"
                elif ext in ['.zip', '.rar', '.7z']: icon = "📦"
                elif ext in ['.exe', '.msi']: icon = "⚙️"
                elif ext in ['.doc', '.docx', '.odt']: icon = "📄"
                elif ext in ['.xls', '.xlsx', '.ods']: icon = "📊"
                elif ext in ['.ppt', '.pptx', '.odp']: icon = "📊"
                elif ext in ['.txt', '.log', '.ini', '.cfg', '.py', '.js', '.html', '.css', '.json', '.xml', '.md']: icon = "📝"
                
                unique_file_id = str(uuid.uuid4()) # ID for file actions
                context.user_data['path_map'][unique_file_id] = full_path # Store mapping
                
                copy_cb = f"copy_file:{full_path}" # Full path in callback data for copy/cut
                cut_cb = f"cut_file:{full_path}"
                download_cb = f"download_file:{full_path}"

                # Each file row will have the file name, Cut, Copy, and Download buttons
                file_buttons_rows.append([
                    InlineKeyboardButton(f"{icon} {escape_markdown_v2(item)}", callback_data=f"file_id_{unique_file_id}"), # File name for direct action
                    InlineKeyboardButton("✂️ Cut", callback_data=cut_cb),
                    InlineKeyboardButton("📋 Copy", callback_data=copy_cb),
                    InlineKeyboardButton("⬇️ Download", callback_data=download_cb)
                ])
        
        keyboard.extend(file_buttons_rows) # Add all file rows to the main keyboard

        # Navigation and Action buttons: Parent Directory and Go to C:\
        nav_buttons = []
        parent = os.path.dirname(current_path)
        # If not at root, show parent directory button
        # and ensure parent is not the same as current_path (e.g., C:\'s parent is C:\)
        if parent != current_path: 
            unique_id = str(uuid.uuid4()) # Generate unique ID for parent
            context.user_data['path_map'][unique_id] = parent # Store mapping
            nav_buttons.append(InlineKeyboardButton("⬆️ Parent Directory", callback_data=f"browse_id_{unique_id}"))
        
        # Add "Go to C:\" button if not already at C:\
        if current_path != "C:\\":
            unique_id = str(uuid.uuid4()) # Generate unique ID for C:\
            context.user_data['path_map'][unique_id] = "C:\\" # Store mapping
            nav_buttons.append(InlineKeyboardButton("🏠 Go to C:\\", callback_data=f"browse_id_{unique_id}"))
            
        if nav_buttons:
            keyboard.append(nav_buttons)
            
        # Add "Create Folder" button
        keyboard.append([InlineKeyboardButton("➕ Create New Folder", callback_data="create_folder_prompt")])

        # Add "Paste" button if something is in clipboard
        if 'clipboard' in context.user_data and context.user_data['clipboard']:
            keyboard.append([InlineKeyboardButton("✅ Paste", callback_data="paste_file")])

        # Always provide a way back to the main menu
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu_callback")])
        
        # Use ParseMode.MARKDOWN_V2 and escape the path
        display_path = escape_markdown_v2(current_path)

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit the message if it's a callback query to prevent multiple messages and keep chat clean
        if update.callback_query:
            await message.edit_text(
                f"📂 Current Directory: `{display_path}`\n\nChoose an action:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            # If it's a new message (e.g., from /browse command), send a new one
            await message.reply_text(
                f"📂 Current Directory: `{display_path}`\n\nChoose an action:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        
    except Exception as e:
        await handle_error(update, context, e)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """
    Handles requests to open or send a specific file to the user.
    Provides options like download, read content, or run script based on file type.
    """
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.callback_query.message
        
        if not os.path.exists(file_path):
            await message.reply_text(escape_markdown_v2("⚠️ File not found."), parse_mode=ParseMode.MARKDOWN_V2)
            # Optionally, re-show the current directory after a file not found error
            parent_dir = os.path.dirname(file_path)
            await browse_files(update, context, parent_dir if parent_dir else "C:\\")
            return

        # Check file size before attempting any action
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(escape_markdown_v2(f"⚠️ File too large (max {MAX_FILE_SIZE / (1024*1024):.0f}MB). This file is {file_size / (1024*1024):.2f}MB."), parse_mode=ParseMode.MARKDOWN_V2)
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path) # Get base file name for display

        # Handle different file types: send directly or offer options
        # Use InlineKeyboardMarkup buttons for actions on files
        
        # Generate unique IDs for actions on this specific file
        unique_download_id = str(uuid.uuid4())
        context.user_data['path_map'][unique_download_id] = file_path
        unique_read_id = str(uuid.uuid4())
        context.user_data['path_map'][unique_read_id] = file_path
        unique_run_id = str(uuid.uuid4())
        context.user_data['path_map'][unique_run_id] = file_path

        keyboard = []

        # Always offer download
        keyboard.append([InlineKeyboardButton(f"⬇️ Download `{escape_markdown_v2(file_name)}`", callback_data=f"download_file_id_{unique_download_id}")])

        if ext in ['.txt', '.log', '.csv', '.html', '.css', '.json', '.xml', '.md', '.ini', '.cfg', '.py', '.js']: 
            # Offer choice to read content for text-based files
            keyboard.append([InlineKeyboardButton(f"📝 Read Content of `{escape_markdown_v2(file_name)}`", callback_data=f"read_content_id_{unique_read_id}")])
        
        if ext in ['.py', '.js']: # Specific handling for executable scripts: run
            keyboard.append([InlineKeyboardButton(f"▶️ Run `{escape_markdown_v2(file_name)}`", callback_data=f"run_file_id_{unique_run_id}")])

        # Add a back button to the current directory
        keyboard.append([InlineKeyboardButton("🔙 Back to Browse", callback_data=f"browse_dir:{os.path.dirname(file_path)}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.edit_text(
            f"What would you like to do with `{escape_markdown_v2(file_name)}`?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
            
    except Exception as e:
        await handle_error(update, context, e)

async def run_script_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """
    Executes a Python or JavaScript file on the remote PC.
    Captures stdout and stderr and sends it back to the user.
    Includes timeout for script execution.
    """
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.callback_query.message
        
        if not os.path.exists(file_path):
            await message.reply_text(escape_markdown_v2("⚠️ File not found."), parse_mode=ParseMode.MARKDOWN_V2)
            return

        ext = os.path.splitext(file_path)[1].lower()
        
        # Determine the interpreter based on file extension
        command = []
        if ext == '.py':
            command = ['python', file_path]
            await message.reply_text(escape_markdown_v2(f"▶️ Running Python script: `{os.path.basename(file_path)}`..."), parse_mode=ParseMode.MARKDOWN_V2)
        elif ext == '.js':
            command = ['node', file_path] # Requires Node.js to be installed and in PATH
            await message.reply_text(escape_markdown_v2(f"▶️ Running JavaScript file (requires Node.js): `{os.path.basename(file_path)}`..."), parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await message.reply_text(escape_markdown_v2("⚠️ This file type cannot be run directly."), parse_mode=ParseMode.MARKDOWN_V2)
            return

        # Execute the script using subprocess.Popen to avoid blocking the bot
        # and capture output (stdout and stderr)
        process = subprocess.Popen(command, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   encoding='utf-8')
        stdout, stderr = process.communicate(timeout=30) # Set a 30-second timeout for script execution
        
        response = ""
        if stdout:
            response += f"```\n{escape_markdown_v2(stdout)}\n```"
        if stderr:
            response += f"❌ Error:\n```\n{escape_markdown_v2(stderr)}\n```"
        if not stdout and not stderr:
            response = escape_markdown_v2("✅ Script executed successfully with no output.")
            
        await message.reply_text(f"Script output for `{escape_markdown_v2(os.path.basename(file_path))}`:\n{response}", parse_mode=ParseMode.MARKDOWN_V2)

    except subprocess.TimeoutExpired:
        # Handle cases where the script takes too long to execute
        process.kill() # Terminate the process if it times out
        await message.reply_text(escape_markdown_v2(f"⏰ Script execution timed out for `{os.path.basename(file_path)}`."), parse_mode=ParseMode.MARKDOWN_V2)
    except FileNotFoundError:
        # Handle cases where the interpreter (python or node) is not found
        await message.reply_text(escape_markdown_v2(f"❌ Error: Python/Node.js executable not found. Make sure they are installed and in your system's PATH."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)


# ==================== SYSTEM CONTROL & PC ACTIONS ====================
async def shutdown_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Prompts the user for confirmation before shutting down the PC,
    offering immediate, timed, or cancel options.
    """
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        
        keyboard = [
            [InlineKeyboardButton("✅ Yes, shutdown immediately", callback_data="confirm_shutdown")],
            [InlineKeyboardButton("⏰ Shutdown in 60 seconds", callback_data="shutdown_60s")],
            [InlineKeyboardButton("❌ Cancel Shutdown", callback_data="cancel_shutdown_inline")] # Renamed to avoid clash with command
        ]
        
        await message.reply_text(
            escape_markdown_v2("⚠️ *Are you sure you want to shutdown the PC?*"),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        await handle_error(update, context, e)

async def confirm_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes an immediate PC shutdown command."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.callback_query.message
        await message.edit_text(escape_markdown_v2("🖥️ Shutting down PC NOW... Goodbye!"), parse_mode=ParseMode.MARKDOWN_V2)
        os.system("shutdown /s /t 1")  # Immediate shutdown command for Windows
    except Exception as e:
        await handle_error(update, context, e)

async def shutdown_60s(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Schedules PC shutdown in 60 seconds."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.callback_query.message
        await message.edit_text(escape_markdown_v2("🖥️ PC will shutdown in 60 seconds. You can cancel with /cancel_shutdown."), parse_mode=ParseMode.MARKDOWN_V2)
        os.system("shutdown /s /t 60") # Schedule shutdown after 60 seconds
    except Exception as e:
        await handle_error(update, context, e)

async def cancel_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aborts any scheduled PC shutdown (used by /command)."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.message or update.callback_query.message # Can be called by command or inline button
        os.system("shutdown /a") # Abort shutdown command for Windows
        await message.reply_text(escape_markdown_v2("✅ Scheduled shutdown has been cancelled."), parse_mode=ParseMode.MARKDOWN_V2)
        if update.callback_query: # If from inline button, also edit the original message
            await update.callback_query.edit_message_reply_markup(reply_markup=None) # Remove buttons
    except Exception as e:
        await handle_error(update, context, e)

async def cancel_shutdown_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aborts any scheduled PC shutdown (used by inline button)."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.callback_query.message
        os.system("shutdown /a") # Abort shutdown command for Windows
        await message.edit_text(escape_markdown_v2("✅ Scheduled shutdown has been cancelled."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)


async def open_application(update: Update, context: ContextTypes.DEFAULT_TYPE, app_name: str):
    """
    Opens an application on the remote PC by simulating Windows key + typing the app name.
    Takes a screenshot afterwards to confirm.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        kb.press_and_release('windows')
        time.sleep(0.5)
        kb.write(app_name)
        time.sleep(1)
        kb.press_and_release('enter')
        await message.reply_text(escape_markdown_v2(f"✅ Attempted to open: *{app_name.title()}*"), parse_mode=ParseMode.MARKDOWN_V2)
        await take_screenshot(update, context) # Confirm with a screenshot
    except Exception as e:
        await handle_error(update, context, e)

async def type_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text_to_type: str):
    """
    Types the given text on the remote PC using keyboard simulation.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        pyperclip.copy(text_to_type) # Copy text to clipboard
        kb.press_and_release('ctrl+v') # Paste it
        await message.reply_text(escape_markdown_v2("✅ Typing completed successfully."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    """
    Presses a single key or a shortcut combination on the remote PC using `keyboard` library.
    Supports both direct key names and defined shortcut names.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        # Normalize key input for consistent processing
        key = key.lower().replace(" ", "")
        
        keys_to_press = key # Default to direct key name
        # Check if the input matches a known shortcut name or its key combination
        for shortcut_name, shortcut_info in shortcuts.items():
            if key == shortcut_name.lower().replace(" ", "") or key == shortcut_info['keys'].lower().replace(" ", ""):
                keys_to_press = shortcut_info['keys']
                break

        kb.press_and_release(keys_to_press)
        await message.reply_text(escape_markdown_v2(f"✅ Pressed key(s): `{keys_to_press}` successfully."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Retrieves and sends detailed system information like battery status,
    CPU/memory usage, disk space, network activity, and system uptime.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        info_text = escape_markdown_v2("🖥️ *System Information:*\n")
        
        # Battery Information
        battery = psutil.sensors_battery()
        if battery:
            plugged_status = escape_markdown_v2("Plugged In ⚡") if battery.power_plugged else escape_markdown_v2("Not Plugged In")
            time_left = ""
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                minutes, seconds = divmod(battery.secsleft, 60)
                hours, minutes = divmod(minutes, 60)
                time_left = escape_markdown_v2(f", Est. {int(hours)}h {int(minutes)}m remaining")
            info_text += escape_markdown_v2(f"- Battery: `{battery.percent}%` ({plugged_status}{time_left})\n")
        else:
            info_text += escape_markdown_v2("- Battery: `Information not available`\n")
        
        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1) # Measures CPU usage over 1 second
        info_text += escape_markdown_v2(f"- CPU Usage: `{cpu_usage}%`\n")
        
        # Memory Usage
        memory = psutil.virtual_memory()
        info_text += escape_markdown_v2(f"- Memory Usage: `{memory.percent}%` (`{memory.used / (1024**3):.2f} GB` / `{memory.total / (1024**3):.2f} GB`)\n")

        # Disk Usage (specifically for C: drive)
        try:
            disk_c = psutil.disk_usage('C:\\')
            info_text += escape_markdown_v2(f"- C:\\ Disk Usage: `{disk_c.percent}%` (`{disk_c.used / (1024**3):.2f} GB` / `{disk_c.total / (1024**3):.2f} GB`)\n")
        except Exception:
            info_text += escape_markdown_v2("- C:\\ Disk Usage: `Information not available`\n")

        # Network I/O (bytes sent/received)
        net_io = psutil.net_io_counters()
        info_text += escape_markdown_v2(f"- Network (Sent/Recv): `{net_io.bytes_sent / (1024**2):.2f} MB` / `{net_io.bytes_recv / (1024**2):.2f} MB`\n")

        # System Uptime
        boot_time_timestamp = psutil.boot_time()
        boot_time_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time_timestamp))
        info_text += escape_markdown_v2(f"- Last Boot: `{boot_time_readable}`\n")
        
        await message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Takes a screenshot of the remote PC's display and sends it to the user.
    Cleans up the temporary screenshot file afterwards.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        screenshot_path = "screenshot.png"
        screenshot = pyautogui.screenshot() # Uses Pillow for screenshot
        screenshot.save(screenshot_path)
        
        await message.reply_text(escape_markdown_v2("📸 Taking screenshot..."), parse_mode=ParseMode.MARKDOWN_V2)
        await message.reply_photo(photo=open(screenshot_path, "rb"))
        os.remove(screenshot_path)  # Clean up the saved screenshot file
    except Exception as e:
        await handle_error(update, context, e)

async def click_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Takes a photo using the default webcam and sends it to the user.
    Handles cases where no webcam is detected or is in use.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        photo_path = "webcam_photo.jpg"
        camera = cv2.VideoCapture(0) # 0 is typically the default webcam ID
        
        if not camera.isOpened():
            await message.reply_text(escape_markdown_v2("⚠️ No webcam detected or it is in use by another application."), parse_mode=ParseMode.MARKDOWN_V2)
            return

        time.sleep(1) # Give camera a moment to initialize and adjust
        return_value, image = camera.read() # Read a frame from the camera
        
        if return_value:
            cv2.imwrite(photo_path, image) # Save the captured image
            await message.reply_text(escape_markdown_v2("📷 Photo clicked successfully. Sharing it with you..."), parse_mode=ParseMode.MARKDOWN_V2)
            await message.reply_photo(photo=open(photo_path, "rb"))
            os.remove(photo_path)  # Clean up the photo file
        else:
            await message.reply_text(escape_markdown_v2("Failed to capture photo. Ensure your camera is connected and not in use."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)
    finally:
        # Ensure the camera resource is released even if an error occurs
        if 'camera' in locals() and camera.isOpened():
            camera.release()
        cv2.destroyAllWindows() # Close any OpenCV windows (though not usually created in this use case)

async def youtube_url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a YouTube link to the user and opens it in the default browser on the remote PC.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    webbrowser.open("https://www.youtube.com") # Open on PC
    await message.reply_text("YouTube opened in your default browser.", parse_mode=ParseMode.MARKDOWN_V2)


async def open_whatsapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Opens WhatsApp application on the remote PC by simulating Windows key + typing 'WhatsApp'.
    """
    if not await is_authorized(update, context): return
    message = update.message if update.message else update.callback_query.message
    try:
        kb.press_and_release('windows')
        time.sleep(0.5) # Short delay for start menu to appear
        kb.write('WhatsApp')
        time.sleep(1) # Delay for search results
        kb.press_and_release('enter')
        await message.reply_text(escape_markdown_v2("✅ WhatsApp opened successfully."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

# System control actions (keyboard simulations for various functions)
async def show_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Windows+Tab to show the Task View (all open applications)."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("windows+tab")
        await update.message.reply_text(escape_markdown_v2("✅ Show application."), parse_mode=ParseMode.MARKDOWN_V2)
        await take_screenshot(update, context) # Provide visual confirmation
    except Exception as e: await handle_error(update, context, e)

async def initiate_multi_app_swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the process to switch to the Nth open application by asking for user input.
    Sets a flag in `user_data` to await the number input.
    """
    if not await is_authorized(update, context): return
    try:
        context.user_data['awaiting_multi_app_swap_input'] = True
        await update.message.reply_text(
            escape_markdown_v2("Please enter the number of applications you want to switch through (e.g., 3 for the 3rd app):"),
            reply_markup=ReplyKeyboardRemove(), # Temporarily remove the ReplyKeyboard to allow free text input
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        await handle_error(update, context, e)

async def swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Alt+Tab to switch to the next open application."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("alt+tab")
        await update.message.reply_text(escape_markdown_v2("✅ Switched application."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def change_tab_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Tab to switch to the next browser tab."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+tab")
        await update.message.reply_text(escape_markdown_v2("✅ Switched to next tab."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def change_tab_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Shift+Tab to switch to the previous browser tab."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+shift+tab")
        await update.message.reply_text(escape_markdown_v2("✅ Switched to previous tab."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def press_enter_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Enter key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("enter")
        await update.message.reply_text(escape_markdown_v2("✅ 'Enter' key pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def press_space_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Spacebar."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("space")
        await update.message.reply_text(escape_markdown_v2("✅ 'Space' key pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def refresh_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates F5 to refresh the current window."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("f5")
        await update.message.reply_text(escape_markdown_v2("✅ Window refreshed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def press_tab_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Tab key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("tab")
        await update.message.reply_text(escape_markdown_v2("✅ 'Tab' key pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def arrow_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Up arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("up")
        await update.message.reply_text(escape_markdown_v2("⬆️ 'Up' arrow pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def arrow_down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Down arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("down")
        await update.message.reply_text(escape_markdown_v2("⬇️ 'Down' arrow pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def arrow_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Left arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("left")
        await update.message.reply_text(escape_markdown_v2("⬅️ 'Left' arrow pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def arrow_right(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Right arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("right")
        await update.message.reply_text(escape_markdown_v2("➡️ 'Right' arrow pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)
    
async def press_backspace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Backspace key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("backspace")
        await update.message.reply_text(escape_markdown_v2("� 'Backspace' pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def press_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Home key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("home")
        await update.message.reply_text(escape_markdown_v2("✅ 'Home' key pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def press_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the End key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("end")
        await update.message.reply_text(escape_markdown_v2("✅ 'End' key pressed."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def zoom_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl++ to zoom in."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+plus") # 'plus' key for '+'
        await update.message.reply_text(escape_markdown_v2("✅ Zoomed In."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def zoom_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+- to zoom out."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+-")
        await update.message.reply_text(escape_markdown_v2("✅ Zoomed Out."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def undo_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Z for undo."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+z")
        await update.message.reply_text(escape_markdown_v2("✅ Undo action triggered."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def redo_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Y for redo."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+y")
        await update.message.reply_text(escape_markdown_v2("✅ Redo action triggered."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e: await handle_error(update, context, e)

async def increase_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Increases the screen brightness by 10% steps, up to 100%.
    Requires `screen_brightness_control` library.
    """
    if not await is_authorized(update, context): return
    try:
        current_brightness = sbc.get_brightness()[0] # get_brightness returns a list
        new_brightness = min(current_brightness + 10, 100) # Ensure brightness doesn't exceed 100
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(escape_markdown_v2(f"🔆 Brightness increased to: `{new_brightness}%`"), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def decrease_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Decreases the screen brightness by 10% steps, down to 0%.
    Requires `screen_brightness_control` library.
    """
    if not await is_authorized(update, context): return
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = max(current_brightness - 10, 0) # Ensure brightness doesn't go below 0
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(escape_markdown_v2(f"🔆 Brightness decreased to: `{new_brightness}%`"), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Increases the system master volume by 10% steps, up to 100%.
    Requires `pycaw` library.
    """
    if not await is_authorized(update, context): return
    try:
        devices = AudioUtilities.GetSpeakers()
        # Activate the volume interface
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar() # Volume as a scalar (0.0 to 1.0)
        new_volume = min(current_volume + 0.10, 1.0) # Increase by 0.1 (10%)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        await update.message.reply_text(escape_markdown_v2(f"🔊 Volume increased to: `{new_volume * 100:.0f}%`"), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Decreases the system master volume by 10% steps, down to 0%.
    Requires `pycaw` library.
    """
    if not await is_authorized(update, context): return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.10, 0.0) # Decrease by 0.1 (10%)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        await update.message.reply_text(escape_markdown_v2(f"🔉 Volume decreased to: `{new_volume * 100:.0f}%`"), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def lock_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Locks the PC by running a Windows system command.
    """
    if not await is_authorized(update, context): return
    try:
        message = update.message if update.message else update.callback_query.message
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        await message.reply_text(escape_markdown_v2("🔒 PC has been locked."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

async def restart_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Prompts the user for confirmation before restarting the PC.
    """
    if not await is_authorized(update, context): return
    try:
        message = update.message or update.callback_query.message
        keyboard = [
            [InlineKeyboardButton("✅ Yes, restart now", callback_data="confirm_restart")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_restart_inline")]
        ]
        await message.reply_text(
            escape_markdown_v2("⚠️ Are you sure you want to restart the PC?"),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        await handle_error(update, context, e)

async def confirm_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes the PC restart command immediately."""
    if not await is_authorized(update, context): return
    try:
        message = update.callback_query.message
        await message.edit_text(escape_markdown_v2("🔄 Restarting PC NOW..."), parse_mode=ParseMode.MARKDOWN_V2)
        os.system("shutdown /r /t 1") # Immediate restart command
    except Exception as e:
        await handle_error(update, context, e)

async def cancel_restart_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels any pending PC restart initiated by inline button."""
    if not await is_authorized(update, context): return
    try:
        message = update.callback_query.message
        await message.edit_text(escape_markdown_v2("✅ Restart cancelled."), parse_mode=ParseMode.MARKDOWN_V2) 
    except Exception as e:
        await handle_error(update, context, e)

async def sleep_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Puts the PC into sleep mode by running a Windows system command.
    """
    if not await is_authorized(update, context): return
    try:
        message = update.message if update.message else update.callback_query.message
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        await message.reply_text(escape_markdown_v2("💤 PC is going to sleep..."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)

# Handler for receiving files with categorization
async def handle_incoming_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles incoming documents from the user, checks authorization,
    creates target directories if needed, and saves the file to
    a categorized directory based on its file type (extension).
    """
    if not await is_authorized(update, context):
        return

    document = update.message.document
    file_name = document.file_name
    file_extension = os.path.splitext(file_name)[1].lower()

    target_directory = OTHER_FILES_DIR
    file_type_description = "other file"

    # Define common code/text file extensions
    code_extensions = ['.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.txt', '.log', '.ini', '.cfg', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.go', '.rb', '.sh', '.bat', '.ps1']
    
    # Categorize the file based on its extension
    if file_extension in code_extensions:
        target_directory = CODE_FILES_DIR
        file_type_description = "code/text file"
    elif file_extension == '.pdf':
        target_directory = PDF_FILES_DIR
        file_type_description = "PDF file"
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        target_directory = IMAGE_FILES_DIR
        file_type_description = "image file"
    elif file_extension in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']:
        target_directory = VIDEO_FILES_DIR
        file_type_description = "video file"
    elif file_extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
        target_directory = AUDIO_FILES_DIR
        file_type_description = "audio file"
    
    # Ensure the target directory exists, create it if it doesn't
    os.makedirs(target_directory, exist_ok=True)

    file_path = os.path.join(target_directory, file_name)

    try:
        # Check file size against MAX_FILE_SIZE limit before downloading
        if document.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                escape_markdown_v2(f"⚠️ File too large (max {MAX_FILE_SIZE / (1024*1024):.0f}MB). This file is {document.file_size / (1024*1024):.2f}MB."),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        # Download the file to the specified path
        new_file = await context.bot.get_file(document.file_id)
        await new_file.download_to_drive(custom_path=file_path)
        await update.message.reply_text(escape_markdown_v2(f"✅ Your {file_type_description} '{file_name}' saved successfully to `{target_directory}`."), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await handle_error(update, context, e)


async def chatbot_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles general text messages from the user and routes them to appropriate functions
    based on keywords or specific commands, or provides a predefined conversational response.
    Also manages state for multi-step interactions (e.g., 'Type Text', 'Switch N Apps').
    """
    if not await is_authorized(update, context):
        return

    query_text = update.message.text # Original text for direct matching
    query_lower = query_text.lower().strip() # Lowercase and strip for consistent matching

    # --- Handle state-based interactions (highest priority) ---

    # Handle input for 'Switch N Apps' feature
    if context.user_data.get('awaiting_multi_app_swap_input'):
        try:
            num_apps = int(query_lower)
            if num_apps < 1:
                await update.message.reply_text(escape_markdown_v2("Please enter a positive number."), parse_mode=ParseMode.MARKDOWN_V2)
                return
            
            # Simulate Alt+Tab presses
            kb.press('alt')
            # Press tab num_apps times, then release alt
            for _ in range(num_apps):
                kb.press_and_release('tab')
                time.sleep(0.1) # Small delay to ensure each tab press registers
            kb.release('alt')

            await update.message.reply_text(escape_markdown_v2(f"✅ Switched application by pressing Tab {num_apps} time(s)."), parse_mode=ParseMode.MARKDOWN_V2)
            await take_screenshot(update, context) # Take screenshot immediately after switching apps
            context.user_data['awaiting_multi_app_swap_input'] = False # Reset flag
            await update.message.reply_text(escape_markdown_v2("What next, sir?"), reply_markup=quick_actions_markup, parse_mode=ParseMode.MARKDOWN_V2) # Show quick actions again
            return # Exit after handling this specific input
        except ValueError:
            await update.message.reply_text(escape_markdown_v2("Invalid input. Please enter a number."), parse_mode=ParseMode.MARKDOWN_V2)
            return
        except Exception as e:
            await handle_error(update, context, e)
            context.user_data['awaiting_multi_app_swap_input'] = False # Reset flag on error
            return

    # Handle input for 'Type Text' feature
    elif context.user_data.get('awaiting_text_input'):
        text_to_type = query_text # Use original case for typing
        await type_text(update, context, text_to_type)
        context.user_data['awaiting_text_input'] = False # Reset flag
        await update.message.reply_text(escape_markdown_v2("What next, sir?"), reply_markup=quick_actions_markup, parse_mode=ParseMode.MARKDOWN_V2) # Show quick actions again
        return # Exit after handling this specific input
        
    # --- Handle ReplyKeyboard button presses (second priority) ---
    # These match the exact text of the buttons in the ReplyKeyboardMarkup
    elif query_text == "📁 Browse Files":
        await browse_files(update, context, "C:\\") # Start browsing from C drive
    elif query_text == "🖥️ System Info":
        await system_info(update, context)
    elif query_text == "📸 Screenshot":
        await take_screenshot(update, context)
    elif query_text == "📷 Click Photo":
        await click_photo(update, context)
    elif query_text == "⚡ Shortcuts":
        await send_shortcut_buttons(update, context)
    elif query_text == "🚀 Quick Actions":
        await update.message.reply_text(escape_markdown_v2("⚡ *Quick Actions Menu:*"), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=quick_actions_markup)
    elif query_text == "⚙️ System Control":
        await update.message.reply_text(escape_markdown_v2("⚙️ *System Control Menu:*"), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=system_control_markup)
    elif query_text == "ℹ️ Help":
        await help_command(update, context)
    elif query_text == "⏪ Main Menu":
        await main_menu(update, context)
    elif query_text == "🌐 Open Google":
        webbrowser.open("https://www.google.com")
        await update.message.reply_text(escape_markdown_v2("✅ Opened Google in browser."), parse_mode=ParseMode.MARKDOWN_V2)
    elif query_text == "📝 Type Text":
        await update.message.reply_text(escape_markdown_v2("Please reply to this message with the text you want me to type."),
                                        reply_markup=ReplyKeyboardRemove(), # Remove buttons to get free text input
                                        parse_mode=ParseMode.MARKDOWN_V2) 
        context.user_data['awaiting_text_input'] = True # Set flag to await next message as text input
    elif query_text == "⬆️ Up":
        await arrow_up(update, context)
    elif query_text == "⬇️ Down":
        await arrow_down(update, context)
    elif query_text == "⬅️ Left":
        await arrow_left(update, context)
    elif query_text == "➡️ Right":
        await arrow_right(update, context)
    elif query_text == "↩️ Enter":
        await press_enter_key(update, context)
    elif query_text == "🔙 Backspace":
        await press_backspace(update, context)
    elif query_text == "Space":
        await press_space_key(update, context)
    elif query_text == "🔆 Brightness +":
        await increase_brightness(update, context)
    elif query_text == "🔆 Brightness -":
        await decrease_brightness(update, context)
    elif query_text == "🔊 Volume +":
        await increase_volume(update, context)
    elif query_text == "🔉 Volume -":
        await decrease_volume(update, context)
    elif query_text == "🔒 Lock PC":
        await lock_pc(update, context)
    elif query_text == "🖥️ Shutdown PC":
        await shutdown_pc(update, context)
    elif query_text == "🔄 Restart PC":
        await restart_pc(update, context)
    elif query_text == "💤 Sleep PC":
        await sleep_pc(update, context)
    elif query_text == "🔃 Swap":
        await swap(update, context)
    elif query_text == "📲 Show Apps":
        await show_apps(update, context)
    elif query_text == "🔄 Switch N Apps": # New button handler for multi-app swap
        await initiate_multi_app_swap(update, context)
    elif query_text == "🔁 Next Tab":
        await change_tab_next(update, context)
    elif query_text == "🔁 Prev Tab":
        await change_tab_prev(update, context)
    elif query_text == "TAB": # Direct input for tab key
        await press_tab_key(update, context)
    elif query_text == "Refress": # Typo in original code, assuming it means "Refresh"
        await refresh_window(update, context)
    elif query_text == "Home":
        await press_home(update, context)
    elif query_text == "End":
        await press_end(update, context)
    elif query_text == "🔍 Zoom IN":
        await zoom_in(update, context)
    elif query_text == "🔎 Zoom OUT":
        await zoom_out(update, context)
    elif query_text == "Undu": # Typo in original code, assuming it means "Undo"
        await undo_action(update, context)
    elif query_text == "Redu": # Typo in original code, assuming it means "Redo"
        await redo_action(update, context)
    
    # --- Handle specific text commands (parsed by prefix - third priority) ---
    elif query_lower.startswith("open "):
        app_name = query_text[len("open "):] # Use query_text to preserve case for app name
        await open_application(update, context, app_name)
    elif query_lower.startswith("type ") or query_lower.startswith("write "):
        text_to_type = query_text.replace("type ", "", 1).replace("write ", "", 1).strip() # Use query_text
        await type_text(update, context, text_to_type)
    elif query_lower.startswith("press "):
        key_command = query_lower[len("press "):] # Use query_lower for key command
        await press_key(update, context, key_command)
    elif query_lower.startswith('google '):
        search_query = query_lower[len('google '):]
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        await update.message.reply_text(escape_markdown_v2(f"✅ Searching Google for: `{search_query}`"), parse_mode=ParseMode.MARKDOWN_V2)
    elif query_lower.startswith('youtube '):
        search_query = query_lower[len('youtube '):]
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
        await update.message.reply_text(escape_markdown_v2(f"✅ Searching YouTube for: `{search_query}`"), parse_mode=ParseMode.MARKDOWN_V2)
    
    # --- Handle general chatbot responses for unrecognized input (lowest priority) ---
    else:
        # Provide a predefined response or query the LLM
        response = response_dict.get(query_lower)
        if response:
            await update.message.reply_text(escape_markdown_v2(response), reply_markup=main_menu_markup, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            # Fallback to LLM if no other handler or predefined response matches
            chat_history = []
            chat_history.append({"role": "user", "parts": [{"text": query_text}]}) # Use original text for LLM

            payload = {"contents": chat_history}
            
            try:
                await update.message.reply_text(escape_markdown_v2("Thinking..."), parse_mode=ParseMode.MARKDOWN_V2) # Provide immediate feedback

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        API_URL_TEXT_GEN,
                        json=payload,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                    result = response.json()
                
                if result.get("candidates") and \
                   result["candidates"][0].get("content") and \
                   result["candidates"][0]["content"].get("parts"):
                    llm_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    await update.message.reply_text(escape_markdown_v2(llm_text), reply_markup=main_menu_markup, parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    await update.message.reply_text(escape_markdown_v2("Sorry, I could not generate a response. Please try again."), reply_markup=main_menu_markup, parse_mode=ParseMode.MARKDOWN_V2)

            except httpx.RequestError as exc:
                await update.message.reply_text(escape_markdown_v2(f"An error occurred while connecting to the LLM: {exc}"), reply_markup=main_menu_markup, parse_mode=ParseMode.MARKDOWN_V2)
            except httpx.HTTPStatusError as exc:
                await update.message.reply_text(escape_markdown_v2(f"LLM API returned an error {exc.response.status_code}: {exc.response.text}"), reply_markup=main_menu_markup, parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                await update.message.reply_text(escape_markdown_v2(f"An unexpected error occurred while generating response: {e}"), reply_markup=main_menu_markup, parse_mode=ParseMode.MARKDOWN_V2)

# ==================== REPLY KEYBOARD MARKUPS ====================
# These keyboards stay visible until explicitly removed or replaced.
main_menu_markup = ReplyKeyboardMarkup([
    [KeyboardButton("📁 Browse Files"), KeyboardButton("🖥️ System Info")],
    [KeyboardButton("📸 Screenshot"), KeyboardButton("📷 Click Photo")],
    [KeyboardButton("⚡ Shortcuts"), KeyboardButton("🚀 Quick Actions")],
    [KeyboardButton("⚙️ System Control"), KeyboardButton("ℹ️ Help")]
], resize_keyboard=True, one_time_keyboard=False, is_persistent=True) # is_persistent keeps it visible always

quick_actions_markup = ReplyKeyboardMarkup([
    [KeyboardButton("🌐 Open Google"), KeyboardButton("📝 Type Text")],
    [KeyboardButton("🔃 Swap"), KeyboardButton("📲 Show Apps"), KeyboardButton("🔄 Switch N Apps")],
    [KeyboardButton("⬆️ Up"), KeyboardButton("⬇️ Down"), KeyboardButton("⬅️ Left"), KeyboardButton("➡️ Right")],
    [KeyboardButton("↩️ Enter"), KeyboardButton("🔙 Backspace"), KeyboardButton("Space")],
    [KeyboardButton("⏪ Main Menu")]
], resize_keyboard=True, one_time_keyboard=False, is_persistent=True)

system_control_markup = ReplyKeyboardMarkup([
    [KeyboardButton("🔆 Brightness +"), KeyboardButton("🔆 Brightness -")],
    [KeyboardButton("🔊 Volume +"), KeyboardButton("🔉 Volume -")],
    [KeyboardButton("🔒 Lock PC"), KeyboardButton("🖥️ Shutdown PC")],
    [KeyboardButton("🔄 Restart PC"), KeyboardButton("💤 Sleep PC")],
    [KeyboardButton("⏪ Main Menu")]
], resize_keyboard=True, one_time_keyboard=False, is_persistent=True)


# ==================== REGISTER HANDLERS ====================
def main():
    """Sets up and runs the Telegram bot application."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handlers: Respond to commands starting with '/'
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", main_menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("youtube", youtube_url_command)) # Renamed to avoid conflict
    application.add_handler(CommandHandler("open_whatsapp", open_whatsapp_command)) # Renamed to avoid conflict
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

    # Message Handler: For specific user inputs (like new folder name, brightness, volume, multi-app swap, type text)
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
    print("✅ Bot is starting...")
    # Start polling for updates from Telegram API
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
