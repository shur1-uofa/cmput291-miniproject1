import sqlite3
import os
import time

conn = None
cursor = None
DBPATH = "./test.db"
SCHEMAPATH = "./prj-tables.txt"
user_info = {
	"id": None,
	"name": None
}

# Check if DB exists
def isDBPresent():
	return os.path.exists(DBPATH)


# Create database with the specified schema file provided
# Return True if success. False otherwise
def createDB():
	global conn, cursor

	with open(SCHEMAPATH, 'r') as f:
		script = f.read()
		try:
			conn = sqlite3.connect(DBPATH)
			conn.row_factory = sqlite3.Row
			cursor = conn.cursor()

			cursor.executescript(script)
			conn.commit()

		except sqlite3.Error as e:
			print("Database failed to be created")
			print(e)
			# Remove the database file we tried to create 
			os.remove(DBPATH)
			return False

	return True


# Connect to database given by DBPATH global var
# Return True if success. False otherwise
def connectToDB():
	global conn, cursor

	try:
		conn = sqlite3.connect(DBPATH)
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		cursor.execute('PRAGMA foreign_keys=ON')
		conn.commit()
	except sqlite3.Error as e:
		print("Failed to connect to database")
		print(e)
		return False
	
	return True


def closeProgram():
	conn.close()
	exit()


# Returns True if Yes. Return False if No. 
def getUserYesOrNo():
	resp = ""
	while resp != "N" and resp != "Y":
		resp = str(input("N or Y: ")).strip().upper()
		if resp == "Y":
			return True
		elif resp == "N":
			return False
		else:
			input("Invalid response. Try again...")


def InitScreen():

	while True:
		print("----- Select your options -----")
		print("Login - 1")
		print("Register (as customer) - 2")
		print("Exit program - 3")
		# Call strip function to ignore spaces
		resp = str(input("Type in your selection: ")).strip()

		if resp == "1":
			print()
			loginScreen()
		elif resp == "2":
			registerScreen()
		elif resp == "3":
			print("Exitting program")
			closeProgram()
		else:
			print("Invalid selection. Try again")
			input("...")


def loginScreen():
	
	while True:
		print("----- Login -----")
		id = str(input("ID: ")).strip()
		pwd = str(input("Password: ")).strip()
		
		# Try logging in as customer
		cursor.execute("SELECT * FROM customers WHERE cid=:id", { "id":id })
		row = cursor.fetchone()
		
		# Case : customer with wrong password
		if row != None and row["pwd"] != pwd:
			print("Invalid credentials. Try again?")
			resp = getUserYesOrNo()
			if resp:
				continue
			else:
				return
		# Case : customer with right password
		elif row != None and row["pwd"] == pwd:
			user_info["id"] = id
			user_info["name"] = row["name"]

			print("Welcome " + user_info["name"])
			customerMenu()
			break

		# Try logging in as editor
		cursor.execute("SELECT * FROM editors WHERE eid=:id",{ "id":id })
		row = cursor.fetchone()
		
		# Case : invalid id or editor with wrong password
		if row == None or row["pwd"] != pwd:
			print("Invalid credentials. Try again?")
			resp = getUserYesOrNo()
			if resp:
				continue
			else:
				return
		# Case : editor with right password
		else:
			user_info["id"] = id
			
			print("Welcome editor " + id)
			editorMenu()
			break


def registerScreen():

	while True:
		print("----- Register -----")
		id = str(input("Provide ID: ")).strip()
		name = str(input("Provide name: "))
		#FIXME: password must be not visible at time of typing
		pwd = str(input("Provide password: "))
		
		if len(pwd) < 1 or len(name) < 1 or len(id) < 1:
			input("Please input appropriate fields...")
			continue

		# First it cannot have the same id as an editor's
		try:
			cursor.execute("SELECT 1 FROM editors WHERE eid = :id LIMIT 1", { "id": id } )
			res = cursor.fetchone()
		except sqlite3.Error as e:
			print("Something went wrong with sqlite3")
			print(e)
			print()
			return

		# If id is already taken by an editor
		if res != None:
			input("Invalid ID. Please try again...")
			continue

		# Now check if id already exists as customer id
		try:
			cursor.execute("SELECT 1 FROM customers WHERE cid = :id LIMIT 1", { "id": id} )
			res = cursor.fetchone()
		except sqlite3.Error as e:
			print("Something went wrong with sqlite3")
			print(e)
			print()
			return

		if res != None:
			input("Invalid ID. Please try again...")
			continue

		# Now since ID is unique, and we checked little things, it should be good to go
		try:
			cursor.execute("INSERT INTO customers VALUES(?, ?, ?)", (id, name, pwd))
			conn.commit()
		except sqlite3.Error as e:
			print("Could not add your registration information")
			print(e)
			print()
			return
		user_info["id"] = id
		user_info["name"] = name

		print("Successfully registered.")
		print()
		customerMenu()
		break

	return


def customerMenu():
	
	while True:
		print("----- Customer Menu -----")
		print("Select your options")
		print("Start a session - 1")
		print("Search for movies - 2")
		print("End watching a movie - 3")
		print("End the session - 4")
		print("Log out - 5")
		print("Exit program - 6")
		resp = str(input("Your selection: ")).strip()

		# TODO: fill out functionalities
		if resp == "1":
			# Do start session stuff
			print("")
		elif resp == "2":
			# Do search movie stuff
			print()
		elif resp == "3":
			# Do end movie stuff
			print()
		elif resp == "4":
			# Do end session stuff
			print()
		elif resp == "5":
			print("Logging out")
			user_info["id"] = None
			user_info["name"] = None
			return
		elif resp == "6":
			print("Exitting program")
			closeProgram()
		else:
			input("Invalid selection. Try again...")
			continue


def editorMenu():

	while True:
		print("----- Editor Menu -----")
		print("Select your options")
		print("Add a movie - 1")
		print("Update a recommendation - 2")
		print("Log out - 3")
		print("Exit program - 4")
		resp = str(input("Your selection: ")).strip()

		# TODO: fill out functionalities
		if resp == "1":
			# Do add movie stuff
			print("")
		elif resp == "2":
			# Do update recommends stuff
			print()
		elif resp == "3":
			print("Logging out")
			user_info["id"] = None
			return
		elif resp == "4":
			print("Exitting program")
			closeProgram()
		else:
			input("Invalid selection. Try again...")
			continue


#Prompts a user for movie keywords and 
#returns a list of all movies ordered by number of matches  
def search4movies():
	#User Searches for movie
	movie_input = str(input("Search for a movie: "))

	#Identify keywords of user input
	split_input = movie_input.split()

	#Add a 'number of matches' attribute to movies
	cursor.executescript("""CREATE TEMP TABLE temp AS SELECT * FROM movies;
			    ALTER TABLE temp ADD num int DEFAULT 0;
			    """)

	#increment the 'number of matches' for each row
	for x in split_input:
	    cursor.execute("""UPDATE temp
			SET num = num + 1
			WHERE title LIKE '%'||:x||'%'""",{'x' : x})

	#select and order results
	cursor.execute("""SELECT *
		    FROM temp
		    WHERE num > 0
		    ORDER BY num DESC;""")
	rows = cursor.fetchall()
	conn.rollback()
	conn.close()
	return rows

def main():
	if not isDBPresent():
		success  = createDB()
		if not success:
			print("Exiting program")
			return
	else:
		success = connectToDB()
		if not success:
			print("Exiting program")
			return

	InitScreen()


# Run below if this file is directly being executed
if __name__ == "__main__":
	main()
