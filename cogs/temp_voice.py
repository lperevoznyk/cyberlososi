import discord
from discord.ext import commands
import sqlite3

from bot_config import config


class VoiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_channels = set()
        self.master_channels = set()

        # Connect to or create the SQLite database.
        # You can rename "permissions.db" to something else if you prefer.
        self.conn = sqlite3.connect(config.get('database', 'filename'))
        self.cursor = self.conn.cursor()

        # Create a table (if not exists) to store master channel IDs.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_master_channels (
                channel_id INTEGER PRIMARY KEY
            )
        """)
        self.conn.commit()

        # Load any stored master channel IDs from the database into self.master_channels.
        self.load_master_channels()

    def load_master_channels(self):
        """Load all channel_id rows from the DB into self.master_channels."""
        self.cursor.execute("SELECT channel_id FROM voice_master_channels")
        rows = self.cursor.fetchall()
        for (channel_id,) in rows:
            self.master_channels.add(channel_id)

    def save_master_channel(self, channel_id: int):
        """Insert a new master channel row if it doesn’t already exist."""
        self.cursor.execute(
            "INSERT OR IGNORE INTO voice_master_channels (channel_id) VALUES (?)",
            (channel_id,)
        )
        self.conn.commit()

    def remove_master_channel_db(self, channel_id: int):
        """Remove a master channel row."""
        self.cursor.execute(
            "DELETE FROM voice_master_channels WHERE channel_id = ?",
            (channel_id,)
        )
        self.conn.commit()

    @commands.command(name="add_master_channel",
                      usage="<channel>",
                      help="Add a master channel by mentioning it.")
    async def add_master_channel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if channel.id not in self.master_channels:
            self.master_channels.add(channel.id)
            self.save_master_channel(channel.id)
            await ctx.send(f"✅ Added {channel.mention} as a master channel.")
        else:
            await ctx.send(f"{channel.mention} is already in the master channels set.")

    @commands.command(name="remove_master_channel",
                      usage="<channel>",
                      help="Remove a master channel by mentioning it.")
    async def remove_master_channel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if channel.id in self.master_channels:
            self.master_channels.remove(channel.id)
            self.remove_master_channel_db(channel.id)
            await ctx.send(f"❌ Removed {channel.mention} from master channels.")
        else:
            await ctx.send(f"⚠️ {channel.mention} is not in the master channels list.")

    @commands.command(name="list_master_channels", help="List all current master channels.")
    async def list_master_channels(self, ctx: commands.Context):
        if not self.master_channels:
            await ctx.send("No master channels set yet.")
            return

        channels = [self.bot.get_channel(cid).mention
                    for cid in self.master_channels
                    if self.bot.get_channel(cid)]
        channel_list = ', '.join(channels)
        await ctx.send(f"📌 **Master channels:** {channel_list}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if after.channel and after.channel.id in self.master_channels:
            category = after.channel.category
            temp_channel = await category.create_voice_channel(
                name=f"{member.display_name}'s Channel",
                reason="Temporary channel created automatically."
            )
            await member.move_to(temp_channel)

            for target, overwrite in category.overwrites.items():
                if target != category.guild.default_role:
                    await temp_channel.set_permissions(target, overwrite=overwrite)

            await temp_channel.set_permissions(member, manage_channels=True)
            self.temp_channels.add(temp_channel.id)

        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                await before.channel.delete(reason="Temporary channel became empty.")
                self.temp_channels.remove(before.channel.id)

    def cog_unload(self):
        """Close the database connection when the cog is unloaded or bot shuts down."""
        self.conn.close()


def setup(bot: commands.Bot):
    bot.add_cog(VoiceCommands(bot))
