# mid_project_flask
Building a RESTful API with Flask

By William Nguyen, Randell Lapid, and Fabrizio Mejia

This is a library application where user can upload short books (in the form of .txt files). Books can only be 1MB.
If you're not signed in, you can see all of the metadata of the public books, and if you're signed in, you can see the private books as well.

# Prerequisites
- python 3.10.4 and above (tested on 3.10.4)
- MySQL workbench

# How to install
1. Initialize python virtual environment folder (run this command in the directory `python -m venv .venv`)
2. Navigate to .venv/Scripts
3. Activate the virtual environment (for windows it is just `activate`, for bash prompt it is `source activate`, Linux is probably `./activate`)
4. Once you see the (.venv), run the command `pip install -r requirements` to install all dependencies

# MySQL workbench
Run the following commands to instantiate the book database in MySQL workbench:
```
CREATE SCHEMA `Mid_Project`;

CREATE TABLE `Mid_Project`.`Book` (
`ID` INT NOT NULL AUTO_INCREMENT,
`Title` VARCHAR(45),
`Author` VARCHAR(45),
`MembersOnly` BOOL, 
PRIMARY KEY (`ID`));
```

# Running the server
You'll probably need to configure the following values dependong on how you configured your MYSQL environment.
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_HOST

Then simply run py main.py

# Endpoints
- /
  - Home
  - Displays all public book
  - No JWT token required
- {GET / POST} /login
  - No JWT token required
- /profile
  - Displays number of times page is visited, and displays all books
  - Need to access with JWT token (bearer token or URL argument)
- /logout
  - Logs you out
  - Need to access with JWT token (bearer token or URL argument)
- {GET} /public_books
  - Retrieves a list of public books
- {GET / POST} /books
  - Gets a list of all books, or append a single book
  - Need to access with JWT token (bearer token or URL argument)
- {GET / PUT / DELETE} /book
  - Get a single book, update a single book, or delete a single book
  - Need to access with JWT token (bearer token or URL argument)
- /upload
  - A form allowing you to upload a file
  - Need to access with JWT token (bearer token or URL argument)
- {POST} /sendFile
  - Endpoint allowing one to upload a .txt file that doesn't exceed 1 MB
  - This file will be saved in the uploads folder
  - Need to access with JWT token (bearer token or URL argument)
