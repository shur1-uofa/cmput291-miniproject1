import sqlite3
from pathlib import Path

conn = None
cursor = None
DBPATH = "./test.db"
SCHEMAPATH = "./prj-tables.txt"

def isDBPresent():
	my_file = Path(DBPATH)
	return my_file.is_file()

def createDB():
	conn = sqlite3.connect(DBPATH)
	cursor = conn.cursor()

	with open(SCHEMAPATH) as f:
		try:
			cursor.execute(f.read().decode('utf-8'), multi=True)
		except:
			print("Database failed to be created")
			return False

	conn.commit()
	return True

def connectToDB():
	try:
		conn = sqlite3.connect(DBPATH)
		cursor = conn.cursor()
		cursor.execute('PRAGMA foreign_keys=ON')
		conn.commit()
	except:
		print("Failed to connect to database")
		return False

def loginScreen():
	print("Success")



def main():
	if not isDBPresent():
		req = createDB()
		if not req:
			return
	else:
		connectToDB()
	
	loginScreen()


# If this file is directly being executed (not imported or anything) then run this...
if __name__ == "__main__":
	main()
