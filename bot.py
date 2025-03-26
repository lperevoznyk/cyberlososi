import discord
import os
from discord.ext import commands
import logging
import configparser

config = configparser.ConfigParser()
config.read('bot.ini')
TOKEN = config.get('bot', 'token')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Commands: {', '.join([str(command) for command in bot.commands])}")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        extension_name = filename[:-3]
        try:
            bot.load_extension(f"cogs.{extension_name}")
            print(f"Loaded {extension_name} cog successfully!")
        except Exception as e:
            print(f"Failed to load extension {extension_name}: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"Received message: {message.content}")
    await bot.process_commands(message)


@bot.event
async def on_command(ctx):
    print(f"Command {ctx.command} called!")


logging.basicConfig(level=logging.INFO)
bot.run(TOKEN)