from asyncio.tasks import sleep
# from math import ulp
# from typing import Tuple
import discord
from discord.abc import User
from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ext import tasks
from discord_components import DiscordComponents, Button, ButtonStyle, component, interaction
import youtube_dl
from pytube import YouTube, Playlist
import os
import pathlib
from youtube_search import YoutubeSearch
import validators
import time
import asyncio
import datetime
import lyricsgenius as lg
from pyfiglet import figlet_format
import shutil
import random
from pymediainfo import MediaInfo

from dotenv import load_dotenv

# from mutagen.mp4 import M4A

os.system('cls' if os.name == 'nt' else 'clear')

print('Bot iniciado...')
print('-------------------------------------------')
print("BOT OLIMPO MUSIC\n\n")
print(figlet_format('OwO'))
print('Por:')
print('SAMUELSON PAJEU XD')
print('-------------------------------------------')
activity = discord.Game(name="!play")
client = commands.Bot(command_prefix='!', activity=activity, help_command=None)
ddb = DiscordComponents(client)
# buttons = ButtonsClient(client)



local_path = pathlib.Path().resolve()

songs_folder = "{}/Songs".format(local_path)
apolo_folder = "{}/Apolo".format(local_path)
icon = "{}/icon.ico".format(local_path)
os.chdir(songs_folder)

load_dotenv()
class Users:
    admin = os.getenv('ADMIN_ID')
    blocked = []

genius = lg.Genius(os.getenv('GENIUS_SECRET'), skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)
genius_blacklist = [
    "(", ")", "[", "]", "<", ">",
    "Remix",
    "Live",
    "Official",
    "Video",
    "Clipe",
    "Oficial",
    "Lyrics",
    "Cover",
    "Animated",
    "Music",
    "Cover"
]

can_leave = True

queue = []
queue_length = []
loop = []
in_pause = []
checkQ = []

react_msg = []
ctx_l = []


@client.command()
async def help(ctx):
    comandos = [
        "`➤ !p ou !play`",
        "`➤ !pause`",
        "`➤ !resume`",
        "`➤ !fs`",
        "`➤ !clear`",
        "`➤ !l`",
        "`➤ !leave ou !stop`",
        "`➤ !q`",
        "`➤ !clear`",
    ]
    descricao = [
        "`Tocar uma música`",
        "`Pausa a música`",
        "`Continua a reproduzir a música`",
        "`Pula a música atual`",
        "`Limpa a fila atual`",
        "`Exibe a letra da música atual`",
        "`Para a música e disconecta o bot`",
        "`Mostra a fila atual`",
        "`Limpa a fila atual`"
    ]
    comandos_texto = "\n".join(comandos)
    descricao_texto = "\n".join(descricao)
    
    embed = discord.Embed(
        color=discord.Color.from_rgb(254, 231, 92)
    )
    embed.set_author(name="Comandos", icon_url='https://cdn.discordapp.com/avatars/892020683473821766/f7fc68080e3550140eb5a35893b47c65.png?size=256')
    embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/892020683473821766/f7fc68080e3550140eb5a35893b47c65.png?size=256')
    embed.add_field(name="Comando", value=comandos_texto, inline=True)
    embed.add_field(name="Descrição", value=descricao_texto, inline=True)      
    await ctx.send(embed=embed)
    
