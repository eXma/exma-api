# eXma API

This is a attempt to wrap a ancient invision power
board into a RESTful web api to build more modern clients for it.

## How to run the debug environment:

1. Clone the repo

   ```
   git clone git@github.com:janLo/exma-api.git
   ```
   
2. create/activate a virtualenv:

   ```
   virtualenv </some/path>
   . </some/path>/bin/activate
   ```
   
3. install requirenments:

   ```
   pip install requirenments.txt
   ```
   
4. create a file containing the db password in the project root:

   ```
   echo "password" > exma_pw
   ```
   
5. build a tunnel to the database:

   ```
   ssh -L 3306:localhost:3306 <mysql_host>
   ```
   
6. mount the images:

   ```
   sshfs user@host:<path_to_pictures> /mnt/tmp
   ```
   
7. start the server:

   ```
   python exma-api.py
   ```
   
8. enjoy!

## How to turn debug mode on/off:

There are two settings in exma-api.py:

* user_ressources.debug
* app.debug

The first enables or disables the debug mode for the auth stuff
(if disables its possible to test without auth at all!) The 
second enables the flask debug mode with its debug features:

* automatic reloading on script change
* enable the werkzeug debugger on exceptions
