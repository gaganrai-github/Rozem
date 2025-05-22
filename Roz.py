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

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7070124825:AAFSnUIo0c-b_7dsMj8fFL_rUILLL3i7ab8")
ALLOWED_USER_ID = 5285057277  # Replace with your Telegram user ID
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB max file size for transfers

# NEW: Define specific target directories for categorization
BASE_PROGRAMS_DIR = "C:\\Programs"
CODE_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Code")
OTHER_FILES_DIR = os.path.join(BASE_PROGRAMS_DIR, "Other")

# Initialize the Application with your bot token
app = Application.builder().token(BOT_TOKEN).build()

# Global dictionary for responses
response_dict = {
    "hello": "Hello! How are you, sir?",
    "hi": "Hi! How can I assist you today?",
    "how are you": "I'm just a bot, but I'm functioning perfectly!",
    "what is your name": "I am your friendly chatbot. You can call me ROZ!",
    "bye": "Goodbye! Have a great day!"
}

# Advanced shortcuts with descriptions for better user understanding
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
    'clear Browse data': {'keys': 'ctrl+shift+delete', 'desc': 'Opens clear Browse data dialog'},
    'new incognito window': {'keys': 'ctrl+shift+n', 'desc': 'Opens a new incognito/private browser window'},
    'private Browse': {'keys': 'ctrl+shift+p', 'desc': 'Opens a new private browser window (Firefox)'},
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
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks if the user interacting with the bot is authorized."""
    user_id = update.effective_user.id
    if user_id == ALLOWED_USER_ID:
        return True
    else:
        await update.message.reply_text("❌ Access Denied: You are not authorized to use this bot.")
        return False

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    """Centralized error handling to send error messages to the user and console."""
    try:
        message = update.message or (update.callback_query.message if update.callback_query else None)
        if message:
            await message.reply_text(f"❌ An error occurred: {str(error)}\nPlease try again or use /help.")
        print(f"Error: {error}", flush=True)
    except Exception as e:
        print(f"Critical error handler failure: {e}", flush=True)

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, welcoming the user and showing the main menu."""
    if not await is_authorized(update, context):
        return
        
    await update.message.reply_text(
        "👋 *Welcome to ROZ - Your Remote Control Bot!* 👋\n\n"
        "I can help you control your computer remotely. "
        "Use the menu buttons below or type /help for a list of commands.\n\n"
        "To get started, try Browse files or checking system info!",
        parse_mode="Markdown",
        reply_markup=main_menu_markup
    )

