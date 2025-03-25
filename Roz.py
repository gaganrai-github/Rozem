from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, CommandHandler
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import IAudioEndpointVolume
import os
import subprocess
import time
import keyboard
import psutil
import pyautogui
import cv2
import webbrowser
from telegram import Update

# Use environment variables for security
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7070124825:AAFSnUIo0c-b_7dsMj8fFL_rUILLL3i7ab8")

# Initialize the Application with your bot token
app = Application.builder().token(BOT_TOKEN).build()

# ALLOWED_USERS = [5285057277]  # Replace with the Telegram user IDs of allowed users
ALLOWED_USER_ID = 5285057277

response_dict = {
    "hello": "Hello! How are you, sir?",
    "hi": "Hi! How can I assist you today?",
    "how are you": "I'm just a bot, but I'm functioning perfectly!",
    "what is your name": "I am your friendly chatbot. You can call me Bot!",
    "bye": "Goodbye! Have a great day!"
}

shortcuts = {
    'copy': 'ctrl+c',
    'cut': 'ctrl+x',
    'paste': 'ctrl+v',
    'undo': 'ctrl+z',
    'redo': 'ctrl+y',
    'save': 'ctrl+s',
    'open': 'ctrl+o',
    'print': 'ctrl+p',
    'select all': 'ctrl+a',
    'find': 'ctrl+f',
    'new': 'ctrl+n',
    'close': 'ctrl+w',
    'new folder': 'ctrl+shift+n',
    'reopen closed tab': 'ctrl+shift+t',
    'next tab': 'ctrl+tab',
    'previous tab': 'ctrl+shift+tab',
    'new tab': 'ctrl+t',
    'underline': 'ctrl+u',
    'bold': 'ctrl+b',
    'italic': 'ctrl+i',
    'open start menu': 'ctrl+esc',
    'close window': 'alt+f4',
    'switch apps': 'alt+tab',
    'window menu': 'alt+space',
    'show desktop': 'windows+d',
    'file explorer': 'windows+e',
    'run': 'windows+r',
    'lock computer': 'windows +l',
    'task view': 'windows+tab',
    'help': 'f1',
    'rename': 'f2',
    'search': 'f3',
    'address bar': 'f4',
    'refresh': 'f5',
    'cycle through elements': 'f6',
    'spell check': 'f7',
    'extend selection': 'f8',
    'update fields': 'f9',
    'activate menu': 'f10',
    'toggle fullscreen': 'f11',
    'save as': 'f12',
    'cancel': 'esc',
    'hold for uppercase': 'shift',
    'right-click': 'shift+f10',
    'change case': 'shift+f3',
    'shrink selection': 'shift+f8',
    'task manager': 'ctrl+shift+esc',
    'zoom in': 'ctrl+plus',
    'zoom out': 'ctrl+-',
    'reset zoom': 'ctrl+0',
    'clear browsing data': 'ctrl+shift+delete',
    'new incognito window': 'ctrl+shift+n',
    'private browsing': 'ctrl+shift+p',
    'navigate tabs backward': 'ctrl+shift+tab',
    'switch to next window': 'ctrl+alt+tab',
    'switch to previous window': 'ctrl+alt+shift+tab',
    'open new tab': 'ctrl+alt+t',
    'open new private window': 'ctrl+alt+p',
    'open developer tools': 'ctrl+alt+i',
    'open console': 'ctrl+alt+c',
    'view page source': 'ctrl+alt+u',
    'find in page': 'ctrl+alt+f',
    'lock screen orientation': 'ctrl+alt+l',
    'reload': 'ctrl+alt+r',
    'save page as': 'ctrl+alt+s',
    'close current tab': 'ctrl+alt+w',
    'quit browser': 'ctrl+alt+q',
    'backslash': '|',
    # Add more shortcuts here...
}
async def send_shortcut_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message with shortcut buttons + Hide Button."""
    keyboard_buttons = [[InlineKeyboardButton(name, callback_data=name)] for name in shortcuts.keys()]
    
    # Adding "Hide Buttons" at the end
    keyboard_buttons.append([InlineKeyboardButton("🛑 Hide Buttons", callback_data="hide_buttons")])

    reply_markup = InlineKeyboardMarkup(keyboard_buttons)

    sent_message = await update.message.reply_text("🎹 *Press a button to trigger a shortcut:*", 
                                                   reply_markup=reply_markup, 
                                                   parse_mode="Markdown")
    
    # Store the message ID to delete it later
    context.user_data["last_message_id"] = sent_message.message_id

# Callback function to handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulate shortcut key press and delete the message when hide is clicked."""
    query = update.callback_query
    await query.answer()

    shortcut_name = query.data

    if shortcut_name == "hide_buttons":
        # Delete the message containing the buttons
        if "last_message_id" in context.user_data:
            try:
                await query.message.delete()
            except Exception as e:
                pass
        
        # Send confirmation
        await query.message.reply_text("🔴 *Shortcut buttons hidden! Use /shortcuts to show again.*", parse_mode="Markdown")
        return

    shortcut_keys = shortcuts.get(shortcut_name, None)

    # Simulate the key press
    if shortcut_keys:
        keyboard.send(shortcut_keys)
        await query.message.reply_text(f"✅ *{shortcut_name}* shortcut triggered! (`{shortcut_keys}`)", parse_mode="Markdown")
    else:
        await query.message.reply_text("⚠️ Shortcut not found.")
  # Replace with the actual user ID of the allowed user