@client.command()
async def l(ctx, *arg):
    
    if len(queue) > 0 or arg:
        
        if not arg:
            search_term = queue[0].replace(".mp4","")
        else:
            search_term = ' '.join(arg)

        for i in genius_blacklist:
            search_term = search_term.upper()
            search_term = search_term.replace(i.upper(),"")

        song_lyric = genius.search_song(search_term)
        genius
        try:
            if (song_lyric):
                # await ctx.send("> **Lyrics** \n{0}".format(search_term))
                embed = discord.Embed(
                    title="{}".format(search_term),
                    color=discord.Color.from_rgb(254, 231, 92)
                )
                embed.set_author(name="Pesquisa: ")

                lyric = song_lyric.lyrics.split('\n\n')
                for i in lyric:
                    embed.add_field(name="** **", value=f'> {i}', inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("> Letra não encontrada 😔")
        except Exception as e:
            print (e)
            await ctx.send("> Algo deu errado 😓")
    elif len(queue) == 0 and not arg:
        await ctx.send("> Nenhuma música tocando atualmente")

@client.command()
async def bt(ctx,):
    if len(queue) > 0:
        music = queue[0].replace(".mp4","")
    else:
        await ctx.send("> Nenhuma música tocando atualmente")
        return

    embed = discord.Embed(
        title=music,
    )
    embed.set_author(name="Music player")
    # embed.add_field(name="Titulo 1", value="** **", inline=True)
    # embed.add_field(name="Titulo 2", value="** **", inline=True)
    # embed.add_field(name="** **", value="Texto 1", inline=True)
    # embed.add_field(name="** **", value="Texto 2", inline=False)
    # embed.add_field(name="** **", value="Texto 3", inline=False)
    await ctx.send(
        embed=embed,

        components=[
                [
                Button(style=ButtonStyle.gray, emoji="⏹", custom_id='4'),
                Button(style=ButtonStyle.gray, emoji="⏸️", custom_id='1'),
                Button(style=ButtonStyle.gray, emoji="▶️", custom_id='3'),
                Button(style=ButtonStyle.gray, emoji="⏭️", custom_id='2'),
                ]
            ],
        )
    res = await client.wait_for("button_click")
    if res.channel == ctx.channel:
        if res.channel == ctx.channel:
            # print(res.component)
            if res.component.custom_id == '1':
                await pause(ctx)
                await res.respond(
                    content='Pause'
                )
            elif res.component.custom_id == '2':
                await fs(ctx)
                await res.respond(
                    content='Next'
                )
            elif res.component.custom_id == '3':
                await resume(ctx)
                await res.respond(
                    content='Resume'
                )
            elif res.component.custom_id == '4':
                await stop(ctx)
                await res.respond(
                    content='Stop'
                )

async def CheckReaction():
    while True:
        # print("Aqui")
        await asyncio.sleep(1)
        if len(react_msg) > 0:
            # print("na condicao")
            
            await react_msg[0].send(embed=react_msg[1],components=[react_msg[2]])
            
            res = await client.wait_for("button_click")
            if res.channel == react_msg[0].channel:
                if res.channel == react_msg[0].channel:

                    if res.component.custom_id == '1':
                        await pause(react_msg[0])
                        await res.respond(
                            content='Pause'
                        )
                    elif res.component.custom_id == '2':
                        await fs(react_msg[0])
                        await res.respond(
                            content='Next'
                        )
                    elif res.component.custom_id == '3':
                        await resume(react_msg[0])
                        await res.respond(
                            content='Resume'
                        )
                    elif res.component.custom_id == '4':
                        await stop(react_msg[0])
                        await res.respond(
                            content='Stop'
                        )
                    react_msg.clear()

@client.command()
async def ping(ctx):
    await ctx.send("> Pong!")


def ReturnYoutubeURL(url):
    if not validators.url(url):
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            sulfix = results[0]['url_suffix']
            final_url = 'https://www.youtube.com{}'.format(sulfix)
            return final_url, False
        except Exception as e:
            print(e)
    else:
        if 'youtu' in url:
            if 'playlist' in url or 'list' in url:
                return url, True
            else:
                return url, False
        else:
            return

def GetDuration(file):
    media_info = MediaInfo.parse(f"{file}")
    for track in media_info.tracks:
        return int(track.to_data()["duration"]/1000.0)

@client.command()
async def block(ctx, *arg):
    if len(arg) > 0:
        
        if arg[0] == Users.admin:
            await ctx.send("> Boa tentativa")
        else:
            try:
                if int(arg[0]) not in Users.blocked:
                    integer = int(arg[0])
                    Users.blocked.append(integer)
                    await ctx.send(f"> Usuário <@{integer}> bloqueado pelo seu gosto ruim")
                else:
                    await ctx.send("> Usuário já bloqueado")
            except:
                await ctx.send("> Usuário não encontrado")

@client.command()
async def unblock(ctx, *arg):
    if ctx.message.author.id in Users.blocked:
        await ctx.send("> Você está bloqueado :P ")
        return
    if len(arg) > 0:
        try:
            if int(arg[0]) in Users.blocked:
                integer = int(arg[0])
                Users.blocked.remove(integer)
                await ctx.send(f"> Usuário <@{integer}> desbloqueado")
            else:
                await ctx.send("> Usuário não bloqueado")
        except:
            await ctx.send("> Usuário não encontrado")

@client.command()
async def p(ctx, *arg):
    if ctx.message.author.id in Users.blocked:
        await ctx.send("> Você está bloqueado :P ")
        return
    
    if len(ctx_l) == 0:
        ctx_l.append(ctx)
    else:
        ctx_l[0] = ctx

    
    url = ' '.join(arg)
    # TENTA CONECTAR
    print("Termo pesquisa utilizado: {}".format(url))
    bot_voice = ctx.guild.voice_client
    if not ctx.message.author.voice:
        await ctx.send("> {} não está conectado a um canal de voz, burro".format(ctx.message.author.name))
        return
    
    url = ReturnYoutubeURL(url)
    print (f"URL....... \n{url}")
    # print(url)
    # print("===================================================================")
    
    ydl_opts = {
        'verbose' : True,
        'cookiefile' : 'cookies.txt',
        'format': 'bestaudio',
        'source_address' : '0.0.0.0',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            # 'key': 'aria2c',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
        }],
    }
    if url[1] == False:        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url[0], download=False)
                video_title = info_dict.get('title', None)
                video_thumb = info_dict.get('thumbnails', None)
                video_thumb = video_thumb[0]['url']
                video_duration = info_dict.get('duration',None)
                conversion = datetime.timedelta(seconds=video_duration)
                conversion = str(conversion)
                queue_position = len(queue)
            except Exception as e:
                if 'valid URL' in str(e):
                    await ctx.send(">❗ URL inválida")
                elif 'age' in str(e):
                    await ctx.send(">❗ Vídeo possui restrição de idade")
                else:
                    await ctx.send("> Algo deu errado 😓")
            
            
            embed = discord.Embed(
                title="🎵 {}".format(video_title),
                url=url[0],
                description="Adicionado a fila",
                color=discord.Color.blue()
            )
            embed.set_author(name="@{}".format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=video_thumb)
            embed.add_field(name="< Info >", value="Duração: `{}` | Posição na fila: `{}`".format(conversion,queue_position))      
            
            print("VOU BAIXAR!...............")
            yt = YouTube(url[0])
            print(f"YT!.............{yt}")
            video = yt.streams.filter(only_audio=True).first()
            print(f"VIDEO!.............{video}")
            video.download(songs_folder)
            print("BAIXEI!...............")

            
    else:
        await ctx.send("> Sua Playlist é muito grande senpai! YAMETE! >///<")
        return
        # playlist = Playlist(url[0])
        # embed = discord.Embed(
        #         title="🎵 - Playlist",
        #         url=url[0],
        #         description="{} músicas adicionadas".format(len(playlist.video_urls)),
        #     )
        # embed.set_author(name="@{}".format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
        # await ctx.send(embed=embed)
        # try:
        #     i = 1
        #     for video in playlist.videos:
        #         video.streams.filter(only_audio=True).first().download()
        #         print("")
        # except:
        #     pass
        
    for file in os.listdir("./"):
        if file.endswith(".mp4"):
            if file not in queue:
                # renamed = file
                # renamed = renamed.replace("\\","-").replace("/","-").replace("|","-").replace(":","-").replace("*","-").replace("?","-").replace("<","-").replace(">","-").replace('"',"-")
                try:
                    # os.rename(file, renamed)
                    queue.append(file)
                    queue_length.append(GetDuration(file))
                    await ctx.send(embed=embed)
                except Exception as e:
                    print(e)
                    await ctx.send("> ❗ A música já está na playlist!")
                    os.remove(file)
                    continue

    if len(checkQ) == 0 and len(loop) == 0:
        checkQ.append(client.loop.create_task(CheckPlay(ctx)))

