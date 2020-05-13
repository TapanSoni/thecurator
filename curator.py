"""
The Curator
curator.py

Author: Tapan Soni
Date: 5/12/2020

Description: This bot was created for a very specific purpose. It uses a csv list of students
(includes student name, email, and student ID number) and authenticates incoming Discord accounts
based on that list. If a user wants to join the server and they are not in the list, they are denied
entry. Both the student email and student ID attributes are checked and must match for users to be
able to enter the server. Once the user is authenticated, they are automatically assigned a specific
role which allows them access to specific channels with preset permissions, and a unchangeable nickname -
their first name and last name. This way, the users of are segmented into their individual class channels,
and their nicknames represent their real legal names. 
"""

import os
import random
import time
import discord
import discord.utils
import discord.guild
from dotenv import load_dotenv
import csv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

studentEmail = ""
studentBannerID = ""

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_member_join(member):
    students = []  # Holds the students that are in the class
    alreadyInServer = []  # Holds the students that already in the server

    with open('<INSERT LOCATION OF STUDENT LIST CSV FILE>') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                students.append(row)
                line_count += 1
    
    # Initially assign the Rules role -- Can only view the Rules channel and nothing else -- no posting allowed
    purgatoryRole = discord.utils.get(member.guild.roles, name="Rules")
    await member.add_roles(purgatoryRole)

    await member.create_dm()
    await member.dm_channel.send(
        f'Hello {member.name}, I am The Curator\nI am here to make sure you are authorized to be in this server.\nJust answer these questions and I can let you in.'
    )

    correctEmail = "N"

    # If correct email is input, then quit
    while(correctEmail != "Y"):
        # Ask for the student email
        await member.dm_channel.send("What is your Rowan University student email? (example: <INSERT EMAIL EXAMPLE>)")

        def check(m):
            return m.author == member and m.channel == member.dm_channel

        m = await client.wait_for("message", check=check)
        studentEmail = str(m.content)

        # Confirmation
        await member.dm_channel.send(studentEmail)
        await member.dm_channel.send("Is that the correct email address? Make extra sure that it is - (Y/N)")

        m = await client.wait_for("message", check=check)
        correctEmail = str(m.content).upper()

    # Check for Banner ID
    correctBannerID = "N"

    while(correctBannerID != "Y"):
        await member.dm_channel.send("What is your Rowan University Banner ID? (example: <INSERT ID EXAMPLE>)")

        m = await client.wait_for("message", check=check)
        studentBannerID = str(m.content)

        # Confirmation
        await member.dm_channel.send(studentBannerID)
        await member.dm_channel.send("Is that the correct Banner ID? Make extra sure that it is - (Y/N)")

        m = await client.wait_for("message", check=check)
        correctBannerID = str(m.content).upper()

    await member.dm_channel.send(f"**Your input\n{studentEmail}\n{studentBannerID}**")

    validate = 0

    # Check if the student email and banner ID is in the students array
    studentProfile = ()
    # If true, then get the student profile
    for profile in students:
        if(profile[2] == studentEmail and profile[1] == studentBannerID):
            validate = 1
            studentProfile = profile

    # Check if the student is already in the server
    t = open("alreadyin.txt", "r")
    q = t.readlines()
    t.close()

    # Remove the new lines
    for e in q:
        alreadyInServer.append(e.replace("\n", "").split(","))

    # Check if the student is already in the server
    if(studentEmail in alreadyInServer):
        validate = 2

    await member.dm_channel.send("**Validating...**")

    if(validate == 1):
        # Get full name for nickname
        lastName, firstName = studentProfile[0].split(",")
        lastName = lastName.strip()
        firstName = firstName.strip()

        await member.dm_channel.send("**Approved**")
        await member.dm_channel.send(f"**You are {firstName} {lastName}. Check the server**")
        await member.dm_channel.send("**If there are any issues -- contact <INSERT ADMIN CONTACT INFORMATION> with a screenshot of The Curator's output**")
        await member.remove_roles(purgatoryRole)

        # Get the new role
        newRole = discord.utils.get(member.guild.roles, name=studentProfile[3])
        await member.add_roles(newRole)

        # Set the nickname
        await member.edit(nick=firstName + " " + lastName)

        # Write to the alreadyin.txt file
        f = open("alreadyin.txt", "a")
        f.write(studentEmail + "," + firstName + " " + lastName + "\n")
        f.close()
    elif(validate == 0):
        await member.dm_channel.send("**You are not authorized to join this server** -- It's probably because you typed in the wrong Email/Banner ID combo")
        await member.dm_channel.send("**If you think this is a mistake - contact <INSERT ADMIN CONTACT INFORMATION> with a screenshot of The Curator's output**")
        await member.remove_roles(purgatoryRole)
        await member.kick()  # Kicks the user
    elif(validate == 2):
        await member.dm_channel.send("**You are already in the server -- OR -- Someone else is trying to join as you**")
        await member.dm_channel.send("**If you think this is a mistake - contact <INSERT ADMIN CONTACT INFORMATION> with a screenshot of The Curator's output**")
        await member.remove_roles(purgatoryRole)
        await member.kick()  # Kicks the user


client.run(TOKEN)
