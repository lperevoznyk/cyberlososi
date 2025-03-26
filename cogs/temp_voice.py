import discord
from discord.ext import commands


class VoiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_channels = set()
        self.master_channels = set()  # store multiple master channel IDs

    # Command to add master channels dynamically
    @commands.command(name="add_master_channel",
                      usage="<channel>",
                      help="Add a master channel by mentioning it.")
    async def add_master_channel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        self.master_channels.add(channel.id)
        await ctx.send(f"✅ Added {channel.mention} as a master channel.")

    # Command to remove master channels dynamically
    @commands.command(name="remove_master_channel",
                      usage="<channel>",
                      help="Remove a master channel by mentioning it.")
    async def remove_master_channel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if channel.id in self.master_channels:
            self.master_channels.remove(channel.id)
            await ctx.send(f"❌ Removed {channel.mention} from master channels.")
        else:
            await ctx.send(f"⚠️ {channel.mention} is not in master channels list.")

    # Command to list all current master channels
    @commands.command(name="list_master_channels", help="List all current master channels.")
    async def list_master_channels(self, ctx: commands.Context):
        if not self.master_channels:
            await ctx.send("No master channels set yet.")
            return

        channels = [self.bot.get_channel(cid).mention for cid in self.master_channels if self.bot.get_channel(cid)]
        channel_list = ', '.join(channels)
        await ctx.send(f"📌 **Master channels:** {channel_list}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # User joins any of the master channels
        if after.channel and after.channel.id in self.master_channels:
            category = after.channel.category
            temp_channel = await category.create_voice_channel(
                name=f"{member.display_name}'s Channel",
                reason="Temporary channel created automatically."
            )

            await member.move_to(temp_channel)

            # Copy permissions from category
            for target, overwrite in category.overwrites.items():
                if target != category.guild.default_role:
                    await temp_channel.set_permissions(target, overwrite=overwrite)

            # Allow creator to manage channel
            await temp_channel.set_permissions(member, manage_channels=True)

            # Store temporary channel ID
            self.temp_channels.add(temp_channel.id)

        # Check if user left a temporary channel
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                await before.channel.delete(reason="Temporary channel became empty.")
                self.temp_channels.remove(before.channel.id)


def setup(bot: commands.Bot):
    bot.add_cog(VoiceCommands(bot))
