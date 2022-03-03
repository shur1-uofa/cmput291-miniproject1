import sqlite3
import os

conn = None
cursor = None
DBPATH = "./test.db"
SCHEMAPATH = "./prj-tables.txt"

# Check if DB exists
def isDBPresent():
	return os.path.exists("./test.db")

# Create database with the specified schema file provided
# Return True if success. False otherwise
def createDB():

	with open(SCHEMAPATH, 'r') as f:
		try:
			conn = sqlite3.connect(DBPATH)
			cursor = conn.cursor()

			cursor.executescript(f.read())
			conn.commit()

		except sqlite3.Error as e:
			print("Database failed to be created")
			print(e)
			# Remove the database we tried to create 
			os.remove(DBPATH)
			return False

	return True

# Connect to database given by DBPATH global var
# Return True if success. False otherwise
def connectToDB():

	try:
		conn = sqlite3.connect(DBPATH)
		cursor = conn.cursor()
		cursor.execute('PRAGMA foreign_keys=ON')
		conn.commit()
	except sqlite3.Error as e:
		print("Failed to connect to database")
		print(e)
		return False
	
	return True


def loginScreen():
	print("Success")


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
	
	loginScreen()


# Run below if this file is directly being executed
if __name__ == "__main__":
	main()
