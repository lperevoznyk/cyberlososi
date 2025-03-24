import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class VoiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.users_original_channels = {}
        self.temp_channels = {}  # Store temporary channels with their creation time
        self.master_channel_id = 1351180895268376653  # Replace with your master channel ID
        self.delete_task.start()  # Start the background task to delete empty channels after 2 hours

    # Event when a user joins a voice channel
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if after.channel and after.channel.id == self.master_channel_id:
            category = after.channel.category
            temp_channel = await category.create_voice_channel(
                name=f"temp-{member.name}",
                reason="Temporary channel created automatically."
            )

            await member.move_to(temp_channel)

            # Copy permissions correctly
            for target, overwrite in category.overwrites.items():
                if target != category.guild.default_role:  # Skip @everyone
                    await temp_channel.set_permissions(target, overwrite=overwrite)

            # Allow the user to manage the channel explicitly
            await temp_channel.set_permissions(member, manage_channels=True)

            # Store temporary channel creation timestamp
            self.temp_channels[temp_channel.id] = datetime.utcnow()

    @commands.command(name="delete_voices", help="Delete all empty temporary voice channels.")
    async def delete_voices(self, ctx: commands.Context):
        # Check all temp channels and delete empty ones
        for channel_id, creation_time in list(self.temp_channels.items()):
            channel = self.bot.get_channel(channel_id)
            if channel and len(channel.members) == 0:
                # Delete the channel if it's empty
                await channel.delete()
                del self.temp_channels[channel_id]
                await ctx.send(f"Deleted empty temporary channel {channel.name}.")

    @tasks.loop(minutes=30)
    async def delete_task(self):
        """ This task checks for empty temp channels every 30 minutes and deletes them if they're older than 2 hours """
        current_time = datetime.utcnow()
        for channel_id, creation_time in list(self.temp_channels.items()):
            if (current_time - creation_time) > timedelta(hours=2):
                channel = self.bot.get_channel(channel_id)
                if channel and len(channel.members) == 0:
                    # Delete the empty channel after 2 hours
                    await channel.delete()
                    del self.temp_channels[channel_id]
                    print(f"Deleted empty temporary channel {channel.name} after 2 hours.")

    @delete_task.before_loop
    async def before_delete_task(self):
        """ Wait until the bot is ready before starting the delete task """
        await self.bot.wait_until_ready()


# Setup function to add the cog to the bot
def setup(bot: commands.Bot):
    bot.add_cog(VoiceCommands(bot))
