import discord
import asyncio
from timer import Timer
import json

client = discord.Client()
vc = None
timeout = 180
with open("commands.json", "r") as rf:
    file = json.load(rf)
normal = file["normal"]
admin = file["admin"]


async def mute(members, mute_state):
    for member in members:
        await member.edit(mute=mute_state)


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
    vc = await voice.disconnect(force=True)


async def disconnect_channel(message):
    global vc
    global inactivity_timer
    channel = message.author.voice.channel
    if not vc or not vc.is_connected():
    #if len(client.voice_clients) == 0:
        return await message.channel.send('Bot não conectado à nenhum canal.')
    if channel != vc.channel:
        return await message.channel.send(f"{message.author.mention}, para usar este comando você e o Bot precisam estar conectados ao mesmo canal.")
    if inactivity_timer.is_alive:
        inactivity_timer.cancel()
    vc = await client.voice_clients[0].disconnect(force=True)


@client.event
async def on_ready():
    print(f"logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!pare') and is_admin(message.author):
        await disconnect_channel(message)
    try:
        if message.content.startswith('!mute') and is_admin(message.author):
            await mute(message.author.voice.channel.members, True)

        if message.content.startswith('!unmute') and is_admin(message.author):
            await mute(message.author.voice.channel.members, False)

        for cmd, clip in admin.items():
            if message.content.startswith(cmd) and is_admin(message.author):
                await play_clip(channel=message.author.voice.channel, clip=clip)
                break

        for cmd, clip in normal.items():
            if message.content.startswith(cmd):
                await play_clip(channel=message.author.voice.channel, clip=clip)
                break

        if message.content.startswith('!comandos'):
            commands_msgs = '\n'.join(normal.keys())
            await message.channel.send(f"Lista de comandos:\n{commands_msgs}")

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
