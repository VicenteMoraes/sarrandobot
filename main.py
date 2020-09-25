import discord
import asyncio
from timer import Timer

client = discord.Client()
vc = None
timeout = 300


async def mute(members, mute):
    for member in members:
        await member.edit(mute=mute)


def is_admin(member):
    return member.guild_permissions.administrator


async def play_clip(channel, clip):
    global vc
    global inactivity_timer
    if not vc or channel != vc.channel:
        vc = await channel.connect()
    elif inactivity_timer.is_alive:
        inactivity_timer.cancel()
    vc.play(discord.FFmpegPCMAudio(clip), after=lambda e: print('done', e))
    await asyncio.sleep(1)
    while vc.is_playing():
        await asyncio.sleep(1)
    inactivity_timer.start(vc)


async def vc_disconnect(voice):
    global vc
    await voice.disconnect(force=True)


async def disconnect_channel(message):
    channel = message.author.voice.channel
    if len(client.voice_clients) == 0:
        return await message.channel.send('Bot não conectado à nenhum canal.')
    if not client.voice_clients[0].channel == channel:
        return await message.channel.send(f"{message.author.mention}, para usar este comando você e o Bot precisam estar conectados ao mesmo canal.")
    await client.voice_clients[0].disconnect(force=True)


@client.event
async def on_ready():
    print(f"logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!stop') and is_admin(message.author):
        await disconnect_channel(message.author.voice.channel)
    try:
        if message.content.startswith('!mute') and is_admin(message.author):
            await mute(message.author.voice.channel.members, True)

        if message.content.startswith('!unmute') and is_admin(message.author):
            await mute(message.author.voice.channel.members, False)

        if message.content.startswith('!galaxiana'):
            await play_clip(channel=message.author.voice.channel, clip='audio/jotavic.mp3')
        if message.content.startswith('!vergonha'):
            await play_clip(channel=message.author.voice.channel, clip='audio/vergonha.mp3')
        if message.content.startswith('!hehe'):
            await play_clip(channel=message.author.voice.channel, clip='audio/risada2.mp3')
        if message.content.startswith('!ihu'):
            await play_clip(channel=message.author.voice.channel, clip='audio/ihu.mp3')
        if message.content.startswith('!chama'):
            await play_clip(channel=message.author.voice.channel, clip='audio/chama.mp3')
        if message.content.startswith('!discord'):
            await play_clip(channel=message.author.voice.channel, clip='audio/discord.mp3')
        if message.content.startswith('!tazmania'):
            await play_clip(channel=message.author.voice.channel, clip='audio/tazmania.mp3')
        if message.content.startswith('!mod') and is_admin(message.author):
            await play_clip(channel=message.author.voice.channel, clip='audio/mod.mp3')
        if message.content.startswith('!tira') and is_admin(message.author):
            await play_clip(channel=message.author.voice.channel, clip='audio/joao.mp3')
        if message.content.startswith('!pombo'):
            await play_clip(channel=message.author.voice.channel, clip='audio/pombo.mp3')
        if message.content.startswith('!comandos'):
            await message.channel.send("Lista de comandos:\n!chama\n!discord\n!galaxiana\n!hehe\n!ihu\n!mod (apenas admin)\n!mute (apenas admin)\n!pombo\n!stop (apenas admin)\n!tazmania\n!unmute (apenas admin)\n!vergonha\n")
    except AttributeError:
        await message.channel.send(f"{message.author.mention}, você não está em um Canal de Voz.")
    except discord.errors.ClientException:
        # playing audio twice
        pass

    if message.content.startswith('!git'):
        await message.channel.send("Meu código: https://github.com/VicenteMoraes/sarrandobot")


@client.event
async def on_member_join(member):
   pass


if __name__ == "__main__":
    with open("token", "r") as rf:
        token = rf.readline()
    inactivity_timer = Timer(timeout, vc_disconnect)
    client.run(token)
