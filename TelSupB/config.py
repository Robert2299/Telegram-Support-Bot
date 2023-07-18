"""
To start working with the bot, you need to configure the bot's configuration file - config.py.
The mandatory variables are TOKEN, ADMIN_ID, and MySQL.
You can leave PROXY_URL empty.

I will provide instructions for installation and configuration on Linux, Ubuntu-based distributions. If you have Windows or a different distribution, the differences from the guide below will only be in the steps for installing and configuring MySQL. So, if you encounter any issues, try finding a guide specifically for installing MySQL on your operating system.

First, check if MySQL is installed on your PC.
Open the terminal and type the command: mysql --version
If you see a message similar to: mysql Ver xx.xx ****, then you can proceed to step number 2.
1.2. If MySQL is not installed, enter a few commands in the terminal:
sudo apt update
sudo apt install mysql-server

Go back to step 1 and check if you have installed everything correctly.
If you see a message with the version of the installed MySQL, then continue to the next step.
If not, go back and double-check what you might have done wrong.

With the MySQL installation completed, let's move on to creating a user and a database.
Enter the following command in the terminal: mysql
2.2. After that, create a user with the following command:
CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';

Where 'user' is the username you want to use
And 'password' is the password for the user

2.3. Grant privileges to the user:
GRANT ALL PRIVILEGES ON * . * TO 'user'@'localhost';
FLUSH PRIVILEGES;

Where 'user' is the username you entered in the previous step

2.4. Create a database:
CREATE DATABASE support_db;

Where support_db is the name of the database

2.5. Replace all the values in the MySQL variable:
localhost - leave it unchanged
user - the username you created
password - the password for the user
support_db - the name of the database

Create your bot and obtain a token for it.
Go to the link t.me/BotFather or search for @BotFather in Telegram and enter the command /newbot.
Follow the instructions provided by the bot and specify the obtained token in the TOKEN variable.

Find a bot that will send you your Telegram ID.
Some examples of such bots are @userinfobot or @username_to_id_bot.
Enter the received ID in the ADMIN_ID variable.

With that, the configuration setup is complete. You can simply save and close this file. @END_SOFT
"""

MySQL = ['localhost', 'user', 'password', 'support_db']
TOKEN = '@END_SOFT'
ADMIN_ID = '@END_SOFT'
PROXY_URL = '@END_SOFT'