import asyncio
import discord
from discord.ext import commands


class TextCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.users_original_channels = {}
        self.temp_channels = {}

    @commands.command(name="move_users",
                      help="Move all users from all voice channels in a specific category to one target channel.")
    async def move_users(self, ctx: commands.Context, target_channel: discord.VoiceChannel):
        # Ensure the target channel is in a category
        category = target_channel.category
        if category is None:
            await ctx.send("Target channel must be in a category.")
            return

        # Save original channel positions for users
        for channel in category.voice_channels:
            if channel != target_channel:  # Exclude the target channel
                for member in channel.members:
                    self.users_original_channels[member.id] = channel
                    await member.move_to(target_channel)

        await ctx.send(f"Moved all users from the voice channels in {category.name} to {target_channel.name}.")

    @commands.command(name="move_back", help="Move users back to their original voice channels.")
    async def move_back(self, ctx: commands.Context):
        # Move users back to their original channels
        for user_id, original_channel in self.users_original_channels.items():
            user = ctx.guild.get_member(user_id)
            if user and user.voice:
                await user.move_to(original_channel)

        # Clear the saved data after moving back
        self.users_original_channels.clear()
        await ctx.send("Moved users back to their original channels.")

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
