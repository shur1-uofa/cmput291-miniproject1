import sqlite3
import os
DBPATH = "./test.db"
SCHEMAPATH = "./prj-tables.txt"

conn = None
cursor = None

def isDBPresent():
	return os.path.exists(DBPATH)

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

if __name__ == "__main__":
	if not isDBPresent():
		success  = createDB()
		if not success:
			print("Exiting program")
			exit()
	else:
		success = connectToDB()
		if not success:
			print("Exiting program")
			exit()
	
	with open("./test-data.sql", 'r') as f:
		try:
			cursor.executescript(f.read())
			conn.commit()
			print("Successfully inserted test data")
		except sqlite3.Error as e:
			print("Failed to insert test data")
			print(e)
		
	conn.close()

