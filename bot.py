import discord
import os
from discord.ext import commands

intents = discord.Intents.all()
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Commands: {', '.join([str(command) for command in bot.commands])}")

# 1. Manually load each cog by file name:
# bot.load_extension("cogs.foo")
# bot.load_extension("cogs.bar")

# 2. OR load all cogs dynamically:
# (You can loop through the cogs directory and load each .py file automatically)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        extension_name = filename[:-3]  # remove .py
        try:
            bot.load_extension(f"cogs.{extension_name}")
            print(f"Loaded {extension_name} cog successfully!")
        except Exception as e:
            print(f"Failed to load extension {extension_name}: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages sent by the bot itself

    print(f"Received message: {message.content}")  # Debug print
    await bot.process_commands(message)  # Ensure commands still work

@bot.event
async def on_command(ctx):
    print(f"Command {ctx.command} called!")

import logging
logging.basicConfig(level=logging.DEBUG)

# Run the bot
bot.run("іДі")
