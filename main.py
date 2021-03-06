import discord
import asyncio
from timer import Timer
import json

client = discord.Client()
vc = None
timeout = 60

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
    while vc and vc.is_playing():
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
    if message.content.startswith('!pare'):
        await disconnect_channel(message)
    try:
        if is_admin(message.author):
            if message.content.startswith('!mute'):
                await mute(message.author.voice.channel.members, True)

            if message.content.startswith('!unmute'):
                await mute(message.author.voice.channel.members, False)

            for cmd, clip in admin.items():
                if message.content.startswith(cmd):
                    await play_clip(channel=message.author.voice.channel, clip=clip)
                    break

        for cmd, clip in normal.items():
            if message.content.startswith(cmd):
                await play_clip(channel=message.author.voice.channel, clip=clip)
                break

        if message.content.startswith('!comandos'):
            audio_commands = '\n'.join(normal.keys())
            await message.channel.send(f"Lista de comandos:\n{audio_commands}")

    except AttributeError as e:
        await message.channel.send(f"{message.author.mention}, você não está em um Canal de Voz.")
        print(e)
    except discord.errors.ClientException as e:
        # playing audio twice
        print(e)

    if message.content.startswith('!git'):
        await message.channel.send("Meu código: https://github.com/VicenteMoraes/sarrandobot")


@client.event
async def on_voice_state_update(member, before, after):
    if member.nick == "pombo" and before.channel != after.channel != None:
        await play_clip(after.channel, clip="audio/pombo.mp3")
    elif member.name == "BadBad" and before.channel != after.channel != None:
        await play_clip(after.channel, clip="audio/tiltado.mp3")
    elif member.name == "lucas0one" and before.channel != after.channel != None:
        await play_clip(after.channel, clip="audio/superlucao.mp3")

@client.event
async def on_member_join(member):
   pass


if __name__ == "__main__":
    with open("token", "r") as rf:
        token = rf.readline()
    inactivity_timer = Timer(timeout, vc_disconnect)
    client.run(token)