# Middleware to check if the user is authorized
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ALLOWED_USER_ID:
        return True
    else:
        await update.message.reply_text("❌ Access Denied: You are not authorized to use this bot.")
        return False


user_id = None
async def get_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  # Get the user details
    chat = update.effective_chat  # Get the chat details
    global user_id
    # Extract user information
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name if user.last_name else "Not Set"
    username = f"@{user.username}" if user.username else "Not Set"
    chat_id = chat.id
    return user_id 
# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_authorized(update, context):
        keyboard = [
            [InlineKeyboardButton("YouTube", callback_data='youtube'),
             InlineKeyboardButton("Open WhatsApp", callback_data='open_whatsapp')],
            [InlineKeyboardButton("System Info", callback_data='system_info'),
             InlineKeyboardButton("Take Screenshot", callback_data='screenshot')],
            [InlineKeyboardButton("Take Photo", callback_data='click_photo')],
            [InlineKeyboardButton("Menu", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Hello sir, Welcome to the Bot. Please choose an option below:", reply_markup=reply_markup
        )

########### Menu ############
main_menu_buttons = [
    [KeyboardButton("🔃 Swap App"), KeyboardButton("🖥️ System Info")],
    [KeyboardButton("📸 Screenshot"), KeyboardButton("📷 Click Photo")],
    [KeyboardButton("🔁 Prev Tab"),KeyboardButton("TAB"),KeyboardButton("🔁 Next Tab")],
    [KeyboardButton("Space"), KeyboardButton("Refress")],
    [KeyboardButton("ℹ️ Help"), KeyboardButton("⚙️ More Options")] 
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)

# Create a submenu for "⚙️ More Options"
more_options_buttons = [
    [KeyboardButton("📸 Screenshot"), KeyboardButton("📲 Show Apps")],
    [KeyboardButton("⬆️"), KeyboardButton("⬅️"), KeyboardButton("➡️"), KeyboardButton("⬇️")],
    [KeyboardButton("Home"), KeyboardButton("End"), KeyboardButton("🔙"), KeyboardButton("↩️")],
    [KeyboardButton("🔍 Zoom IN"),KeyboardButton("Space"),KeyboardButton("🔎 Zoom OUT")],
    # [KeyboardButton("Refress"),KeyboardButton("🔁 Next Tab"), KeyboardButton("🔁 Prev Tab"),],
    # [KeyboardButton("⬆️ UP")],  
    # [KeyboardButton("⬅️ LEFT"), KeyboardButton("➡️ RIGHT")],  
    # [KeyboardButton("⬇️ DOWN")],
    [KeyboardButton("⏪ Main Menu"),KeyboardButton("⏩ Next Menu")]
]
more_options_markup = ReplyKeyboardMarkup(more_options_buttons, resize_keyboard=True)

system_buttons = [
    [KeyboardButton("📸 Screenshot"), KeyboardButton("🔓 Unlock System")],
    [KeyboardButton("🔅➕"), KeyboardButton("🔅➖"), KeyboardButton("🔉"), KeyboardButton("🔊")],
    [KeyboardButton("Undu"), KeyboardButton("Redu")],
    [KeyboardButton("⏪ Previus Menu"),KeyboardButton("🏠 Menu"),KeyboardButton("⏩ Next Menu")]
]
system_markup = ReplyKeyboardMarkup(system_buttons, resize_keyboard=True)

# Command: Start
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello sir, Welcome to the Bot. Choose an option from the buttons below:",
        reply_markup=main_menu_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_authorized(update, context):
        await update.message.reply_text("""Available Commands:
        /youtube - To get the YouTube URL
        /open_whatsapp - To Open WhatsApp
        /system_info - To get system information 
        /screenshot - Take a screenshot of your system
        /click_photo - Take a photo using the webcam                                 
        You can also type messages like 'hello', 'bye', etc., and I will respond!""")

async def youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message
    await message.reply_text("YouTube Link => https://www.youtube.com/")


# Example for 'open_whatsapp'
async def open_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message

    keyboard.send('windows')
    time.sleep(0.5)
    keyboard.write('WhatsApp')
    time.sleep(1)
    keyboard.send('enter')
    await message.reply_text("WhatsApp opened successfully.")


async def openfunction(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    app_name = query.replace("open ", "").strip()
    keyboard.send('windows')
    time.sleep(0.5)
    keyboard.write(app_name)
    time.sleep(1)
    keyboard.send('enter')
    await update.message.reply_text(f"Opened {app_name} successfully.")

async def typing(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    text_to_type = query.replace("type ", "").replace("write ", "").strip()
    keyboard.write(text_to_type)
    await update.message.reply_text("Typing completed successfully.")

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    key = query.replace("key press ", "").strip()
    try:
        keyboard.send(key)
        await update.message.reply_text(f"Pressed key: {key} successfully.")
    except Exception as e:
        await update.message.reply_text(f"Error pressing key: {key}. Please try again.")

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the update is a callback query or regular message
    message = update.message if update.message else update.callback_query.message

    battery = psutil.sensors_battery()
    if battery:
        plugged = "Plugged In" if battery.power_plugged else "Not Plugged In"
        percent = battery.percent
        await message.reply_text(f"Battery is {percent}% charged and {plugged}.")
    else:
        await message.reply_text("Unable to retrieve battery information.")
    
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    await message.reply_text(f"CPU usage: {cpu_usage}%\nMemory usage: {memory_usage}%")


async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if it's a callback query or regular message
    message = update.message if update.message else update.callback_query.message

    screenshot_path = "screenshot.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    # Send message after taking screenshot
    await message.reply_text("Screenshot taken successfully. Sharing it with you...")
    
    # Send the screenshot photo
    await message.reply_photo(photo=open(screenshot_path, "rb"))


async def click_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if it's a callback query or regular message
    message = update.message if update.message else update.callback_query.message

    photo_path = "photo.jpg"
    camera = cv2.VideoCapture(0)  # Open the webcam
    return_value, image = camera.read()  # Capture a single frame
    if return_value:
        cv2.imwrite(photo_path, image)  # Save the photo
        await message.reply_text("Photo clicked successfully. Sharing it with you...")
        await message.reply_photo(photo=open(photo_path, "rb"))
    else:
        await message.reply_text("Failed to capture photo. Please ensure your camera is connected.")
    
    camera.release()
    cv2.destroyAllWindows()

async def show_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("windows+tab")
    await update.message.reply_text(f"Show Apps successful")
    
async def Chenge_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("ctrl+tab")
    await update.message.reply_text(f"Chenge 🔁 successful")

async def Press_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("enter")
    await update.message.reply_text(f"Press Enter successful")

async def Chenge_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("alt+tab")
    await update.message.reply_text(f"Chenge Tab successful")

async def up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("up")
    await update.message.reply_text(f"⬆️ Press successful")

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("down")
    await update.message.reply_text(f"⬇️ Press successful")

async def left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("left")
    await update.message.reply_text(f"⬅️ Press successful")

async def right(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("right")
    await update.message.reply_text(f"➡️ Press successful")
    
async def backspace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("backspace")
    await update.message.reply_text(f"🔙 Press successful")

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("home")
    await update.message.reply_text(f"Home Press successful")

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("end")
    await update.message.reply_text(f"End Press successful")

async def zoomin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("ctrl+plus")
    await update.message.reply_text(f"Zoom IN successful")

async def zoomout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("ctrl+-")
    await update.message.reply_text(f"Zoom OUT successful")

async def pre_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("ctrl+shift+tab")
    await update.message.reply_text(f"Previus Tab successful")

async def refress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("f5")
    await update.message.reply_text(f"Refress successful")

async def tab_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("tab")
    await update.message.reply_text(f"TAB press successful")

async def space(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("space")
    await update.message.reply_text(f"Space press successful")

async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("ctrl+z")
    await update.message.reply_text(f"Undo successful")

async def redu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard.send("ctrl+y")
    await update.message.reply_text(f"Redu successful")

async def increase_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_brightness = sbc.get_brightness()[0]  # List se first element access karo
    new_brightness = current_brightness + 10  # 1% increase
    if new_brightness > 100:
        new_brightness = 100  # Maximum 100% brightness
    sbc.set_brightness(new_brightness)
    await update.message.reply_text(f"New brightness: {new_brightness}%")

async def decrease_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_brightness = sbc.get_brightness()[0]  # List se first element access karo
    new_brightness = current_brightness - 10  # 1% decrease
    if new_brightness < 0:
        new_brightness = 0  # Minimum 0% brightness
    sbc.set_brightness(new_brightness)
    await update.message.reply_text(f"New brightness: {new_brightness}%")

async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar()  # Current volume dekho
    new_volume = current_volume + 0.10  # 1% increase
    if new_volume > 1.0:
        new_volume = 1.0  # Maximum volume
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    await update.message.reply_text(f"New volume: {new_volume * 100}%")

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar()  # Current volume  dekho
    new_volume = current_volume - 0.10  # 1% decrease
    if new_volume < 0.0:
        new_volume = 0.0  # Minimum volume
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    await update.message.reply_text(f"New volume: {new_volume * 100}%")

async def find_shortkut(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    query = query.replace("press ","")
    query = query.replace("and ","end")
    try:                                      
        for k, v in shortcuts.items():
            if v == query:
                keyboard.write(k)
                await update.message.reply_text(f"press {v} successful")
                break
            elif k == query:
                keyboard.send(v)
                await update.message.reply_text(f"press {k} successful")
                break
    except Exception as e:
        print(e)
        await update.message.reply_text("please say that again sir")

async def chatbot_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    user_input = update.message.text
    if await is_authorized(update, context):   
        if "name" in query:
            response = response_dict.get(query, "My name is ROZ.")
            await update.message.reply_text(response)
        elif "open" in query:
            await openfunction(update, context, query)
        elif "write" in query or "type" in query:
            await typing(update, context, query)
        elif "key press" in query:
            await press_key(update, context, query)
        elif "press" in query:
            await find_shortkut(update, context, query)
        elif 'google' in query:
             query = query.replace("google", "")
             search_query = f"https://www.google.com/search?q={query}"
             webbrowser.open(search_query)
        elif 'youtube' in query:
            query = query.replace("youtube", "")
            search_query = f"https://www.youtube.com/search?q={query}"
            webbrowser.open(search_query)
    
    
    
        elif user_input == "🔃 Swap App":
            await Chenge_window(update, context)
        elif user_input == "🖥️ System Info":
            await system_info(update, context)
        elif user_input == "📸 Screenshot":
            await take_screenshot(update, context)
        elif user_input == "📷 Click Photo":
            await click_photo(update, context)

        elif user_input == "🔁 Next Tab":
            await Chenge_tab(update, context)
        elif user_input == "TAB":
            await tab_key(update, context)
        elif user_input == "🔁 Prev Tab":
            await pre_tab(update, context)
        elif user_input == "Space":
            await space(update, context)
        elif user_input == "Refress":
            await refress(update, context)       

        elif user_input == "↩️ Enter":
            await Press_enter(update, context)
        elif user_input == "ℹ️ Help":
            await help_command(update, context)
        elif user_input == "⚙️ More Options":
            await update.message.reply_text(
                "More options menu. Choose an option:",
                reply_markup=more_options_markup
            )
        elif user_input == "📲 Show Apps":
            await show_apps(update, context)

        elif user_input == "⬆️":
            await up(update, context)       
        elif user_input == "⬇️":
            await down(update, context)       
        elif user_input == "➡️":
            await right(update, context)
        elif user_input == "⬅️":
            await left(update, context)
        elif user_input == "Home":
            await home(update, context)
        elif user_input == "End":
            await end(update, context)
        elif user_input == "🔙":
            await backspace(update, context)
        elif user_input == "↩️":
            await Press_enter(update, context)
        elif user_input == "🔍 Zoom IN":
            await zoomin(update, context)
        elif user_input == "🔎 Zoom OUT":
            await zoomout(update, context)
        
        elif user_input == "⏩ Next Menu":
            await update.message.reply_text(
                "More options menu. Choose an option:",
                reply_markup=system_markup
            )
        ######## MENU 3 ######
        elif user_input == "🔅➕":
            await increase_brightness(update, context)
        elif user_input == "🔅➖":
            await decrease_brightness(update, context)
        elif user_input == "🔊":
            await increase_volume(update, context)
        elif user_input == "🔉":
            await decrease_volume(update, context)
        elif user_input == "Undu":
            await undo(update, context)
        elif user_input == "Redu":
            await redu(update, context)
        
        elif user_input == "⏪ Previus Menu":
            await update.message.reply_text(
                "Back to the main menu:",
                reply_markup=more_options_markup
            )
        elif user_input == "🏠 Menu":
            await update.message.reply_text(
                "Back to the main menu:",
                reply_markup=main_menu_markup
            )
        elif user_input == "⏪ Main Menu":
            await update.message.reply_text(
                "Back to the main menu:",
                reply_markup=main_menu_markup
            )
            
        else:
            response = response_dict.get(query, "I'm sorry, I didn't understand that. Can you rephrase?")
            await update.message.reply_text(response)

# Callback query handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    data = query.data
    message = query.message  # Use query.message instead of update.message for callback queries
    
    if data == "youtube":
        await youtube_url(update, context)
    elif data == "open_whatsapp":
        await open_whatsapp(update, context)
    elif data == "system_info":
        await system_info(update, context)
    elif data == "screenshot":
        await take_screenshot(update, context)
    elif data == "click_photo":
        await click_photo(update, context)
    elif data == "menu":
        await menu(update,context)


# Register handlers
app.add_handler(CommandHandler("start", menu))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_response))
app.add_handler(CommandHandler("shortcuts", send_shortcut_buttons))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(button))

# Start the bot
if __name__ == "__main__":
    app.run_polling()
