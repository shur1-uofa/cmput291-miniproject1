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
	return os.path.exists("./test.db")


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
	print("register screen")


def customerMenu():
	print("in customer menu")

def editorMenu():
	print("in editor menu")

#FIXME: Delete this when handing it in. 
def insertTestData():
	cursor.execute("INSERT INTO customers VALUES('0001', 'Scott', 'scottpass')")
	cursor.execute("INSERT INTO editors VALUES('0002', 'editorpass')")


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

	insertTestData()
	InitScreen()


# Run below if this file is directly being executed
if __name__ == "__main__":
	main()
