# extra imports
import math, time, re, datetime, pytz, os
from config import Config, rkn

# pyrogram imports
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:  # Update every 10 seconds
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        eta = round((total - current) / speed) if speed > 0 else 0

        progress = "{0}{1}".format(
            ''.join(["▣" for i in range(math.floor(percentage / 5))]),
            ''.join(["▢" for i in range(20 - math.floor(percentage / 5))])
        )
        tmp = progress + rkn.RKN_PROGRESS.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            f"{eta}s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close")]])
            )
        except:
            pass

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ") if seconds else "")
    return tmp

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def send_log(b, u):
    if Config.LOG_CHANNEL:
        curr = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        log_message = (
            "**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\n"
            f"Uꜱᴇʀ: {u.mention}\n"
            f"Iᴅ: `{u.id}`\n"
            f"Uɴ: @{u.username}\n\n"
            f"Dᴀᴛᴇ: {curr.strftime('%d %B, %Y')}\n"
            f"Tɪᴍᴇ: {curr.strftime('%I:%M:%S %p')}\n\n"
            f"By: {b.mention}"
        )
        await b.send_message(Config.LOG_CHANNEL, log_message)

async def get_seconds_first(time_string):
    conversion_factors = {
        's': 1,
        'min': 60,
        'hour': 3600,
        'day': 86400,
        'month': 86400 * 30,
        'year': 86400 * 365
    }
    parts = time_string.split()
    total_seconds = 0
    for i in range(0, len(parts), 2):
        value = int(parts[i])
        unit = parts[i+1].rstrip('s')
        total_seconds += value * conversion_factors.get(unit, 0)
    return total_seconds

async def get_seconds(time_string):
    conversion_factors = {
        's': 1,
        'min': 60,
        'hour': 3600,
        'day': 86400,
        'month': 86400 * 30,
        'year': 86400 * 365
    }
    total_seconds = 0
    pattern = r'(\d+)\s*(\w+)'
    matches = re.findall(pattern, time_string)
    for value, unit in matches:
        total_seconds += int(value) * conversion_factors.get(unit, 0)
    return total_seconds

def add_prefix_suffix(input_string, prefix='', suffix=''):
    pattern = r'(?P<filename>.*?)(\.\w+)?$'
    match = re.search(pattern, input_string)
    if match:
        filename = match.group('filename')
        extension = match.group(2) or ''
        prefix_str = f"{prefix} " if prefix else ""
        suffix_str = f" {suffix}" if suffix else ""
        return f"{prefix_str}{filename}{suffix_str}{extension}"
    return input_string

async def remove_path(*paths):
    for path in paths:
        if path and os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)

def metadata_text(metadata_text):
    author = None
    title = None
    video_title = None
    audio_title = None
    subtitle_title = None
    flags = [i.strip() for i in metadata_text.split('--')]
    for f in flags:
        if "change-author" in f:
            author = f[len("change-author"):].strip()
        if "change-title" in f:
            title = f[len("change-title"):].strip()
        if "change-video-title" in f:
            video_title = f[len("change-video-title"):].strip()
        if "change-audio-title" in f:
            audio_title = f[len("change-audio-title"):].strip()
        if "change-subtitle-title" in f:
            subtitle_title = f[len("change-subtitle-title"):].strip()
    return author, title, video_title, audio_title, subtitle_title

def split_file(file_path, chunk_size=50*1024*1024):
    chunks = []
    with open(file_path, 'rb') as f:
        i = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            chunk_path = f"{file_path}.part{i}"
            with open(chunk_path, 'wb') as cf:
                cf.write(chunk_data)
            chunks.append(chunk_path)
            i += 1
    return chunks