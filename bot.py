import aiohttp
import asyncio
import warnings
import pytz
import datetime
import logging
import logging.config
import glob
import sys
import importlib.util
from pathlib import Path

# Pyrogram imports
import pyrogram.utils
from pyrogram import Client, __version__, errors
from pyrogram.raw.all import layer
import pyromod  # Import pyromod for conversational features

# Bot imports
from config import Config
from plugins.web_support import web_server
from plugins.file_rename import app

# Set minimum channel ID for Pyrogram
pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("BotLog.txt"),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class DigitalRenameBot(Client):
    def __init__(self):
        super().__init__(
            name="DigitalRenameBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15
        )

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()
            self.mention = me.mention
            self.username = me.username
            self.uptime = Config.BOT_UPTIME
            self.premium = Config.PREMIUM_MODE
            self.uploadlimit = Config.UPLOAD_LIMIT_MODE

            # Start web server
            web_app = aiohttp.web.AppRunner(await web_server())
            await web_app.setup()
            bind_address = "0.0.0.0"
            await aiohttp.web.TCPSite(web_app, bind_address, Config.PORT).start()
            logger.info(f"Web server started on {bind_address}:{Config.PORT}")

            # Load plugins
            path = "plugins/*.py"
            files = glob.glob(path)
            for name in files:
                try:
                    with open(name) as a:
                        patt = Path(a.name)
                        plugin_name = patt.stem.replace(".py", "")
                        plugins_path = Path(f"plugins/{plugin_name}.py")
                        import_path = f"plugins.{plugin_name}"
                        logger.info(f"Loading plugin: {import_path} from {plugins_path}")
                        if not plugins_path.exists():
                            logger.error(f"Plugin path does not exist: {plugins_path}")
                            continue
                        spec = importlib.util.spec_from_file_location(import_path, plugins_path)
                        if spec is None:
                            logger.error(f"Failed to create spec for {plugins_path}")
                            continue
                        load = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(load)
                        sys.modules[f"plugins.{plugin_name}"] = load
                        logger.info(f"Digital Botz Imported {plugin_name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")

            logger.info(f"{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")

            # Send startup messages to admins
            for id in Config.ADMIN:
                try:
                    if Config.STRING_SESSION:
                        await self.send_message(
                            id,
                            f"𝟮𝗚𝗕+ ғɪʟᴇ sᴜᴘᴘᴏʀᴛ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ʙᴏᴛ.\n\n"
                            f"Note: 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐩𝐫𝐞𝐦𝐢𝐮𝐦 𝐚𝐜𝐜𝐨ᴜɴ𝐭 𝐬𝐭𝐫𝐢ɴ𝐠 𝐬𝐞𝐬𝐬ɪ𝐨ɴ 𝐫𝐞𝐪𝐮𝐢𝐫𝐞ᴅ 𝐓𝐡𝐞𝐧 𝐬𝐮𝐩ᴘᴏʀ𝐭𝐬 𝟐𝐆𝐁+ 𝐟𝐢𝐥𝐞𝐬.\n\n"
                            f"**__{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**"
                        )
                    else:
                        await self.send_message(
                            id,
                            f"𝟮𝗚𝗕- ғɪʟᴇ sᴜᴘᴘᴏʀᴛ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ʙᴏᴛ.\n\n"
                            f"**__{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**"
                        )
                except Exception as e:
                    logger.error(f"Failed to send startup message to admin {id}: {e}")

            # Send message to log channel
            if Config.LOG_CHANNEL:
                try:
                    curr = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
                    date = curr.strftime("%d %B, %Y")
                    time = curr.strftime("%I:%M:%S %p")
                    await self.send_message(
                        Config.LOG_CHANNEL,
                        f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n"
                        f"📅 Dᴀᴛᴇ : `{date}`\n"
                        f"⏰ Tɪᴍᴇ : `{time}`\n"
                        f"🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n"
                        f"🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`"
                    )
                except Exception as e:
                    logger.error(f"Failed to send message to log channel: {e}")
                    print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

    async def stop(self, *args):
        for id in Config.ADMIN:
            try:
                await self.send_message(id, "**Bot Stopped....**")
            except Exception as e:
                logger.error(f"Failed to send stop message to admin {id}: {e}")
        logger.info("Bot Stopped 🙄")
        await super().stop()

bot_instance = DigitalRenameBot()

def main():
    async def start_services():
        try:
            if Config.STRING_SESSION:
                await asyncio.gather(
                    app.start(),  # Start the Pyrogram Client
                    bot_instance.start()  # Start the bot instance
                )
            else:
                await asyncio.gather(bot_instance.start())  # Start the bot instance
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            raise

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_services())
        loop.run_forever()
    except errors.FloodWait as ft:
        logger.info(f"Flood Wait Occurred, Sleeping For {ft.value} seconds")
        asyncio.sleep(ft.value)
        logger.info("Now Ready For Deploying!")
        loop.run_until_complete(start_services())
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        raise

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="There is no current event loop")
    try:
        main()
    except Exception as e:
        logger.error(f"Failed to run main: {e}")
        raise