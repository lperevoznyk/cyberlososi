import discord
from discord.ext import commands


class VoiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_channels = set()
        self.master_channel_id = 1351180894748147742  # Replace with your master channel ID

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # User joins the master channel
        if after.channel and after.channel.id == self.master_channel_id:
            category = after.channel.category
            temp_channel = await category.create_voice_channel(
                name=f"{member.display_name} channel",
                reason="Temporary channel created automatically."
            )

            await member.move_to(temp_channel)

            # Copy permissions from category
            for target, overwrite in category.overwrites.items():
                if target != category.guild.default_role:
                    await temp_channel.set_permissions(target, overwrite=overwrite)

            # Allow creator to manage the channel
            await temp_channel.set_permissions(member, manage_channels=True)

            # Store temporary channel
            self.temp_channels.add(temp_channel.id)

        # Check if user left a temporary channel
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                await before.channel.delete(reason="Temporary channel became empty.")
                self.temp_channels.remove(before.channel.id)


def setup(bot: commands.Bot):
    bot.add_cog(VoiceCommands(bot))
