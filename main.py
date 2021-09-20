import discord
from discord.ext import commands
import youtube_dl
import os
import random
import json
import requests
import logging

client = commands.Bot(command_prefix = "!")

to_do = ["School", "Homework", "Sleep"]

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing",
             "naku", "cry"]

starter_encouragements = [
   "Cheer up!",
   "You got this!",
   "Keep it up!",
   "You're doing great right now :relaxed:"
   ]

@client.event
async def on_ready():
   print("We have logged in as {0.user}".format(client))


@client.listen()
async def on_message(message):
   if message.author == client.user:
      return

   msg = message.content

   if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(starter_encouragements))

#Server info
@client.command()
async def server(ctx):
   name = str(ctx.guild.name)
   description = str(ctx.guild.description)
   
   owner = str(ctx.guild.owner)
   id = str(ctx.guild.id)
   region = str(ctx.guild.region)
   memberCount = str(ctx.guild.member_count)

   icon = str(ctx.guild.icon_url)

   embed = discord.Embed(
      title = name + " Server Information",
      description = description,
      color = discord.Color.blue()
   )
   embed.set_thumbnail(url = icon)
   embed.add_field(name = "Owner", value = owner, inline = True)
   embed.add_field(name = "Server ID", value = id, inline = True)
   embed.add_field(name = "Region", value = region, inline = True)
   embed.add_field(name = "Member Count", value = memberCount, inline = True)

   await ctx.send(embed = embed)


#user info
@client.command(aliases = ['user', 'info'])
async def whois(ctx, member : discord.Member):
   embed = discord.Embed(title = member.name, description = member.mention,
                         color = discord.Color.red())
   embed.add_field(name = "ID", value = member.id, inline = False)
   embed.set_thumbnail(url = member.avatar_url)
   embed.set_footer(icon_url = ctx.author.avatar_url,
                    text = "Requested by " + str(ctx.author.name))
   await ctx.send(embed = embed)

#help command
@client.command()
async def commands(ctx):
    embed = discord.Embed(title = "Command List", description = "Command prefix is '!'", color = discord.Color.red())

    embed.add_field(name = "General", value = "server whois", inline = True)
    embed.add_field(name = "ToDo", value = "toDo add delete", inline = True)
    embed.add_field(name = "Music", value = "play", inline = True)
    embed.add_field(name = "Games", value = "tictactoe", inline = True)
    embed.add_field(name = "Misc", value = "inspire", inline = True)
    embed.set_footer(text = "Use !command <command name> to get more info")

    await ctx.send(embed = embed)

@client.command()
async def command(ctx, commandName):
    embed = discord.Embed(title = "Command info: " + commandName, color = discord.Color.red())

    if(commandName == "server"):
        embed.add_field(name = "!server", value = "Shows the information of the server", inline = True)
    elif(commandName == "whois"):
        embed.add_field(name = "!whois <@ user>", value = "Shows user ID", inline = True)
    elif(commandName == "toDo"):
        embed.add_field(name = "!toDo <@ user>",  value = "Show your ToDo List", inline = True)
        embed.add_field(name = "!add <List>", value = "Adds the list to your ToDo List", inline = True)
        embed.add_field(name = "!delete <List>", value = "Deletes the typed List", inline = True)
    elif(commandName == "play"):
        embed.add_field(name = "!play <url> <Voice Channel Name>", value = "Plays the used YouTube url", inline = True)
        embed.add_field(name = "!pause", value = "Pauses the music", inline = True)
        embed.add_field(name = "!resume", value = "Resumes the music", inline = True)
        embed.add_field(name = "!stop", value = "Deletes the music", inline = True)
        embed.add_field(name = "!leave", value = "Leaves the voice channel", inline = True)
        embed.set_footer(text = "WORK IN PROGRESS: Once music is done, use !leave and then !play to play a new song")
    elif(commandName == "tictactoe"):
        embed.add_field(name = "!tictactoe <@ yourself> <@ user>", value = "Play TicTacToe", inline = True)
        embed.add_field(name = "!place <number>", value = "Places your mark on the number", inline = True)
        embed.set_footer(text = "The board is set up as: \n(1, 2, 3)\n(4, 5, 6)\n(7, 8, 9)")
    elif(commandName == "inspire"):
        embed.add_field(name = "!inspire", value = "Gives an inspiring quote", inline = True)
            
    await ctx.send(embed = embed)


#ToDo list
@client.command()
async def toDo(ctx, member : discord.Member):
   embed = discord.Embed(title = "ToDo List", description = member.name + "'s ToDo list",
                         color = discord.Color.red())
   
   for repeat in range(len(to_do)):
      embed.add_field(name = str(repeat + 1), value = to_do[repeat], inline = False)
   await ctx.send(embed = embed)

@client.command()
async def add(ctx, addList):
    to_do.append(addList)
    await ctx.send("Added: '" + addList + "'")


#inspire
@client.command()
async def inspire(ctx):
   response = requests.get("https://zenquotes.io/api/random")
   json_data = json.loads(response.text)
   quote = json_data[0]['q'] + " -" + json_data[0]['a']

   await ctx.send(quote)

#music
@client.command()
async def play(ctx, url : str, channelName):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    if(ctx.author.voice):
        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = channelName)
        await voiceChannel.connect()
        voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format': '249/250/251',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


#tic tac toe
player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@688534433879556134>).")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")

"""
@client.event
   if str(message.channel) == "chat" and str(message.author) == "tigertaigaa#7429":
      await message.channel.purge(limit = 1)
"""

client.run("ODc3MDMyODk4NDg4ODMyMDIx.YRsuiQ.Vx-Prj9rENtwi7i3Cw8FIB2Mk7I")
