#main_module.py
 
# Import necessary libraries
import asyncio
import logging
import aiohttp
import discord

# Import local modules
from discord.ext import commands
from telegram import Update, ext
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from token_data import PPTOKEN, IMAGEDIR, DISCOTOKE
from disco_utils import setup_event_handlers
from tele_utils import tele_read_message
from tele_disco_periodic_posting_tasks import periodic_posting_task

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants
IMAGE_DIRECTORY = IMAGEDIR
POST_INTERVAL = 3 * 60 * 60

# Define the main function
async def main():
    # Create a new Discord client with default Intents
    intents = discord.Intents.default()
    intents.messages = True
    intents.members = True
    intents.message_content = True
    discord_client = discord.Client(intents=intents)
    bot = commands.Bot(command_prefix='!', intents=intents)

    # Setup the Telegram bot
    application = Application.builder().token(PPTOKEN).build()
    # Setup Discord event handlers
    await setup_event_handlers(discord_client)
    
    # Create a new aiohttp session
    async with aiohttp.ClientSession() as session:
        # Manually initialize and start the Telegram application to avoid 'run_polling'
        await application.initialize()
        telegram_task = asyncio.create_task(application.start())
        # Initialize periodic_posting_task as an asyncio task
        periodic_task = asyncio.create_task(periodic_posting_task(session, discord_client, IMAGE_DIRECTORY, POST_INTERVAL))
        # Initialize tele_read_message_task as an asyncio task
        tele_read_message_task = asyncio.create_task(tele_read_message(session, discord_client))
        # Await all tasks concurrently
        await asyncio.gather(
            discord_client.start(DISCOTOKE),
            telegram_task,
            periodic_task,
            tele_read_message_task
        )
        # After all tasks are finished or cancelled, stop the Telegram and Discord Bot application gracefully
        await application.stop()

if __name__ == "__main__":
    logging.info("Starting application...")
    asyncio.run(main())