@client.command()
async def play(ctx, *arg):
    await p(ctx, *arg)

@client.command()
async def apolo(ctx):
    if not ctx.message.author.voice:
        await ctx.send("> {} não está conectado a um canal de voz, burro".format(ctx.message.author.name))
        return
    
    if len(ctx_l) == 0:
        ctx_l.append(ctx)
    else:
        ctx_l[0] = ctx
    apolo_q = []
    for file in os.listdir(apolo_folder):
        if file.endswith(".mp3"):
            if file not in queue:
                _data = [shutil.copy(f"{apolo_folder}\\{file}", songs_folder),GetDuration(f"{apolo_folder}/{file}")]
                apolo_q.append(_data)
    random.shuffle(apolo_q)
    
    for i in apolo_q:
        queue.append(i[0])
        queue_length.append(i[1])
        


    if len(checkQ) == 0 and len(loop) == 0:
        checkQ.append(client.loop.create_task(CheckPlay(ctx)))
    
def ClearQueue():
    queue.clear()
    queue_length.clear()
    if len(loop) > 0:
        loop[0].cancel()
        loop.clear()
    if len(checkQ) > 0:
        checkQ[0].cancel()
        checkQ.clear()
        
    for file in os.listdir("./"):
        if file.endswith(".mp4") or file.endswith(".mp3"):
            os.remove(file)

