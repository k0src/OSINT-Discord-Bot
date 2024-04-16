import discord
from discord.ext import commands
import requests
import io

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

async def make_api_call(query, channel):
    url = f"https://api.proxynova.com/comb?query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        count = data['count']
        lines = "\n".join(data['lines'])

        embed = discord.Embed(title="Results:", description=f"Count: {count}", color=discord.Color.pink())
        embed.url = url
        embed.add_field(name="Lines", value=lines, inline=False)

        message = await channel.send(embed=embed)
    
        await message.add_reaction("📥")
    else:
        await channel.send("An error occurred while fetching data")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def scan(ctx, *, query):
    await make_api_call(query, ctx.channel)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user or str(reaction.emoji) != "📥":
        return

    if isinstance(reaction.message.channel, discord.DMChannel):
        return

    if reaction.message.author != bot.user:
        return
    
    api_response = requests.get(reaction.message.embeds[0].url)
    
    await reaction.message.channel.send(
        content="JSON Data:",
        file=discord.File(io.BytesIO(api_response.content), filename="data.json")
    )

bot.run("TOKEN")