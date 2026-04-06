import discord
from discord.ext import commands
from discord import app_commands
import os
import logging

# Logging so Render shows useful output
logging.basicConfig(level=logging.INFO)

# =============================================
# TOKEN - reads from environment variable
# =============================================
TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError("No TOKEN environment variable set! Add it in Render > Environment.")

# =============================================
# Role names - must match your server exactly
# =============================================
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
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')
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
    await interaction.response.defer(thinking=True)

    guild = interaction.guild
    if not guild:
        await interaction.followup.send('❌ This command can only be used in a server.')
        return

    try:
        members = [m async for m in guild.fetch_members(limit=None)]
    except Exception as e:
        await interaction.followup.send(f'❌ Failed to fetch members: {e}')
        return

    lines = []
    for member in members:
        if member.bot:
            continue
        member_role_names = [role.name for role in member.roles]
        matched_roles = [r for r in TRACKED_ROLES if r in member_role_names]
        if matched_roles:
            lines.append(f'**{member.name}** — {", ".join(matched_roles)}')

    if not lines:
        await interaction.followup.send('No members found with any of the tracked staff roles.')
        return

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
# Run
# =============================================
bot.run('MTQ5MDUyMjY0NjQwMjgzMDM3Nw.GZuQnM.GWOEBOSW5gg4j2CFZEhVTUeXBJqSgdv-oW23Mk')