async def CheckPlay(ctx):
    while True:
        print("Check")
        if len(loop) == 0:
            if len(queue) > 0 and len(queue_length) > 0:
                bot_voice = ctx.guild.voice_client
                
                if not bot_voice:
                    # print(ctx)
                    
                    try:
                        channel = ctx.message.author.voice.channel
                        await channel.connect()
                    except Exception as e:
                        print(e)
                        return

                if ctx.message.author.voice and not bot_voice:                    
                    loop.append(client.loop.create_task(MusicPlay(ctx)))
                    checkQ[0].cancel()
        else:
            if not bot_voice:
                channel = ctx.message.author.voice.channel
                await channel.connect()


        await asyncio.sleep(3)

async def fp(ctx):
    if len(checkQ) > 0:
        checkQ[0].cancel() 
        checkQ.clear()
    checkQ.append(client.loop.create_task(CheckPlay(ctx)))
    
def printf(value):
    print(f"{value}", end="\r")
    
async def MusicPlay(ctx):
    print("Entrou no music Play")
    tem_musica = False
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    while len(queue) == 0:
        print("Esperando Fila carregar")
        await asyncio.sleep(1)
        
    while len(queue) > 0:
        # print("Entrou no While")
        tem_musica = True
        
        #Pega tempo para proxima musica
        print("Música atual... {}".format(queue[0]))
        print("Sleep Time... {}".format(queue_length[0]))
        time_stamp = datetime.timedelta(seconds=int(queue_length[0]))
        time_stamp = str(time_stamp)
        
        voice.play(discord.FFmpegPCMAudio(queue[0]))
        embed = discord.Embed(
            title="{}".format(queue[0].replace(".mp4","")),
        )
        embed.set_author(name="Reproduzindo: ")

        await ctx_l[0].send(embed=embed)
        
        while(queue_length[0] > 0):
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
            if not voice.is_connected():
                print("Desconectado")
                ClearQueue()
            
            ultima_att = datetime.datetime.now()
            await asyncio.sleep(1)
            difference_in_sec = datetime.datetime.now() - ultima_att
            difference_in_sec = difference_in_sec.total_seconds()
            queue_length[0] -= difference_in_sec
            printf("Tempo restante: {} | {}".format(time_stamp, datetime.timedelta(seconds=int(queue_length[0])) ))
            
            
        print("Next Song")
        voice.stop()
        time.sleep(1)
        for file in os.listdir("./"):
            if file.endswith(".mp4") or file.endswith(".mp3"):
                if queue[0] in file:
                    os.remove(file)
        queue.pop(0)
        queue_length.pop(0)
        
    if tem_musica:
        await voice.disconnect()
        await ctx_l[0].send("> A Playlist foi finalizada!")
        print("Fim da playlist")
        ClearQueue() 
        

async def inPause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    while voice.is_paused():
        queue_length[0] += 1
        # print(queue_length[0])
        await asyncio.sleep(1)
    
    in_pause[0].cancel()
    in_pause.clear()



