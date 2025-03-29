import os
import time
import platform
import socket
import uuid
import psutil
import GPUtil
import screen_brightness_control as sbc
import pyautogui
import cv2
import webbrowser
import keyboard as kb
import subprocess
from datetime import datetime
from threading import Timer
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ===== CONFIGURATION =====
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7070124825:AAFSnUIo0c-b_7dsMj8fFL_rUILLL3i7ab8")
ALLOWED_USERS = {5285057277: "Admin"}  # {user_id: "role"}
REQUEST_TIMEOUT = 30  # seconds for confirmation timeout
SCREENSHOT_PATH = "screenshot.png"
PHOTO_PATH = "photo.jpg"
TEMP_DIR = "temp_bot_files"

# ===== KEYBOARD SHORTCUTS =====
SHORTCUTS = {
    'copy': 'ctrl+c',
    'paste': 'ctrl+v',
    'cut': 'ctrl+x',
    'undo': 'ctrl+z',
    'redo': 'ctrl+y',
    'save': 'ctrl+s',
    'select all': 'ctrl+a',
    'find': 'ctrl+f',
    'new window': 'ctrl+n',
    'close window': 'ctrl+w',
    'refresh': 'f5',
    'task manager': 'ctrl+shift+esc',
    'lock pc': 'win+l',
    'screenshot': 'win+shift+s',
    'emoji picker': 'win+.',
    'virtual desktop': 'win+tab',
    'file explorer': 'win+e',
    'run dialog': 'win+r',
    'settings': 'win+i',
    'action center': 'win+a',
    'project screen': 'win+p',
    'magnifier': 'win+plus',
    'minimize all': 'win+m',
    'restore minimized': 'win+shift+m'
}

# ===== KEYBOARD LAYOUTS =====
def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔃 Swap App"), KeyboardButton("🖥️ System Info")],
        [KeyboardButton("📸 Screenshot"), KeyboardButton("📷 Click Photo")],
        [KeyboardButton("🔁 Prev Tab"), KeyboardButton("TAB"), KeyboardButton("🔁 Next Tab")],
        [KeyboardButton("Space"), KeyboardButton("Refresh")],
        [KeyboardButton("ℹ️ Help"), KeyboardButton("⚙️ More Options"), KeyboardButton("⌨️ Shortcuts")]
    ], resize_keyboard=True)

def get_more_options_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📸 Screenshot"), KeyboardButton("📲 Show Apps")],
        [KeyboardButton("⬆️"), KeyboardButton("⬅️"), KeyboardButton("➡️"), KeyboardButton("⬇️")],
        [KeyboardButton("Home"), KeyboardButton("End"), KeyboardButton("🔙"), KeyboardButton("↩️")],
        [KeyboardButton("🔍 Zoom IN"), KeyboardButton("Space"), KeyboardButton("🔎 Zoom OUT")],
        [KeyboardButton("⏪ Main Menu"), KeyboardButton("⏩ Next Menu")]
    ], resize_keyboard=True)

def get_system_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📸 Screenshot"), KeyboardButton("🔓 Unlock System")],
        [KeyboardButton("🔅➕"), KeyboardButton("🔅➖"), KeyboardButton("🔉"), KeyboardButton("🔊")],
        [KeyboardButton("Undu"), KeyboardButton("Redu")],
        [KeyboardButton("⏪ Previus Menu"), KeyboardButton("🏠 Menu"), KeyboardButton("⏩ Next Menu")]
    ], resize_keyboard=True)

def get_shortcuts_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Copy"), KeyboardButton("Paste"), KeyboardButton("Cut")],
        [KeyboardButton("Undo"), KeyboardButton("Redo"), KeyboardButton("Save")],
        [KeyboardButton("Select All"), KeyboardButton("Find"), KeyboardButton("New")],
        [KeyboardButton("Close"), KeyboardButton("Refresh"), KeyboardButton("Task Manager")],
        [KeyboardButton("🏠 Main Menu")]
    ], resize_keyboard=True)

# ===== SYSTEM STATE =====
class SystemState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.pending_actions = {}
        self.media_sessions = {}
        self.current_volume = 0.5
        self.is_muted = False
        self._create_temp_dir()
    
    def _create_temp_dir(self):
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
    
    def clean_temp_files(self):
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

