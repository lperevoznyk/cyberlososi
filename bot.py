import discord
import os
from discord.ext import commands
import logging

from bot_config import config

TOKEN = config.get('bot', 'token')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.get('bot', 'prefix'), intents=intents)


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


@bot.check
async def globally_block_commands(ctx):
    permissions_cog = bot.get_cog('Permissions')
    if permissions_cog:
        return permissions_cog.has_permission(ctx)
    return ctx.author.guild_permissions.administrator


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        logging.warning(f"Permission denied: User {ctx.author} attempted '{ctx.command}' command.")
        return
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


logging.basicConfig(level=logging.INFO)
bot.run(TOKEN)
