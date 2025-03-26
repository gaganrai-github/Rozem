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
    ReplyKeyboardRemove,
    InputFile
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
ALLOWED_USERS = {5285057277: "Admin"}  # Format: {user_id: "role"}
REQUEST_TIMEOUT = 30  # seconds for confirmation timeout
SCREENSHOT_PATH = os.path.join("temp_data", "screenshot.png")
PHOTO_PATH = os.path.join("temp_data", "photo.jpg")
TEMP_DIR = "temp_data"

# ===== SYSTEM STATE MANAGEMENT =====
class SystemState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        self.pending_actions = {}
        self.media_sessions = {}
        self.volume = 0.5
        self.is_muted = False
        self.brightness = sbc.get_brightness()[0] if sbc.get_brightness() else 50
        self.create_temp_dir()
    
    def create_temp_dir(self):
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

def get_user_role(user_id):
    return ALLOWED_USERS.get(user_id, "Unauthorized")

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
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_system_info():
    info = {}
    
    # Basic system info
    uname = platform.uname()
    info["system"] = {
        "os": f"{uname.system} {uname.release}",
        "version": uname.version,
        "hostname": socket.gethostname(),
        "processor": uname.processor,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # CPU info
    cpu_freq = psutil.cpu_freq()
    info["cpu"] = {
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "usage": psutil.cpu_percent(interval=1),
        "freq": {
            "current": cpu_freq.current if cpu_freq else None,
            "min": cpu_freq.min if cpu_freq else None,
            "max": cpu_freq.max if cpu_freq else None
        }
    }
    
    # Memory info
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    info["memory"] = {
        "total": mem.total,
        "used": mem.used,
        "free": mem.free,
        "percent": mem.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_free": swap.free,
        "swap_percent": swap.percent
    }
    
    # Disk info
    disks = []
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        disks.append({
            "device": part.device,
            "mount": part.mountpoint,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        })
    info["disks"] = disks
    
    # Network info
    net_io = psutil.net_io_counters()
    net_if = psutil.net_if_addrs()
    info["network"] = {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "interfaces": len(net_if)
    }
    
    # GPU info
    gpus = GPUtil.getGPUs()
    info["gpu"] = [{
        "name": gpu.name,
        "load": gpu.load * 100,
        "temp": gpu.temperature,
        "memory": f"{gpu.memoryUsed:.1f}/{gpu.memoryTotal:.1f} MB"
    } for gpu in gpus]
    
    # Battery info
    battery = psutil.sensors_battery()
    info["battery"] = {
        "percent": battery.percent if battery else None,
        "power_plugged": battery.power_plugged if battery else None,
        "secsleft": battery.secsleft if battery else None
    }
    
    return info

# ===== BOT COMMAND HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user.id):
        await update.message.reply_text("❌ Unauthorized access. Your ID has been logged.")
        print(f"Unauthorized access attempt from {user.id}")
        return
    
    welcome_msg = f"""
👋 Welcome *{user.first_name}*!

🔹 Your role: *{get_user_role(user.id)}*
🔹 System: *{platform.system()} {platform.release()}*
🔹 Current time: *{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

💡 Use /help to see available commands
    """
    
    keyboard = [
        [InlineKeyboardButton("🖥 System Dashboard", callback_data='system_dashboard')],
        [InlineKeyboardButton("⚙️ Quick Controls", callback_data='quick_controls')],
        [InlineKeyboardButton("📊 Performance", callback_data='performance')]
    ]
    
    if is_admin(user.id):
        keyboard.append([InlineKeyboardButton("🛑 Admin Controls", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        welcome_msg, 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔷 *System Control Bot Help* 🔷

*Basic Commands:*
/start - Start the bot
/help - Show this help message
/menu - Show control menu
/shortcuts - Keyboard shortcuts

*System Monitoring:*
/system - Detailed system info
/performance - Performance metrics
/processes - Running processes
/disks - Disk information
/network - Network information

*Control Commands:*
/screenshot - Take screenshot
/webcam - Take photo with webcam
/volume [0-100] - Set volume level
/brightness [0-100] - Set brightness
/lock - Lock workstation
/sleep - Put system to sleep

*Admin Commands:*
/shutdown - Shutdown system
/restart - Restart system
/command [cmd] - Execute command
/process [kill/start] - Manage processes

*Media Controls:*
/media [play/pause/next/prev] - Control media
/mute - Toggle mute
/volup - Volume up
/voldown - Volume down

*File Operations:*
/list [path] - List directory
/read [file] - Read file
/download [file] - Download file
/upload - Upload file
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        info = get_system_info()
        
        # Format system info
        system_text = f"""
🖥️ *System Information Report* 🖥️

*System:*
- OS: {info['system']['os']}
- Version: {info['system']['version']}
- Hostname: {info['system']['hostname']}
- Boot Time: {info['system']['boot_time']}

*Hardware:*
- Processor: {info['system']['processor']}
- Cores: {info['cpu']['cores']} physical, {info['cpu']['threads']} logical
- CPU Usage: {info['cpu']['usage']}%
"""
        if info['cpu']['freq']['current']:
            system_text += f"- CPU Frequency: {info['cpu']['freq']['current']/1000:.2f} GHz "
            if info['cpu']['freq']['min'] and info['cpu']['freq']['max']:
                system_text += f"(min {info['cpu']['freq']['min']/1000:.2f}, max {info['cpu']['freq']['max']/1000:.2f})\n"
        
        system_text += f"""
*Memory:*
- RAM: {info['memory']['used']/1024/1024:.0f}MB / {info['memory']['total']/1024/1024:.0f}MB ({info['memory']['percent']}%)
- Swap: {info['memory']['swap_used']/1024/1024:.0f}MB / {info['memory']['swap_total']/1024/1024:.0f}MB ({info['memory']['swap_percent']}%)

*GPU:*
"""
        for gpu in info['gpu']:
            system_text += f"- {gpu['name']}: {gpu['load']:.1f}% load, {gpu['temp']}°C, Memory: {gpu['memory']}\n"
        
        if info['battery']['percent']:
            system_text += f"""
*Battery:*
- Percent: {info['battery']['percent']}%
- Status: {'Charging' if info['battery']['power_plugged'] else 'Discharging'}
- Time Left: {info['battery']['secsleft']/3600:.1f} hours
"""
        system_text += f"""
*Network:*
- Bytes Sent: {info['network']['bytes_sent']/1024/1024:.2f} MB
- Bytes Received: {info['network']['bytes_recv']/1024/1024:.2f} MB
- Interfaces: {info['network']['interfaces']} available
"""
        await update.message.reply_text(system_text, parse_mode="Markdown")
        
        # Send disk information
        disk_text = "*Disk Partitions:*\n"
        for disk in info['disks']:
            disk_text += (
                f"- {disk['device']} mounted on {disk['mount']}\n"
                f"  Total: {disk['total']/1024/1024/1024:.2f}GB, "
                f"Used: {disk['used']/1024/1024/1024:.2f}GB ({disk['percent']}%), "
                f"Free: {disk['free']/1024/1024/1024:.2f}GB\n"
            )
        await update.message.reply_text(disk_text, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting system info: {str(e)}")

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
        await update.message.reply_text(f"❌ Error capturing screenshot: {str(e)}")

async def capture_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(PHOTO_PATH, frame)
            await update.message.reply_photo(
                photo=open(PHOTO_PATH, 'rb'),
                caption="📷 Webcam photo captured"
            )
            os.remove(PHOTO_PATH)
        else:
            await update.message.reply_text("❌ Could not access webcam")
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        await update.message.reply_text(f"❌ Error capturing webcam photo: {str(e)}")

async def set_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(f"🔊 Current volume: {system_state.volume*100:.0f}%")
            return
            
        volume_level = int(context.args[0])
        if not 0 <= volume_level <= 100:
            await update.message.reply_text("Usage: /volume [0-100]")
            return
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(volume_level/100, None)
        system_state.volume = volume_level/100
        system_state.is_muted = False
        await update.message.reply_text(f"🔊 Volume set to {volume_level}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error setting volume: {str(e)}")

async def toggle_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(not system_state.is_muted, None)
        system_state.is_muted = not system_state.is_muted
        status = "muted 🔇" if system_state.is_muted else "unmuted 🔊"
        await update.message.reply_text(f"Sound is now {status}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error toggling mute: {str(e)}")

async def set_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(f"🔅 Current brightness: {system_state.brightness}%")
            return
            
        brightness = int(context.args[0])
        if not 0 <= brightness <= 100:
            await update.message.reply_text("Usage: /brightness [0-100]")
            return
        
        sbc.set_brightness(brightness)
        system_state.brightness = brightness
        await update.message.reply_text(f"🔅 Brightness set to {brightness}%")
    except Exception as e:
        await update.message.reply_text(f"❌ Error setting brightness: {str(e)}")

async def lock_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    try:
        if platform.system() == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        else:
            os.system("gnome-screensaver-command -l")
        await update.message.reply_text("🔒 System locked")
    except Exception as e:
        await update.message.reply_text(f"❌ Error locking system: {str(e)}")

async def sleep_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    try:
        if platform.system() == "Windows":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("systemctl suspend")
        await update.message.reply_text("💤 System going to sleep")
    except Exception as e:
        await update.message.reply_text(f"❌ Error putting system to sleep: {str(e)}")

async def shutdown_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm Shutdown", callback_data='confirm_shutdown')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_shutdown')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    system_state.pending_actions[user.id] = {
        "action": "shutdown",
        "time": time.time()
    }
    
    await update.message.reply_text(
        "🛑 Are you sure you want to shutdown the system?",
        reply_markup=reply_markup
    )
    
    # Schedule timeout for confirmation
    Timer(REQUEST_TIMEOUT, lambda: timeout_action(user.id, "shutdown")).start()

async def restart_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm Restart", callback_data='confirm_restart')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_restart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    system_state.pending_actions[user.id] = {
        "action": "restart",
        "time": time.time()
    }
    
    await update.message.reply_text(
        "🔄 Are you sure you want to restart the system?",
        reply_markup=reply_markup
    )
    
    # Schedule timeout for confirmation
    Timer(REQUEST_TIMEOUT, lambda: timeout_action(user.id, "restart")).start()

def timeout_action(user_id, action):
    if user_id in system_state.pending_actions and system_state.pending_actions[user_id]["action"] == action:
        del system_state.pending_actions[user_id]

async def execute_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    action = query.data.split('_')[1]
    
    if user.id not in system_state.pending_actions or system_state.pending_actions[user.id]["action"] != action:
        await query.edit_message_text(f"❌ {action.capitalize()} request expired or invalid")
        return
    
    if query.data.startswith('confirm_'):
        await query.edit_message_text(f"⏳ System {action} in progress...")
        
        if action == "shutdown":
            if platform.system() == "Windows":
                os.system("shutdown /s /t 1")
            else:
                os.system("shutdown -h now")
        elif action == "restart":
            if platform.system() == "Windows":
                os.system("shutdown /r /t 1")
            else:
                os.system("shutdown -r now")
    else:
        del system_state.pending_actions[user.id]
        await query.edit_message_text(f"✅ {action.capitalize()} canceled")

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /command <command_to_execute>")
        return
    
    cmd = ' '.join(context.args)
    result = execute_command(cmd)
    
    if result["success"]:
        response = f"✅ Command executed successfully\n\nOutput:\n{result['output']}"
    else:
        response = f"❌ Command failed\n\nError:\n{result['error']}"
    
    # Split long messages
    if len(response) > 4000:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for part in parts:
            await update.message.reply_text(part)
    else:
        await update.message.reply_text(response)

async def media_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        keyboard = [
            [InlineKeyboardButton("⏯ Play/Pause", callback_data='media_play_pause')],
            [InlineKeyboardButton("⏭ Next Track", callback_data='media_next')],
            [InlineKeyboardButton("⏮ Previous Track", callback_data='media_prev')],
            [InlineKeyboardButton("🔇 Mute", callback_data='media_mute')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🎵 Media Controls:",
            reply_markup=reply_markup
        )
        return
    
    control = context.args[0].lower()
    try:
        if control in ['play', 'pause', 'playpause']:
            kb.press_and_release('play/pause')
            await update.message.reply_text("⏯ Play/Pause")
        elif control in ['next']:
            kb.press_and_release('next track')
            await update.message.reply_text("⏭ Next Track")
        elif control in ['prev', 'previous']:
            kb.press_and_release('previous track')
            await update.message.reply_text("⏮ Previous Track")
        else:
            await update.message.reply_text("Usage: /media [play/pause/next/prev]")
    except Exception as e:
        await update.message.reply_text(f"❌ Media control error: {str(e)}")

async def media_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action = query.data.split('_')[1]
    
    try:
        if action == "playpause":
            kb.press_and_release('play/pause')
            await query.edit_message_text("⏯ Play/Pause")
        elif action == "next":
            kb.press_and_release('next track')
            await query.edit_message_text("⏭ Next Track")
        elif action == "prev":
            kb.press_and_release('previous track')
            await query.edit_message_text("⏮ Previous Track")
        elif action == "mute":
            await toggle_mute(update, context)
    except Exception as e:
        await query.edit_message_text(f"❌ Media control error: {str(e)}")

async def list_directory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    path = context.args[0] if context.args else "."
    try:
        if not os.path.exists(path):
            await update.message.reply_text("❌ Path does not exist")
            return
        
        items = os.listdir(path)
        if not items:
            await update.message.reply_text(f"📂 Empty directory: {path}")
            return
        
        response = f"📂 Contents of {path}:\n\n"
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                response += f"📁 {item}/\n"
            else:
                size = os.path.getsize(full_path)
                response += f"📄 {item} ({size/1024:.1f} KB)\n"
        
        # Split long messages
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ Error listing directory: {str(e)}")

async def show_shortcuts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shortcuts = {
        'copy': 'ctrl+c',
        'paste': 'ctrl+v',
        'cut': 'ctrl+x',
        'undo': 'ctrl+z',
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
    
    try:
        shortcuts_text = "⌨️ *Keyboard Shortcuts*\n\n"
        for name, keys in shortcuts.items():
            shortcuts_text += f"• *{name.title()}*: `{keys}`\n"
        
        await update.message.reply_text(shortcuts_text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting shortcuts: {str(e)}")

async def remote_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remotetype [text to type]")
        return
    
    text = ' '.join(context.args)
    try:
        kb.write(text)
        await update.message.reply_text(f"⌨️ Typed: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error typing: {str(e)}")

async def run_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin privileges required")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /runapp [application name]")
        return
    
    app_name = ' '.join(context.args)
    try:
        if platform.system() == "Windows":
            os.startfile(app_name)
        else:
            os.system(f"xdg-open {app_name}")
        await update.message.reply_text(f"🚀 Launched: {app_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error launching application: {str(e)}")

# ===== MAIN FUNCTION =====
def main():
    # Create application and handlers
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # System monitoring commands
    app.add_handler(CommandHandler("system", system_info))
    
    # Control commands
    app.add_handler(CommandHandler("screenshot", take_screenshot))
    app.add_handler(CommandHandler("webcam", capture_webcam))
    app.add_handler(CommandHandler("volume", set_volume))
    app.add_handler(CommandHandler("mute", toggle_mute))
    app.add_handler(CommandHandler("brightness", set_brightness))
    app.add_handler(CommandHandler("lock", lock_system))
    app.add_handler(CommandHandler("sleep", sleep_system))
    
    # Admin commands
    app.add_handler(CommandHandler("shutdown", shutdown_system))
    app.add_handler(CommandHandler("restart", restart_system))
    app.add_handler(CommandHandler("command", run_command))
    
    # New features
    app.add_handler(CommandHandler("shortcuts", show_shortcuts))
    app.add_handler(CommandHandler("remotetype", remote_type))
    app.add_handler(CommandHandler("runapp", run_application))
    
    # Media commands
    app.add_handler(CommandHandler("media", media_control))
    
    # File operations
    app.add_handler(CommandHandler("list", list_directory))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(execute_action, pattern='^(confirm|cancel)_(shutdown|restart)$'))
    app.add_handler(CallbackQueryHandler(media_button_handler, pattern='^media_'))
    app.add_handler(CallbackQueryHandler(show_shortcuts, pattern='^show_shortcuts$'))
    
    # Start the bot
    print("🤖 System Control Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    finally:
        system_state.clean_temp_files()