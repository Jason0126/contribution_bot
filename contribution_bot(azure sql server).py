# -*- coding: utf-8 -*-
from discord.ext import commands ,tasks
import discord
from datetime import datetime, timedelta
import pyodbc
from contextlib import contextmanager
import os

#SQL server information
SERVER = 'jason-dc-bot-test.database.windows.net'
DATABASE = 'dc_bot_dbtest'
USERNAME = 'jason0126'
PASSWORD = 'Zxc910126!'
DRIVER = '{ODBC Driver 18 for SQL Server}'
conn_str = f'Driver={DRIVER};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
#


intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix="!",intents=intents) 

@contextmanager
def open_db_connection(connection_string):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        connection.close()

def check_db_user_id(user_id):
    with open_db_connection(conn_str)as cursor:
        cursor.execute("SELECT user_id FROM dbo.contribution_table")
        results = cursor.fetchall()
        for result in results:
            if result[0] == str(user_id):
                return True
        return False

    
def add_user_join_time(user_id,join_time):
    with open_db_connection(conn_str)as cursor:
        if check_db_user_id(user_id):
            print("yes")
            cursor.execute(f'UPDATE dbo.contribution_table SET join_time = \'{join_time}\',leave_time=\'{join_time}\' WHERE user_id = \'{user_id}\'')
            cursor.commit()
        else:
            print("no")
            cursor.execute(f'INSERT INTO dbo.contribution_table (user_id,join_time,leave_time,contribution_time,contribution_level) VALUES (\'{user_id}\',\'{join_time}\',\'{join_time}\',0,0)')
            cursor.commit()
    
def add_user_leave_time(user_id,leave_time):
    with open_db_connection(conn_str)as cursor:
        if check_db_user_id(user_id):
            print("yes")
            cursor.execute(f'UPDATE dbo.contribution_table SET leave_time=\'{leave_time}\' WHERE user_id = \'{user_id}\'')
            cursor.commit()
            calculate_contribution(user_id)
        else:
            print("Not have this user")

def get_user_contribution(user_id):
    with open_db_connection(conn_str)as cursor:
        if check_db_user_id(user_id):
            cursor.execute(f'SELECT contribution_time,contribution_level FROM dbo.contribution_table WHERE user_id = \'{user_id}\'')
            results = cursor.fetchall()
        else:
            results = [[0,0]]
    return results

def calculate_contribution(user_id):
    with open_db_connection(conn_str)as cursor:
        cursor.execute(f'SELECT join_time,leave_time,contribution_time FROM dbo.contribution_table WHERE user_id = \'{user_id}\'')
        results = cursor.fetchall()
        contribution_time = datetime.strptime(results[0][1], "%Y-%m-%d %H:%M") - datetime.strptime(results[0][0], "%Y-%m-%d %H:%M")
        total_time = results[0][2]+(contribution_time.total_seconds() / 60)
        print(total_time)
        level = total_time / 10
        cursor.execute(f'UPDATE dbo.contribution_table SET contribution_time = {total_time},contribution_level= {level} WHERE user_id = \'{user_id}\'')
        cursor.commit()
    
@client.event
async def on_ready():
    print("Discord Bot is running.")
    print(".......................")
    

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        time1 = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f'{member.id} join the {after.channel.name} at {time1}')
        add_user_join_time(member.id,time1)
            
    
    if after.channel is None :
        time2 = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f'{member.id} leave the {before.channel.name} at {time2}')
        add_user_leave_time(member.id,time2)
        
        
    if after.channel is not None :
        channel = client.get_channel(1141970073360289853)
        await channel.send(str(member.nick) + " join " + str(after.channel.name))
 
@client.command()
async def check(ctx,member:discord.Member = None):
    print("check")
    user = member if member != None else ctx.author
    contri = get_user_contribution(user.id)
    embed = discord.Embed(title = f"{user.nick}貢獻值",color=discord.Color.green(),timestamp=ctx.message.created_at)
    embed.add_field(name = "貢獻時間", value = str(contri[0][0]),inline = False)
    embed.add_field(name = "貢獻等級", value = str(contri[0][1]),inline = False)
    await ctx.send(embed=embed)
    
client.run(os.environ.get('dcbot_token'))