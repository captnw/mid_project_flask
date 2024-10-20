# mid_project_flask
Building a RESTful API with Flask

By William N, X, and X

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