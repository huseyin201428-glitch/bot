import discord
from discord.ext import commands
from discord import app_commands

# =============================================
# CONFIG - Fill these in before running
# =============================================
import os
TOKEN = os.getenv('TOKEN')

# The exact role names to check for (case-sensitive - match your server's role names)
TRACKED_ROLES = [
    'Founder',
    'OWNER',
    'CO OWNER',
    'HEAD ADMIN',
    'admin',
    'moderator',
    'trial moderator',
]

# =============================================
# Bot Setup
# =============================================
intents = discord.Intents.default()
intents.members = True  # Requires "Server Members" privileged intent in Dev Portal

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')


# =============================================
# /check Command
# =============================================
@bot.tree.command(name='check', description='Lists all server members and their staff roles')
async def check(interaction: discord.Interaction):
    # Defer immediately — prevents the 3 second timeout error
    await interaction.response.defer(thinking=True)

    guild = interaction.guild
    if not guild:
        await interaction.followup.send('❌ This command can only be used in a server.')
        return

    # Fetch all members properly using async iterator
    members = [m async for m in guild.fetch_members(limit=None)]

    lines = []

    for member in members:
        if member.bot:
            continue  # Skip bots

        # Find which tracked roles this member has
        member_role_names = [role.name for role in member.roles]
        matched_roles = [r for r in TRACKED_ROLES if r in member_role_names]

        if matched_roles:
            lines.append(f'**{member.name}** — {", ".join(matched_roles)}')

    if not lines:
        await interaction.followup.send('No members found with any of the tracked staff roles.')
        return

    # Split into pages of 30 entries each (Discord embed limit: 4096 chars)
    chunk_size = 30
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]

    for i, chunk in enumerate(chunks):
        embed = discord.Embed(
            title='📋 Staff Role Check' if i == 0 else '📋 Staff Role Check (cont.)',
            description='\n'.join(chunk),
            color=0x5865F2
        )
        embed.set_footer(text=f'{len(lines)} staff member(s) found • Page {i + 1}/{len(chunks)}')
        embed.timestamp = discord.utils.utcnow()

        if i == 0:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.channel.send(embed=embed)


# =============================================
# Run the bot
# =============================================
bot.run('MTQ5MDUyMjY0NjQwMjgzMDM3Nw.GHSlIM.-yQFjXVcuN4ha0lWjoO-a1J8PmSo118kg5z31Q')