@client.command()
async def fs(ctx):
    # if ctx.user.id == 664630445698187265:
    #     await ctx.send("> Bloqueado")
    #     return

    if can_leave == False:
        await ctx.send("> Bloqueado")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if len(queue) > 1:
        voice.stop()
        time.sleep(1)
        for file in os.listdir("./"):
            if file.endswith(".mp4") or file.endswith(".mp3"):
                if queue[0] in file:
                    os.remove(file)
        queue.pop(0)
        queue_length.pop(0)
        voice.play(discord.FFmpegPCMAudio(queue[0]))
        embed = discord.Embed(
            title="{}".format(queue[0].replace(".mp4","")),
        )
        embed.set_author(name="> Próxima música 👍")

        await ctx.send("> Próxima música 👍\n `{}`".format(queue[0].replace(".mp4","")))

def checkQueue():
    for file in os.listdir("./"):
        if file.endswith(".mp4") or file.endswith(".mp3"):
            queue.append(file)
    print (queue)


@client.command()
async def clear(ctx):
    if can_leave == False:
        await ctx.send("> Se fode ae")
        return
    ClearQueue()
    await ctx.send("> Queue foi limpa")
    
@client.command()
async def leave(ctx):
    if can_leave == False:
        await ctx.send("> 🤣😂😂🤣🤣")
        return
    if not ctx.message.author.voice:
        await ctx.send("> {} não está conectado a um canal de voz, burro".format(ctx.message.author.name))
        return
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        
    await ctx.send("> Tchaaaaau 👋")
    await voice.disconnect()
    time.sleep(2)
    if len(loop) > 0:
        loop[0].cancel()
        loop.clear()
    ClearQueue()
    
    


@client.command()
async def pause(ctx):
    if can_leave == False:
        await ctx.send("> Não!")
        return
    if not ctx.message.author.voice:
        await ctx.send("> {} não está conectado a um canal de voz, burro".format(ctx.message.author.name))
        return
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        await ctx.send("> ⏸ Pausou musica")
        voice.pause()
        if len(in_pause) == 0:
            in_pause.append(client.loop.create_task(inPause(ctx)))
    else:
        await ctx.send("> Não tem nenhuma música tocando.")


@client.command()
async def resume(ctx):
    if not ctx.message.author.voice:
        await ctx.send("> {} não está conectado a um canal de voz, burro".format(ctx.message.author.name))
        return
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        await ctx.send("> ▶️ E a musica volta a rolar \O/")
        voice.resume()
        in_pause[0].cancel()
        in_pause.clear()
        
    else:
        await ctx.send("> A música não está pausada")


@client.command()
async def stop(ctx):
    await leave(ctx)
    # if not ctx.message.author.voice:
    #     await ctx.send("> {} não está conectado a um canal de voz, burro".format(ctx.message.author.name))
    #     return
    
    # voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    # voice.stop()
    # time.sleep(1)
    # ClearQueue()
    # if len(loop) > 0:
    #     loop[0].cancel()
    #     loop.clear()

@client.command()
async def q(ctx):
    if len(queue) > 0:
        paginas = 0
        tamanho_queue = len(queue)
        i =  0
        
        while(tamanho_queue > 0):
            paginas += 1
            tamanho_queue -= 5
        
        while(paginas > 0):
            embed = discord.Embed(
                title="Playlist",
                color=discord.Color.blue(),
                description='Página {}'.format(i+1),
            )
            atual_pos = []
            music_name = []
            for x in range(5):
                    j = i * 5
                    if x+j < len(queue):
                        # print(f"j.... {j}")
                        # print("x+j.... {}".format(x+j))

                        atual_pos.append("Reproduzindo" if x+j == 0 else "{}".format(x+j))
                        music_name.append("➤ {}".format(queue[x+j].replace(".mp4","")))
                
            pos_text = "\n".join(atual_pos)
            music_text = "\n".join(music_name)
            
            embed.add_field(name="Posição", value="`{}`".format(pos_text),inline=True)
            embed.add_field(name="Música", value="{}".format(music_text),inline=True)
            await ctx.send(embed=embed)
            
            paginas -= 1
            i += 1

    
    if len(queue) == 0:
        embed = discord.Embed(
                title="Playlist",
                color=discord.Color.blue()
            )
        embed.add_field(name="> Parece que não tem nenhuma música na Playlist", value="\n Use o comando `!p` para adicionar uma")
        await ctx.send(embed=embed)
    

ClearQueue()
# client.loop.create_task(CheckReaction())
client.run(os.getenv('DISCORD_APP_ID'))