# ==================== FILE BROWSER ====================
async def browse_files(update: Update, context: ContextTypes.DEFAULT_TYPE, path="C:\\"):
    """
    Allows the user to browse files and folders on the remote computer.
    It updates the current message to show the new directory content,
    making the chat cleaner.
    """
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        
        if not os.path.exists(path) or not os.path.isdir(path):
            await message.reply_text("⚠️ Invalid path or not a directory. Returning to root.")
            path = "C:\\" # Reset to C drive if path is invalid

        items = []
        try:
            items = os.listdir(path)
        except PermissionError:
            await message.reply_text("⛔️ Permission denied to access this directory.")
            parent = os.path.dirname(path)
            if parent == path: # If already at root and still permission denied
                await message.reply_text("Cannot access any further. Please try another drive or directory.")
                return
            else:
                return await browse_files(update, context, parent) # Go back to parent on permission error
        except Exception as e:
            await message.reply_text(f"❌ Error listing directory contents: {e}")
            parent = os.path.dirname(path)
            if parent == path:
                return
            else:
                return await browse_files(update, context, parent)

        keyboard = []
        
        # Add drive buttons at root level
        if path == "C:\\":
            # Corrected the list comprehension syntax: removed the duplicate 'd'
            drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\") and os.path.isdir(f"{d}:\\")]
            if drives:
                drive_buttons = []
                for drive in drives:
                    drive_buttons.append(InlineKeyboardButton(f"💿 Drive {drive}", callback_data=f"browse_{drive}"))
                keyboard.append(drive_buttons)
            else:
                keyboard.append([InlineKeyboardButton("🤷‍♂️ No drives found", callback_data="no_action")])
        
        # Folders first
        folder_buttons = []
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folder_buttons.append(InlineKeyboardButton(f"📁 {item}", callback_data=f"browse_{full_path}"))
                if len(folder_buttons) == 2: # Max 2 buttons per row for better readability
                    keyboard.append(folder_buttons)
                    folder_buttons = []
        if folder_buttons: # Add any remaining folder buttons
            keyboard.append(folder_buttons)
            
        # Files with icons
        file_buttons = []
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                icon = "📄"
                ext = os.path.splitext(item)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif']:
                    icon = "🖼️"
                elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    icon = "🎬"
                elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
                    icon = "🎵"
                elif ext in ['.pdf']:
                    icon = "📄"
                elif ext in ['.zip', '.rar', '.7z']:
                    icon = "📦"
                elif ext in ['.exe', '.msi']:
                    icon = "⚙️"
                elif ext in ['.doc', '.docx']:
                    icon = "📄"
                elif ext in ['.xls', '.xlsx']:
                    icon = "📊"
                elif ext in ['.ppt', '.pptx']:
                    icon = "📊"
                elif ext in ['.txt', '.log', '.ini', '.cfg', '.py', '.js', '.html', '.css']:
                    icon = "📝" # Generic text/code file icon
                file_buttons.append(InlineKeyboardButton(f"{icon} {item}", callback_data=f"file_{full_path}"))
                if len(file_buttons) == 2: # Max 2 buttons per row
                    keyboard.append(file_buttons)
                    file_buttons = []
        if file_buttons: # Add any remaining file buttons
            keyboard.append(file_buttons)
        
        # Navigation and Action buttons
        nav_buttons = []
        parent = os.path.dirname(path)
        if parent != path: # If not at root, show parent directory button
            nav_buttons.append(InlineKeyboardButton("⬆️ Parent Directory", callback_data=f"browse_{parent}"))
        
        # Add "Go to C:\" button if not already at C:\
        if path != "C:\\":
            nav_buttons.append(InlineKeyboardButton("🏠 Go to C:\\", callback_data="browse_C:\\"))
            
        if nav_buttons:
            keyboard.append(nav_buttons)
            
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])
        
        # Edit the message if it's a callback query to prevent multiple messages
        if update.callback_query:
            await message.edit_text(
                f"📂 Current Directory: `{path}`",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await message.reply_text(
                f"📂 Current Directory: `{path}`",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        
    except Exception as e:
        await handle_error(update, context, e)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Handles requests to open or send a specific file to the user."""
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.callback_query.message
        
        if not os.path.exists(file_path):
            await message.reply_text("⚠️ File not found.")
            # Optionally, re-show the current directory
            parent_dir = os.path.dirname(file_path)
            await browse_files(update, context, parent_dir if parent_dir else "C:\\")
            return

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(f"⚠️ File too large (max {MAX_FILE_SIZE / (1024*1024):.0f}MB). This file is {file_size / (1024*1024):.2f}MB.")
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path) # Define file_name here

        # Handle different file types
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            await message.reply_photo(photo=open(file_path, 'rb'))
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            await message.reply_video(video=open(file_path, 'rb'))
        elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
            await message.reply_audio(audio=open(file_path, 'rb'))
        elif ext in ['.txt', '.log', '.csv', '.html', '.css', '.json', '.xml', '.md', '.ini', '.cfg']: 
            # Offer choice to download or read content for general text files
            keyboard = [
                [InlineKeyboardButton(f"⬇️ Download `{file_name}`", callback_data=f"download_file_{file_path}")],
                [InlineKeyboardButton(f"📝 Read Content of `{file_name}`", callback_data=f"read_content_{file_path}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(
                f"What would you like to do with `{file_name}`?",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        elif ext in ['.py', '.js']: # Specific handling for executable scripts
            keyboard = [
                [InlineKeyboardButton(f"⬇️ Download `{file_name}`", callback_data=f"download_file_{file_path}")],
                [InlineKeyboardButton(f"📝 Read Content of `{file_name}`", callback_data=f"read_content_{file_path}")],
                [InlineKeyboardButton(f"▶️ Run `{file_name}`", callback_data=f"run_file_{file_path}")] # New "Run" option
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(
                f"What would you like to do with `{file_name}`?",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await message.reply_document(document=open(file_path, 'rb'))
            
    except Exception as e:
        await handle_error(update, context, e)

async def run_script_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """Executes a Python or JavaScript file."""
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.callback_query.message
        
        if not os.path.exists(file_path):
            await message.reply_text("⚠️ File not found.")
            return

        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            await message.reply_text(f"▶️ Running Python script: `{os.path.basename(file_path)}`...", parse_mode="Markdown")
            # Using subprocess.Popen to avoid blocking the bot and get output
            process = subprocess.Popen(['python', file_path], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True, 
                                       encoding='utf-8')
            stdout, stderr = process.communicate(timeout=30) # Add a timeout
            
            response = ""
            if stdout:
                response += f"```\n{stdout}\n```"
            if stderr:
                response += f"❌ Error:\n```\n{stderr}\n```"
            if not stdout and not stderr:
                response = "✅ Script executed successfully with no output."
                
            await message.reply_text(f"Script output for `{os.path.basename(file_path)}`:\n{response}", parse_mode="Markdown")

        elif ext == '.js':
            await message.reply_text(f"▶️ Running JavaScript file (requires Node.js): `{os.path.basename(file_path)}`...", parse_mode="Markdown")
            # Ensure Node.js is in your system's PATH
            process = subprocess.Popen(['node', file_path], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True, 
                                       encoding='utf-8')
            stdout, stderr = process.communicate(timeout=30)
            
            response = ""
            if stdout:
                response += f"```\n{stdout}\n```"
            if stderr:
                response += f"❌ Error:\n```\n{stderr}\n```"
            if not stdout and not stderr:
                response = "✅ Script executed successfully with no output."
                
            await message.reply_text(f"Script output for `{os.path.basename(file_path)}`:\n{response}", parse_mode="Markdown")
        else:
            await message.reply_text("⚠️ This file type cannot be run directly.")
            
    except subprocess.TimeoutExpired:
        process.kill()
        await message.reply_text(f"⏰ Script execution timed out for `{os.path.basename(file_path)}`.", parse_mode="Markdown")
    except FileNotFoundError:
        await message.reply_text(f"❌ Error: Python/Node.js executable not found. Make sure they are installed and in your system's PATH.", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)


# ==================== SYSTEM CONTROL ====================
async def shutdown_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts the user for confirmation before shutting down the PC, offering options."""
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        
        keyboard = [
            [InlineKeyboardButton("✅ Yes, shutdown immediately", callback_data="confirm_shutdown")],
            [InlineKeyboardButton("⏰ Shutdown in 60 seconds", callback_data="shutdown_60s")],
            [InlineKeyboardButton("❌ Cancel Shutdown", callback_data="cancel_shutdown")]
        ]
        
        await message.reply_text(
            "⚠️ *Are you sure you want to shutdown the PC?*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        await handle_error(update, context, e)

async def confirm_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes the PC shutdown command immediately."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.callback_query.message
        await message.edit_text("🖥️ Shutting down PC NOW... Goodbye!")
        os.system("shutdown /s /t 1")  # Immediate shutdown
    except Exception as e:
        await handle_error(update, context, e)

async def shutdown_60s(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Schedules PC shutdown in 60 seconds."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.callback_query.message
        await message.edit_text("🖥️ PC will shutdown in 60 seconds. You can cancel with /cancel_shutdown.")
        os.system("shutdown /s /t 60")
    except Exception as e:
        await handle_error(update, context, e)

async def cancel_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aborts any scheduled PC shutdown."""
    if not await is_authorized(update, context):
        return
    try:
        message = update.message or update.callback_query.message
        os.system("shutdown /a") # Abort shutdown
        await message.edit_text("✅ Scheduled shutdown has been cancelled.")
    except Exception as e:
        await handle_error(update, context, e)

# ==================== MENU SYSTEM (Enhanced) ====================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main menu options to the user using ReplyKeyboardMarkup."""
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        # Using the ReplyKeyboardMarkup for the main menu for persistent buttons
        await message.reply_text(
            "� *Main Menu - Choose an option:*",
            parse_mode="Markdown",
            reply_markup=main_menu_markup
        )
    except Exception as e:
        await handle_error(update, context, e)

# ==================== ORIGINAL FEATURES (Refactored and Improved) ====================
async def send_shortcut_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message with inline keyboard buttons for various shortcuts."""
    if not await is_authorized(update, context):
        return
    
    message = update.message or update.callback_query.message
    
    # Create a list of all shortcut names for inline buttons
    shortcut_names = list(shortcuts.keys())
    
    # Divide shortcuts into rows for better display
    keyboard_buttons = []
    row = []
    for name in shortcut_names:
        row.append(InlineKeyboardButton(name.title(), callback_data=f"shortcut_{name}"))
        if len(row) == 3: # 3 buttons per row
            keyboard_buttons.append(row)
            row = []
    if row: # Add any remaining buttons
        keyboard_buttons.append(row)
    
    # Adding "Hide Buttons" and "Back to Main Menu" at the end
    keyboard_buttons.append([
        InlineKeyboardButton("🛑 Hide Shortcuts", callback_data="hide_shortcuts"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu_from_shortcuts")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard_buttons)

    sent_message = await message.reply_text("🎹 *Press a button to trigger a shortcut:*\n\n"
                                           "💡 *Tip:* You can also type 'press [shortcut_name]' "
                                           "or 'press [keys]' directly in the chat!", 
                                           reply_markup=reply_markup, 
                                           parse_mode="Markdown")
    
    context.user_data["last_shortcut_message_id"] = sent_message.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles all inline keyboard button presses.
    It routes to appropriate functions based on callback_data.
    """
    query = update.callback_query
    await query.answer() # Acknowledge the callback query immediately

    callback_data = query.data
    
    if callback_data == "hide_shortcuts":
        if "last_shortcut_message_id" in context.user_data:
            try:
                await query.message.delete()
            except Exception as e:
                print(f"Error deleting message: {e}")
            del context.user_data["last_shortcut_message_id"] # Clean up the stored ID
        await query.message.reply_text("🔴 *Shortcut buttons hidden! Use /shortcuts to show them again.*", parse_mode="Markdown")
        # Optionally, show the main menu again after hiding buttons
        await main_menu(update, context)
        return
    
    if callback_data.startswith("shortcut_"):
        shortcut_name = callback_data.replace("shortcut_", "")
        shortcut_info = shortcuts.get(shortcut_name)

        if shortcut_info:
            try:
                kb.press_and_release(shortcut_info['keys'])
                await query.message.reply_text(f"✅ *'{shortcut_name.title()}'* shortcut triggered! (`{shortcut_info['keys']}`)", parse_mode="Markdown")
            except Exception as e:
                await query.message.reply_text(f"⚠️ Error triggering shortcut '{shortcut_name}': {e}")
        else:
            await query.message.reply_text("⚠️ Shortcut not found.")
    
    elif callback_data == "youtube_link":
        await youtube_url(update, context)
    elif callback_data == "open_whatsapp_app":
        await open_whatsapp(update, context)
    elif callback_data == "system_info":
        await system_info(update, context)
    elif callback_data == "take_screenshot":
        await take_screenshot(update, context)
    elif callback_data == "click_webcam_photo":
        await click_photo(update, context)
    elif callback_data.startswith('browse_'):
        await browse_files(update, context, callback_data[7:])
    elif callback_data.startswith('file_'):
        await handle_file(update, context, callback_data[5:])
    elif callback_data.startswith('download_file_'): # New handler for downloading files
        file_path = callback_data[14:]
        try:
            await query.message.reply_text(f"⬇️ Sending file: `{os.path.basename(file_path)}` for download...", parse_mode="Markdown")
            await query.message.reply_document(document=open(file_path, 'rb'))
        except Exception as e:
            await handle_error(update, context, e)
    elif callback_data.startswith('read_content_'): # New handler for reading content
        file_path = callback_data[13:]
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4000) # Limit content to avoid message length issues
                if len(content) >= 4000:
                    content += "\n\n... (content truncated)"
                await query.message.reply_text(f"📝 Content of `{file_name}`:\n```\n{content}\n```", parse_mode="Markdown")
        except Exception as e:
            await handle_error(update, context, e)
    elif callback_data.startswith('run_file_'): # NEW: Handler for running files
        file_path = callback_data[9:] # 'run_file_' is 9 characters
        await run_script_file(update, context, file_path)
    elif callback_data == 'shutdown_pc':
        await shutdown_pc(update, context)
    elif callback_data == 'confirm_shutdown':
        await confirm_shutdown(update, context)
    elif callback_data == 'shutdown_60s':
        await shutdown_60s(update, context)
    elif callback_data == 'cancel_shutdown':
        await cancel_shutdown(update, context)
    elif callback_data == 'main_menu' or callback_data == 'main_menu_from_shortcuts':
        await main_menu(update, context)
    elif callback_data == 'show_shortcuts':
        await send_shortcut_buttons(update, context)
    elif callback_data == "no_action":
        await query.message.edit_text("No action available.")


# Reply Keyboard Markups for main navigation
main_menu_markup = ReplyKeyboardMarkup([
    [KeyboardButton("📁 Browse Files"), KeyboardButton("🖥️ System Info")],
    [KeyboardButton("📸 Screenshot"), KeyboardButton("📷 Click Photo")],
    [KeyboardButton("⚡ Shortcuts"), KeyboardButton("🚀 Quick Actions")],
    [KeyboardButton("⚙️ System Control"), KeyboardButton("ℹ️ Help")]
], resize_keyboard=True, one_time_keyboard=False)

quick_actions_markup = ReplyKeyboardMarkup([
    [KeyboardButton("🌐 Open Google"), KeyboardButton("▶️ Open YouTube")],
    [KeyboardButton("💬 Open WhatsApp"), KeyboardButton("📝 Type Text")],
    [KeyboardButton("⬆️ Up"), KeyboardButton("⬇️ Down"), KeyboardButton("⬅️ Left"), KeyboardButton("➡️ Right")],
    [KeyboardButton("↩️ Enter"), KeyboardButton("🔙 Backspace"), KeyboardButton("Space")],
    [KeyboardButton("⏪ Main Menu")]
], resize_keyboard=True, one_time_keyboard=False)

system_control_markup = ReplyKeyboardMarkup([
    [KeyboardButton("🔆 Brightness +"), KeyboardButton("🔆 Brightness -")],
    [KeyboardButton("🔊 Volume +"), KeyboardButton("🔉 Volume -")],
    [KeyboardButton("🔒 Lock PC"), KeyboardButton("🖥️ Shutdown PC")],
    [KeyboardButton("🔄 Restart PC"), KeyboardButton("💤 Sleep PC")],
    [KeyboardButton("⏪ Main Menu")]
], resize_keyboard=True, one_time_keyboard=False)

# Command handlers for common actions (can be accessed directly or via buttons)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides a list of available commands and functionalities."""
    if await is_authorized(update, context):
        # Using a raw string (r"") and escaping all MarkdownV2 special characters
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
\- /shutdown: Initiates PC shutdown sequence\.
\- /cancel\_shutdown: Aborts a scheduled shutdown\.

*Quick Actions \(via 'Quick Actions' menu\):*
\- Open Google, Open YouTube, Open WhatsApp, Type Text, Arrow keys, Enter, Backspace, Space\.

*System Control \(via 'System Control' menu\):*
\- Brightness adjustment, Volume adjustment, Lock PC, Shutdown PC, Restart PC, Sleep PC\.

*General Chat:*
\- Try typing 'hello', 'hi', 'how are you', 'what is your name' for a quick chat\!
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=main_menu_markup)

async def youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a YouTube link and opens it in the default browser."""
    message = update.message if update.message else update.callback_query.message
    await message.reply_text("Here's a link to YouTube: http://www.youtube.com") # Corrected YouTube URL
    webbrowser.open("http://www.youtube.com") # Open on PC

async def open_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Opens WhatsApp application on the remote PC."""
    message = update.message if update.message else update.callback_query.message
    try:
        kb.press_and_release('windows')
        time.sleep(0.5)
        kb.write('WhatsApp')
        time.sleep(1)
        kb.press_and_release('enter')
        await message.reply_text("✅ WhatsApp opened successfully.")
    except Exception as e:
        await handle_error(update, context, e)

async def open_application(update: Update, context: ContextTypes.DEFAULT_TYPE, app_name: str):
    """Opens an application based on user's text input."""
    message = update.message if update.message else update.callback_query.message
    try:
        kb.press_and_release('windows')
        time.sleep(0.5)
        kb.write(app_name)
        time.sleep(1)
        kb.press_and_release('enter')
        await message.reply_text(f"✅ Attempted to open: *{app_name.title()}*", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)

async def type_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text_to_type: str):
    """Types the given text on the remote PC."""
    message = update.message if update.message else update.callback_query.message
    try:
        kb.write(text_to_type)
        await message.reply_text("✅ Typing completed successfully.")
    except Exception as e:
        await handle_error(update, context, e)

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    """Presses a single key or a shortcut combination on the remote PC."""
    message = update.message if update.message else update.callback_query.message
    try:
        # Normalize key input
        key = key.lower().replace(" ", "")
        
        # Check if it's a known shortcut name or a direct key
        keys_to_press = key # Default to direct key name
        for shortcut_name, shortcut_info in shortcuts.items():
            if key == shortcut_name.lower() or key == shortcut_info['keys'].lower().replace(" ", ""):
                keys_to_press = shortcut_info['keys']
                break

        kb.press_and_release(keys_to_press)
        await message.reply_text(f"✅ Pressed key(s): `{keys_to_press}` successfully.")
    except Exception as e:
        await handle_error(update, context, e)

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retrieves and sends detailed system information like battery, CPU/memory usage, disk, and uptime."""
    message = update.message if update.message else update.callback_query.message
    try:
        info_text = "🖥️ *System Information:*\n"
        
        # Battery Info
        battery = psutil.sensors_battery()
        if battery:
            plugged_status = "Plugged In ⚡" if battery.power_plugged else "Not Plugged In"
            time_left = ""
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                minutes, seconds = divmod(battery.secsleft, 60)
                hours, minutes = divmod(minutes, 60)
                time_left = f", Est. {int(hours)}h {int(minutes)}m remaining"
            info_text += f"- Battery: `{battery.percent}%` ({plugged_status}{time_left})\n"
        else:
            info_text += "- Battery: `Information not available`\n"
        
        # CPU Info
        cpu_usage = psutil.cpu_percent(interval=1)
        info_text += f"- CPU Usage: `{cpu_usage}%`\n"
        
        # Memory Info
        memory = psutil.virtual_memory()
        info_text += f"- Memory Usage: `{memory.percent}%` (`{memory.used / (1024**3):.2f} GB` / `{memory.total / (1024**3):.2f} GB`)\n"

        # Disk Info (C: drive)
        try:
            disk_c = psutil.disk_usage('C:\\')
            info_text += f"- C:\\ Disk Usage: `{disk_c.percent}%` (`{disk_c.used / (1024**3):.2f} GB` / `{disk_c.total / (1024**3):.2f} GB`)\n"
        except Exception:
            info_text += "- C:\\ Disk Usage: `Information not available`\n"

        # Network Info (basic)
        net_io = psutil.net_io_counters()
        info_text += f"- Network (Sent/Recv): `{net_io.bytes_sent / (1024**2):.2f} MB` / `{net_io.bytes_recv / (1024**2):.2f} MB`\n"

        # Uptime
        boot_time_timestamp = psutil.boot_time()
        boot_time_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time_timestamp))
        info_text += f"- Last Boot: `{boot_time_readable}`\n"
        
        await message.reply_text(info_text, parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Takes a screenshot of the remote PC and sends it to the user."""
    message = update.message if update.message else update.callback_query.message
    try:
        screenshot_path = "screenshot.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        await message.reply_text("📸 Taking screenshot...", parse_mode="Markdown")
        await message.reply_photo(photo=open(screenshot_path, "rb"))
        os.remove(screenshot_path)  # Clean up
    except Exception as e:
        await handle_error(update, context, e)

async def click_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Takes a photo using the webcam and sends it to the user."""
    message = update.message if update.message else update.callback_query.message
    try:
        photo_path = "webcam_photo.jpg"
        camera = cv2.VideoCapture(0) # 0 is typically the default webcam
        
        if not camera.isOpened():
            await message.reply_text("⚠️ No webcam detected or it is in use by another application.")
            return

        # Give camera time to warm up
        time.sleep(1) 
        return_value, image = camera.read()
        
        if return_value:
            cv2.imwrite(photo_path, image)
            await message.reply_text("📷 Photo clicked successfully. Sharing it with you...", parse_mode="Markdown")
            await message.reply_photo(photo=open(photo_path, "rb"))
            os.remove(photo_path)  # Clean up
        else:
            await message.reply_text("Failed to capture photo. Ensure your camera is connected and not in use.")
    except Exception as e:
        await handle_error(update, context, e)
    finally:
        if 'camera' in locals() and camera.isOpened():
            camera.release()
        cv2.destroyAllWindows()

# System control actions (keyboard simulations)
async def swap_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Alt+Tab to switch between open applications."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("alt+tab")
        await update.message.reply_text("✅ Switched application.")
    except Exception as e: await handle_error(update, context, e)

async def change_tab_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Tab to switch to the next browser tab."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+tab")
        await update.message.reply_text("✅ Switched to next tab.")
    except Exception as e: await handle_error(update, context, e)

async def change_tab_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Shift+Tab to switch to the previous browser tab."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+shift+tab")
        await update.message.reply_text("✅ Switched to previous tab.")
    except Exception as e: await handle_error(update, context, e)

async def press_enter_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Enter key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("enter")
        await update.message.reply_text("✅ 'Enter' key pressed.")
    except Exception as e: await handle_error(update, context, e)

async def press_space_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Spacebar."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("space")
        await update.message.reply_text("✅ 'Space' key pressed.")
    except Exception as e: await handle_error(update, context, e)

async def refresh_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates F5 to refresh the current window."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("f5")
        await update.message.reply_text("✅ Window refreshed.")
    except Exception as e: await handle_error(update, context, e)

async def press_tab_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Tab key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("tab")
        await update.message.reply_text("✅ 'Tab' key pressed.")
    except Exception as e: await handle_error(update, context, e)

async def arrow_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Up arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("up")
        await update.message.reply_text("⬆️ 'Up' arrow pressed.")
    except Exception as e: await handle_error(update, context, e)

async def arrow_down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Down arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("down")
        await update.message.reply_text("⬇️ 'Down' arrow pressed.")
    except Exception as e: await handle_error(update, context, e)

async def arrow_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Left arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("left")
        await update.message.reply_text("⬅️ 'Left' arrow pressed.")
    except Exception as e: await handle_error(update, context, e)

async def arrow_right(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Right arrow key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("right")
        await update.message.reply_text("➡️ 'Right' arrow pressed.")
    except Exception as e: await handle_error(update, context, e)
    
async def press_backspace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Backspace key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("backspace")
        await update.message.reply_text("🔙 'Backspace' pressed.")
    except Exception as e: await handle_error(update, context, e)

async def press_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the Home key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("home")
        await update.message.reply_text("✅ 'Home' key pressed.")
    except Exception as e: await handle_error(update, context, e)

async def press_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates pressing the End key."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("end")
        await update.message.reply_text("✅ 'End' key pressed.")
    except Exception as e: await handle_error(update, context, e)

async def zoom_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl++ to zoom in."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+plus")
        await update.message.reply_text("✅ Zoomed In.")
    except Exception as e: await handle_error(update, context, e)

async def zoom_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+- to zoom out."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+-")
        await update.message.reply_text("✅ Zoomed Out.")
    except Exception as e: await handle_error(update, context, e)

async def undo_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Z for undo."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+z")
        await update.message.reply_text("✅ Undo action triggered.")
    except Exception as e: await handle_error(update, context, e)

async def redo_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulates Ctrl+Y for redo."""
    if not await is_authorized(update, context): return
    try:
        kb.press_and_release("ctrl+y")
        await update.message.reply_text("✅ Redo action triggered.")
    except Exception as e: await handle_error(update, context, e)

async def increase_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Increases the screen brightness."""
    if not await is_authorized(update, context): return
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = min(current_brightness + 10, 100)
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(f"🔆 Brightness increased to: `{new_brightness}%`", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)

async def decrease_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Decreases the screen brightness."""
    if not await is_authorized(update, context): return
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = max(current_brightness - 10, 0)
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(f"🔆 Brightness decreased to: `{new_brightness}%`", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)

async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Increases the system volume."""
    if not await is_authorized(update, context): return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(current_volume + 0.10, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        await update.message.reply_text(f"🔊 Volume increased to: `{new_volume * 100:.0f}%`", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Decreases the system volume."""
    if not await is_authorized(update, context): return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.10, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        await update.message.reply_text(f"🔉 Volume decreased to: `{new_volume * 100:.0f}%`", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)

async def lock_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Locks the PC."""
    if not await is_authorized(update, context): return
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        await update.message.reply_text("🔒 PC has been locked.")
    except Exception as e:
        await handle_error(update, context, e)

async def restart_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompts for confirmation before restarting the PC."""
    if not await is_authorized(update, context): return
    try:
        keyboard = [
            [InlineKeyboardButton("✅ Yes, restart now", callback_data="confirm_restart")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_restart")]
        ]
        await update.message.reply_text(
            "⚠️ Are you sure you want to restart the PC?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await handle_error(update, context, e)

async def confirm_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes the PC restart command immediately."""
    if not await is_authorized(update, context): return
    try:
        message = update.callback_query.message
        await message.edit_text("🔄 Restarting PC NOW...")
        os.system("shutdown /r /t 1") # Immediate restart
    except Exception as e:
        await handle_error(update, context, e)

async def cancel_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels any pending PC restart."""
    if not await is_authorized(update, context): return
    try:
        message = update.callback_query.message
        await message.edit_text("✅ Restart cancelled.")
    except Exception as e:
        await handle_error(update, context, e)

async def sleep_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Puts the PC into sleep mode."""
    if not await is_authorized(update, context): return
    try:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        await update.message.reply_text("💤 PC is going to sleep...")
    except Exception as e:
        await handle_error(update, context, e)

# MODIFIED: Handler for receiving files with categorization
async def handle_incoming_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles incoming documents, checks authorization, creates the target directory if needed,
    and saves the file to C:\\Programs\\Code or C:\\Programs\\Other based on its type.
    """
    if not await is_authorized(update, context):
        return

    document = update.message.document
    file_name = document.file_name
    file_extension = os.path.splitext(file_name)[1].lower()

    target_directory = ""
    file_type_description = ""

    # Define code file extensions (including .txt)
    code_extensions = ['.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.txt', '.log', '.ini', '.cfg', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.go', '.rb', '.sh', '.bat', '.ps1']
    
    # Categorize the file
    if file_extension in code_extensions:
        target_directory = CODE_FILES_DIR
        file_type_description = "code/text file"
    else:
        target_directory = OTHER_FILES_DIR
        file_type_description = "other file"

    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)

    file_path = os.path.join(target_directory, file_name)

    try:
        # Check file size before attempting to download
        if document.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(f"⚠️ File too large (max {MAX_FILE_SIZE / (1024*1024):.0f}MB). This file is {document.file_size / (1024*1024):.2f}MB.")
            return

        new_file = await context.bot.get_file(document.file_id)
        await new_file.download_to_drive(custom_path=file_path)
        await update.message.reply_text(f"✅ Your {file_type_description} `{file_name}` saved successfully to `{target_directory}`.", parse_mode="Markdown")
    except Exception as e:
        await handle_error(update, context, e)


async def chatbot_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles general text messages from the user and routes them to appropriate functions
    or provides a predefined response.
    """
    if not await is_authorized(update, context):
        return

    query = update.message.text.lower().strip()
    user_input_raw = update.message.text.strip() # Preserve original case for specific button matches

    # Handle menu button presses (ReplyKeyboard)
    if user_input_raw == "📁 Browse Files":
        await browse_files(update, context)
    elif user_input_raw == "🖥️ System Info":
        await system_info(update, context)
    elif user_input_raw == "📸 Screenshot":
        await take_screenshot(update, context)
    elif user_input_raw == "📷 Click Photo":
        await click_photo(update, context)
    elif user_input_raw == "⚡ Shortcuts":
        await send_shortcut_buttons(update, context)
    elif user_input_raw == "🚀 Quick Actions":
        await update.message.reply_text("⚡ *Quick Actions Menu:*", parse_mode="Markdown", reply_markup=quick_actions_markup)
    elif user_input_raw == "⚙️ System Control":
        await update.message.reply_text("⚙️ *System Control Menu:*", parse_mode="Markdown", reply_markup=system_control_markup)
    elif user_input_raw == "ℹ️ Help":
        await help_command(update, context)
    elif user_input_raw == "⏪ Main Menu":
        await main_menu(update, context)
    elif user_input_raw == "🌐 Open Google":
        webbrowser.open("https://www.google.com")
        await update.message.reply_text("✅ Opened Google in browser.")
    elif user_input_raw == "▶️ Open YouTube":
        await youtube_url(update, context)
    elif user_input_raw == "💬 Open WhatsApp":
        await open_whatsapp(update, context)
    elif user_input_raw == "📝 Type Text":
        await update.message.reply_text("Please reply to this message with the text you want me to type.",
                                        reply_markup=ReplyKeyboardRemove()) # Remove buttons temporarily
        context.user_data['awaiting_text_input'] = True
    elif user_input_raw == "⬆️ Up":
        await arrow_up(update, context)
    elif user_input_raw == "⬇️ Down":
        await arrow_down(update, context)
    elif user_input_raw == "⬅️ Left":
        await arrow_left(update, context)
    elif user_input_raw == "➡️ Right":
        await arrow_right(update, context)
    elif user_input_raw == "↩️ Enter":
        await press_enter_key(update, context)
    elif user_input_raw == "🔙 Backspace":
        await press_backspace(update, context)
    elif user_input_raw == "Space":
        await press_space_key(update, context)
    elif user_input_raw == "🔆 Brightness +":
        await increase_brightness(update, context)
    elif user_input_raw == "🔆 Brightness -":
        await decrease_brightness(update, context)
    elif user_input_raw == "🔊 Volume +":
        await increase_volume(update, context)
    elif user_input_raw == "🔉 Volume -":
        await decrease_volume(update, context)
    elif user_input_raw == "🔒 Lock PC":
        await lock_pc(update, context)
    elif user_input_raw == "🖥️ Shutdown PC":
        await shutdown_pc(update, context)
    elif user_input_raw == "🔄 Restart PC":
        await restart_pc(update, context)
    elif user_input_raw == "💤 Sleep PC":
        await sleep_pc(update, context)
    elif user_input_raw == "🔃 Swap App":
        await swap_app(update, context)
    elif user_input_raw == "🔁 Next Tab":
        await change_tab_next(update, context)
    elif user_input_raw == "🔁 Prev Tab":
        await change_tab_prev(update, context)
    elif user_input_raw == "TAB":
        await press_tab_key(update, context)
    elif user_input_raw == "Refress":
        await refresh_window(update, context)
    elif user_input_raw == "Home":
        await press_home(update, context)
    elif user_input_raw == "End":
        await press_end(update, context)
    elif user_input_raw == "🔍 Zoom IN":
        await zoom_in(update, context)
    elif user_input_raw == "🔎 Zoom OUT":
        await zoom_out(update, context)
    elif user_input_raw == "Undu":
        await undo_action(update, context)
    elif user_input_raw == "Redu":
        await redo_action(update, context)
    
    # Handle text input for 'type text'
    elif context.user_data.get('awaiting_text_input'):
        text_to_type = user_input_raw
        await type_text(update, context, text_to_type)
        context.user_data['awaiting_text_input'] = False
        await update.message.reply_text("What next, sir?", reply_markup=quick_actions_markup) # Show quick actions again
        
    # Handle specific text commands
    elif query.startswith("open "):
        app_name = query[5:]
        await open_application(update, context, app_name)
    elif query.startswith("type ") or query.startswith("write "):
        text_to_type = query.replace("type ", "").replace("write ", "").strip()
        await type_text(update, context, text_to_type)
    elif query.startswith("press "):
        key_command = query[6:]
        await press_key(update, context, key_command)
    elif query.startswith('google '):
        search_query = query[7:]
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        await update.message.reply_text(f"✅ Searching Google for: `{search_query}`", parse_mode="Markdown")
    elif query.startswith('youtube '):
        search_query = query[8:]
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}") # Corrected Youtube URL
        await update.message.reply_text(f"✅ Searching YouTube for: `{search_query}`", parse_mode="Markdown")
    
    # Handle general chatbot responses
    else:
        response = response_dict.get(query, "I'm sorry, I didn't understand that. Can you rephrase? Or use /help.")
        await update.message.reply_text(response, reply_markup=main_menu_markup)


# Register handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", main_menu))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("youtube", youtube_url))
app.add_handler(CommandHandler("open_whatsapp", open_whatsapp))
app.add_handler(CommandHandler("system_info", system_info))
app.add_handler(CommandHandler("screenshot", take_screenshot))
app.add_handler(CommandHandler("click_photo", click_photo))
app.add_handler(CommandHandler("browse", lambda u,c: browse_files(u,c,"C:\\"))) # Initial browse to C drive
app.add_handler(CommandHandler("shutdown", shutdown_pc))
app.add_handler(CommandHandler("cancel_shutdown", cancel_shutdown)) # Added handler for /cancel_shutdown
app.add_handler(CommandHandler("shortcuts", send_shortcut_buttons))

# Register handler for documents
app.add_handler(MessageHandler(filters.Document.ALL, handle_incoming_document))

# MessageHandler for general text (including quick actions and custom commands)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_response))

# CallbackQueryHandler for all inline button presses
app.add_handler(CallbackQueryHandler(button_handler))


# Start the bot
if __name__ == "__main__":
    print("✅ Bot is starting...")
    app.run_polling()