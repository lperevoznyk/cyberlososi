import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class TvTVoices(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.users_original_channels = {}
        self.temp_channels = {}  # Store channel_id: last_empty_timestamp
        self.master_channel_id = 1351180895268376653  # Replace with your master channel ID
        self.delete_task.start()

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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # User joins the master channel
        if after.channel and after.channel.id == self.master_channel_id:
            category = after.channel.category
            temp_channel = await category.create_voice_channel(
                name=f"temp-{member.name}",
                reason="Temporary channel created automatically."
            )

            await member.move_to(temp_channel)

            # Copy permissions from category
            for target, overwrite in category.overwrites.items():
                if target != category.guild.default_role:
                    await temp_channel.set_permissions(target, overwrite=overwrite)

            # Allow the creator to manage the channel
            await temp_channel.set_permissions(member, manage_channels=True)

            # Initially mark as active, no empty timestamp needed yet
            self.temp_channels[temp_channel.id] = None

        # Check if user left a temporary channel, or rejoined
        affected_channels = set(filter(None, [before.channel, after.channel]))

        for channel in affected_channels:
            if channel.id in self.temp_channels:
                if len(channel.members) == 0:
                    # Channel just became empty: start timer
                    self.temp_channels[channel.id] = datetime.utcnow()
                else:
                    # Channel now has members again: reset timer
                    self.temp_channels[channel.id] = None

    @tasks.loop(minutes=30)
    async def delete_task(self):
        current_time = datetime.utcnow()
        to_delete = []

        for channel_id, empty_since in self.temp_channels.items():
            channel = self.bot.get_channel(channel_id)
            if channel:
                if empty_since and (current_time - empty_since) > timedelta(hours=2):
                    to_delete.append(channel_id)

        for channel_id in to_delete:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.delete(reason="Temporary channel empty for 2 hours.")
                print(f"Deleted empty temporary channel {channel.name} after 2 hours.")
            del self.temp_channels[channel_id]

    @delete_task.before_loop
    async def before_delete_task(self):
        await self.bot.wait_until_ready()

    @commands.command(name="delete_voices", help="Immediately deletes all empty temporary voice channels.")
    async def delete_voices(self, ctx: commands.Context):
        to_delete = []
        for channel_id, empty_since in self.temp_channels.items():
            channel = self.bot.get_channel(channel_id)
            if channel and len(channel.members) == 0:
                to_delete.append(channel_id)

        for channel_id in to_delete:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.delete(reason="Manually deleted empty temporary channel.")
                await ctx.send(f"Deleted empty temporary channel {channel.name}.")
            del self.temp_channels[channel_id]


def setup(bot: commands.Bot):
    bot.add_cog(TvTVoices(bot))
