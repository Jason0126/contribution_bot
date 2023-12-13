# -*- coding: utf-8 -*-
from discord.ext import commands, tasks
import discord
from datetime import datetime, timedelta
import json
import os

#
file_name = "data.json"
new_data = {
    "user_id": "",
    "join_time": "",
    "leave_time": "",
    "contribution_time": 0,
    "contribution_level": 0
}
#

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)


def check_db_user_id(user_id):
  with open('data.json', 'r') as file:
    jsonData = json.load(file)
    for result in jsonData['data']:
      if result['user_id'] == str(user_id):
        return True
    return False


def add_user_join_time(user_id, join_time):
  with open('data.json', 'r') as file:
    jsonData = json.load(file)
  if check_db_user_id(user_id):
    for index in range(len(jsonData['data'])):
      if jsonData['data'][index]['user_id'] == str(user_id):
        jsonData['data'][index]['join_time'] = join_time
        with open('data.json', 'w') as file2:
          json.dump(jsonData, file2, indent='\t')
        break
  else:
    new_data['user_id'] = f'{user_id}'
    new_data['join_time'] = join_time
    jsonData['data'].append(new_data)
    with open('data.json', 'w') as file2:
      json.dump(jsonData, file2, indent='\t')


def add_user_leave_time(user_id, leave_time):
  with open('data.json', 'r') as file:
    jsonData = json.load(file)
  if check_db_user_id(user_id):
    for index in range(len(jsonData['data'])):
      if jsonData['data'][index]['user_id'] == str(
          user_id) and jsonData['data'][index]['join_time'] != "":
        jsonData['data'][index]['leave_time'] = leave_time
        contribution_time = datetime.strptime(
            jsonData['data'][index]['leave_time'],
            "%Y-%m-%d %H:%M") - datetime.strptime(
                jsonData['data'][index]['join_time'], "%Y-%m-%d %H:%M")
        total_time = jsonData['data'][index]['contribution_time'] + (
            contribution_time.total_seconds() / 60)
        print(total_time)
        level = total_time / 10
        jsonData['data'][index]['contribution_time'] = total_time
        jsonData['data'][index]['contribution_level'] = int(level)
        with open('data.json', 'w') as file2:
          json.dump(jsonData, file2, indent='\t')
        break


def get_user_contribution(user_id):
  with open('data.json', 'r') as file:
    jsonData = json.load(file)
    if check_db_user_id(user_id):
      for index in range(len(jsonData['data'])):
        if jsonData['data'][index]['user_id'] == str(user_id):
          contri_data = [
              jsonData['data'][index]['contribution_time'],
              jsonData['data'][index]['contribution_level']
          ]
          return contri_data
    else:
      return [0, 0]


@client.event
async def on_ready():
  print("Discord Bot is running.")
  print(".......................")


@client.event
async def on_voice_state_update(member, before, after):
  if before.channel is None and after.channel is not None:
    time1 = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f'{member.id} join the {after.channel.name} at {time1}')
    add_user_join_time(member.id, time1)

  if after.channel is None:
    time2 = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f'{member.id} leave the {before.channel.name} at {time2}')
    add_user_leave_time(member.id, time2)

  if after.channel is not None:
    channel = client.get_channel(1141970073360289853)
    await channel.send(str(member.nick) + " join " + str(after.channel.name))


@client.command()
async def check(ctx, member: discord.Member = None):
  print("check")
  user = member if member != None else ctx.author
  contri_data = get_user_contribution(user.id)
  #print(contri_data)
  embed = discord.Embed(title=f"{user.nick}貢獻值",
                        color=discord.Color.green(),
                        timestamp=ctx.message.created_at)
  embed.add_field(name="貢獻時間", value=str(contri_data[0]), inline=False)
  embed.add_field(name="貢獻等級", value=str(contri_data[1]), inline=False)
  await ctx.send(embed=embed)


client.run(os.environ.get('dcbot_token'))
