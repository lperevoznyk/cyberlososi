import asyncio
import discord
from discord.ext import commands


class TextCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="progriv", help="This is a prefix command.")
    async def foo(self, ctx: commands.Context):
        required_role = "SUPER ADMIN"  # Replace with the name of the role you want to check

        # Get the roles of the member who sent the command
        member_roles = [role.name for role in ctx.author.roles]

        # If the user has the required role, proceed
        if required_role in member_roles:
            await ctx.send("Анло купи баратрауму")
        else:
            warning_message = await ctx.send(
                f"{ctx.author.mention}, You do not have the required role to use this command.")

            # Delete the message after 5 seconds (adjust the time as needed)
            await asyncio.sleep(5)
            await warning_message.delete()

# The setup function is required so the bot knows how to load this cog
def setup(bot: commands.Bot):
    bot.add_cog(TextCommands(bot))