system_state = SystemState()

# ===== UTILITY FUNCTIONS =====
def is_authorized(user_id):
    return user_id in ALLOWED_USERS

def is_admin(user_id):
    return user_id in ALLOWED_USERS and ALLOWED_USERS[user_id] == "Admin"

def execute_command(cmd, timeout=10):
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            timeout=timeout,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_system_info():
    info = {}
    uname = platform.uname()
    
    # System information
    info["system"] = {
        "os": f"{uname.system} {uname.release}",
        "version": uname.version,
        "hostname": socket.gethostname(),
        "processor": uname.processor,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Hardware information
    info["cpu"] = {
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "usage": psutil.cpu_percent(interval=1),
        "freq": psutil.cpu_freq().current if hasattr(psutil, "cpu_freq") else None
    }
    
    info["memory"] = {
        "total": psutil.virtual_memory().total,
        "used": psutil.virtual_memory().used,
        "percent": psutil.virtual_memory().percent
    }
    
    info["disk"] = {
        "total": psutil.disk_usage('/').total,
        "used": psutil.disk_usage('/').used,
        "percent": psutil.disk_usage('/').percent
    }
    
    info["battery"] = {
        "percent": psutil.sensors_battery().percent if hasattr(psutil, "sensors_battery") else None,
        "power_plugged": psutil.sensors_battery().power_plugged if hasattr(psutil, "sensors_battery") else None
    }
    
    return info

# ===== COMMAND HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    welcome_msg = """
👋 *Welcome to Advanced System Control Bot!* 🚀

🔹 *Main Features:*
- Full system monitoring
- Remote keyboard control
- Media management
- Power controls
- File operations

💡 Use /help for commands or buttons below
"""
    await update.message.reply_text(
        welcome_msg, 
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🛠 *Available Commands:*

*Basic Controls:*
/start - Start the bot
/menu - Show main menu
/help - Show this message
/shortcuts - Show keyboard shortcuts

*System Monitoring:*
/system - Detailed system info
/performance - Performance metrics

*Remote Control:*
/screenshot - Take screenshot
/webcam - Take photo
/volume [0-100] - Set volume
/brightness [0-100] - Set brightness
/type [text] - Type text
/press [key] - Press key

*Admin Commands:*
/shutdown - Shutdown system
/restart - Restart system
/lock - Lock workstation
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Main Menu",
        reply_markup=get_main_menu()
    )

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        info = get_system_info()
        response = f"""
🖥 *System Information Report* 📊

*System:*
- OS: {info['system']['os']}
- Hostname: {info['system']['hostname']}
- Processor: {info['system']['processor']}
- Boot Time: {info['system']['boot_time']}

*Hardware:*
- CPU: {info['cpu']['usage']}% usage ({info['cpu']['cores']} cores)
- Memory: {info['memory']['percent']}% used
- Disk: {info['disk']['percent']}% used
- Battery: {info['battery']['percent'] if info['battery']['percent'] else 'N/A'}%
"""
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== BUTTON HANDLERS =====
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    try:
        # Main menu buttons
        if query == "🖥️ System Info":
            await system_info(update, context)
        elif query == "📸 Screenshot":
            await take_screenshot(update, context)
        elif query == "📷 Click Photo":
            await capture_webcam(update, context)
        elif query == "🔁 Next Tab":
            await next_tab(update, context)
        elif query == "🔁 Prev Tab":
            await prev_tab(update, context)
        elif query == "TAB":
            await press_tab(update, context)
        elif query == "Space":
            await press_space(update, context)
        elif query == "Refresh":
            await refresh_page(update, context)
        elif query == "⚙️ More Options":
            await more_options(update, context)
        elif query == "⌨️ Shortcuts":
            await show_shortcuts_menu(update, context)
        elif query == "🔃 Swap App":
            await swap_app(update, context)
        
        # More options buttons
        elif query == "⬆️":
            await press_up(update, context)
        elif query == "⬇️":
            await press_down(update, context)
        elif query == "⬅️":
            await press_left(update, context)
        elif query == "➡️":
            await press_right(update, context)
        elif query == "Home":
            await press_home(update, context)
        elif query == "End":
            await press_end(update, context)
        elif query == "🔙":
            await press_backspace(update, context)
        elif query == "↩️":
            await press_enter(update, context)
        elif query == "🔍 Zoom IN":
            await zoom_in(update, context)
        elif query == "🔎 Zoom OUT":
            await zoom_out(update, context)
        elif query == "⏪ Main Menu":
            await menu(update, context)
        elif query == "⏩ Next Menu":
            await system_menu(update, context)
        
        # System menu buttons
        elif query == "🔅➕":
            await increase_brightness(update, context)
        elif query == "🔅➖":
            await decrease_brightness(update, context)
        elif query == "🔉":
            await decrease_volume(update, context)
        elif query == "🔊":
            await increase_volume(update, context)
        elif query == "Undu":
            await undo_action(update, context)
        elif query == "Redu":
            await redo_action(update, context)
        elif query == "🏠 Menu":
            await menu(update, context)
        elif query == "🔓 Unlock System":
            await unlock_system(update, context)
        
        # Shortcuts menu buttons
        elif query == "Copy":
            await press_shortcut(update, context, 'copy')
        elif query == "Paste":
            await press_shortcut(update, context, 'paste')
        elif query == "Cut":
            await press_shortcut(update, context, 'cut')
        elif query == "Undo":
            await press_shortcut(update, context, 'undo')
        elif query == "Redo":
            await press_shortcut(update, context, 'redo')
        elif query == "Save":
            await press_shortcut(update, context, 'save')
        elif query == "Select All":
            await press_shortcut(update, context, 'select all')
        elif query == "Find":
            await press_shortcut(update, context, 'find')
        elif query == "New":
            await press_shortcut(update, context, 'new window')
        elif query == "Close":
            await press_shortcut(update, context, 'close window')
        elif query == "Task Manager":
            await press_shortcut(update, context, 'task manager')
        elif query == "🏠 Main Menu":
            await menu(update, context)
        
        else:
            await update.message.reply_text("ℹ️ Unknown command")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def more_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ More Options",
        reply_markup=get_more_options_menu()
    )

async def system_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    await update.message.reply_text(
        "🛠 System Controls",
        reply_markup=get_system_menu()
    )

async def show_shortcuts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⌨️ Keyboard Shortcuts",
        reply_markup=get_shortcuts_menu()
    )

async def press_shortcut(update: Update, context: ContextTypes.DEFAULT_TYPE, shortcut_name):
    try:
        if shortcut_name in SHORTCUTS:
            kb.press_and_release(SHORTCUTS[shortcut_name])
            await update.message.reply_text(f"⌨️ {shortcut_name.title()} shortcut pressed")
        else:
            await update.message.reply_text("❌ Shortcut not found")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== SYSTEM CONTROL FUNCTIONS =====
async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(SCREENSHOT_PATH)
        await update.message.reply_photo(
            photo=open(SCREENSHOT_PATH, 'rb'),
            caption="📸 Screenshot captured"
        )
        os.remove(SCREENSHOT_PATH)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def capture_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(PHOTO_PATH, frame)
            await update.message.reply_photo(
                photo=open(PHOTO_PATH, 'rb'),
                caption="📷 Photo captured"
            )
            os.remove(PHOTO_PATH)
        else:
            await update.message.reply_text("❌ Couldn't access camera")
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def set_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /volume [0-100]")
            return
            
        volume = int(context.args[0])
        if not 0 <= volume <= 100:
            await update.message.reply_text("Volume must be 0-100")
            return
            
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_ctrl = interface.QueryInterface(IAudioEndpointVolume)
        volume_ctrl.SetMasterVolumeLevelScalar(volume/100, None)
        SystemState.current_volume = volume/100
        await update.message.reply_text(f"🔊 Volume set to {volume}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_volume = min(SystemState.current_volume + 0.1, 1.0)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        SystemState.current_volume = new_volume
        await update.message.reply_text(f"🔊 Volume increased to {int(new_volume*100)}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_volume = max(SystemState.current_volume - 0.1, 0.0)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        SystemState.current_volume = new_volume
        await update.message.reply_text(f"🔉 Volume decreased to {int(new_volume*100)}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def set_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /brightness [0-100]")
            return
            
        brightness = int(context.args[0])
        if not 0 <= brightness <= 100:
            await update.message.reply_text("Brightness must be 0-100")
            return
            
        sbc.set_brightness(brightness)
        await update.message.reply_text(f"🔅 Brightness set to {brightness}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def increase_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current = sbc.get_brightness()[0]
        new_brightness = min(current + 10, 100)
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(f"🔅 Brightness increased to {new_brightness}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def decrease_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current = sbc.get_brightness()[0]
        new_brightness = max(current - 10, 0)
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(f"🔅 Brightness decreased to {new_brightness}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== KEYBOARD CONTROL FUNCTIONS =====
async def next_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('ctrl+tab')
        await update.message.reply_text("➡️ Switched to next tab")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def prev_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('ctrl+shift+tab')
        await update.message.reply_text("⬅️ Switched to previous tab")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('tab')
        await update.message.reply_text("↔️ Tab key pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_space(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('space')
        await update.message.reply_text("␣ Space pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def refresh_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('f5')
        await update.message.reply_text("🔄 Page refreshed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('up')
        await update.message.reply_text("⬆️ Up arrow pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('down')
        await update.message.reply_text("⬇️ Down arrow pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('left')
        await update.message.reply_text("⬅️ Left arrow pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_right(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('right')
        await update.message.reply_text("➡️ Right arrow pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('home')
        await update.message.reply_text("🏠 Home key pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('end')
        await update.message.reply_text("🔚 End key pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_backspace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('backspace')
        await update.message.reply_text("🔙 Backspace pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('enter')
        await update.message.reply_text("↵ Enter pressed")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def zoom_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('ctrl+plus')
        await update.message.reply_text("🔍 Zoomed in")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def zoom_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('ctrl+-')
        await update.message.reply_text("🔎 Zoomed out")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def undo_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('ctrl+z')
        await update.message.reply_text("↩️ Undo action")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def redo_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('ctrl+y')
        await update.message.reply_text("↪️ Redo action")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def swap_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kb.press_and_release('alt+tab')
        await update.message.reply_text("🔄 Swapped application")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def type_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /type [text to type]")
        return
    
    text = ' '.join(context.args)
    try:
        kb.write(text)
        await update.message.reply_text(f"⌨️ Typed: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /press [key]")
        return
    
    key = context.args[0].lower()
    try:
        kb.press_and_release(key)
        await update.message.reply_text(f"⌨️ Pressed: {key}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== ADMIN FUNCTIONS =====
async def shutdown_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_shutdown')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_shutdown')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛑 Are you sure you want to shutdown?",
        reply_markup=reply_markup
    )

async def restart_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_restart')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_restart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔄 Are you sure you want to restart?",
        reply_markup=reply_markup
    )

async def lock_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    try:
        if platform.system() == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            await update.message.reply_text("🔒 System locked")
        else:
            await update.message.reply_text("❌ Only Windows supported")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def unlock_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only")
        return
    
    try:
        # This would require integration with Windows Hello or other auth methods
        # For now just showing a message
        await update.message.reply_text("🔓 Please unlock system manually")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_shutdown':
        await query.edit_message_text("🛑 Shutting down...")
        os.system("shutdown /s /t 1")
    elif query.data == 'cancel_shutdown':
        await query.edit_message_text("✅ Shutdown canceled")
    elif query.data == 'confirm_restart':
        await query.edit_message_text("🔄 Restarting...")
        os.system("shutdown /r /t 1")
    elif query.data == 'cancel_restart':
        await query.edit_message_text("✅ Restart canceled")

# ===== MAIN FUNCTION =====
def main():
    system_state = SystemState()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("system", system_info))
    app.add_handler(CommandHandler("screenshot", take_screenshot))
    app.add_handler(CommandHandler("webcam", capture_webcam))
    app.add_handler(CommandHandler("volume", set_volume))
    app.add_handler(CommandHandler("brightness", set_brightness))
    app.add_handler(CommandHandler("shutdown", shutdown_system))
    app.add_handler(CommandHandler("restart", restart_system))
    app.add_handler(CommandHandler("lock", lock_system))
    app.add_handler(CommandHandler("type", type_text))
    app.add_handler(CommandHandler("press", press_key))
    app.add_handler(CommandHandler("shortcuts", show_shortcuts_menu))
    
    # Message handler for buttons
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Advanced System Control Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    finally:
        SystemState().clean_temp_files()