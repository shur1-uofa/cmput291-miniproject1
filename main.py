import sqlite3
import os
import sys
import datetime
from getpass import getpass


class Database():

	# Initialize database by setting "private" attributes
	def __init__(self):
		self._conn = None
		self._cursor = None


	# Try open given database along with its schema text
	# Return false if failure. 
	def open(self, DBPATH, SCHEMAPATH):
		if not self.isDBPresent(DBPATH):
			success  = self.createDB(DBPATH, SCHEMAPATH)
			if not success:
				return False
		else:
			success = self.connectToDB(DBPATH)
			if not success:
				return False

		return True


	# Check if DB exists
	def isDBPresent(self, DBPATH):
		return os.path.exists(DBPATH)


	# Create database with the specified schema file provided
	# Return True if success. False otherwise
	def createDB(self, DBPATH, SCHEMAPATH):

		with open(SCHEMAPATH, 'r') as f:
			script = f.read()
			try:
				self._conn = sqlite3.connect(DBPATH)
				self._conn.row_factory = sqlite3.Row
				self._cursor = self._conn.cursor()

				self._cursor.executescript(script)
				self._conn.commit()

			except sqlite3.Error as e:
				print("Database failed to be created")
				print(e)
				# Remove the database file we tried to create 
				os.remove(DBPATH)
				return False

		return True


	# Connect to database given by DBPATH global var
	# Return True if success. False otherwise
	def connectToDB(self, DBPATH):

		try:
			self._conn = sqlite3.connect(DBPATH)
			self._conn.row_factory = sqlite3.Row
			self._cursor = self._conn.cursor()
			self._conn.commit()
		except sqlite3.Error as e:
			print("Failed to connect to database")
			print(e)
			return False
		
		return True


	# Close opened database
	def closeDB(self):
		if self._conn != None:
			self._cursor.close()
			self._conn.close()


	# Getter methods
	def getConn(self):
		return self._conn

	def getCursor(self):
		return self._cursor


	# With this, we automatically close the database when the database object 
	# is out of scope or deleted
	def __del__(self):
		self.closeDB()



# This will represent the superclass of the 3 menus we have: 
# start menu, customer, and editor menu
class Menu():

	def __init__(self, db):
		# Retrieve database stuff
		self._db = db 

	# Returns True if Yes. Return False if No. 
	def getUserYesOrNo(self):
		resp = ""
		while resp != "N" and resp != "Y":
			resp = input("N or Y: ").strip().upper()
			if resp == "Y":
				return True
			elif resp == "N":
				return False
			else:
				input("Invalid response. Try again...")

	# Close the program by closing the database as well then exit
	def closeProgram(self):
		# Delete database object
		del self._db
		# Skadoosh... leave. 
		exit()


class StartMenu(Menu):

	# Starts the start menu.
	def start(self):    

		while True:
			print("----- Initial Screen -----")
			print("Select your options")
			print("Login - 1")
			print("Register (as customer) - 2")
			print("Exit program - 3")
			# Call strip function to ignore spaces
			resp = input("Type in your selection: ").strip()

			if resp == "1":
				print()
				self.loginScreen()
			elif resp == "2":
				print()
				self.registerScreen()
			elif resp == "3":
				print("Exitting program")
				self.closeProgram()
			else:
				print("Invalid selection. Try again")
				input("...")


	# Starts the login screen
	def loginScreen(self):

		# Get connection object and cursor object
		conn = self._db.getConn()
		cursor = self._db.getCursor()
		

		while True:
			print("----- Login -----")
			id = input("ID: ").upper()
			pwd = getpass("Password: ") 

			# Try logging in as customer
			try:
				cursor.execute("SELECT * FROM customers WHERE UPPER(cid) = UPPER(:id)", { "id":id })
				row = cursor.fetchone()
			except sqlite3.Error as e:
				print("Something went wrong with sqlite3")
				print(e)
				return

			# Case : customer with wrong password
			if row != None and row["pwd"] != pwd:
				print("Invalid credentials. Try again?")
				resp = self.getUserYesOrNo()
				if resp:
					continue
				else:
					return
			# Case : customer with right password
			elif row != None and row["pwd"] == pwd:

				print("Welcome " + row["name"])
				customerMenu(self._db, id, row["name"])
				break

			# Try logging in as editor
			try:
				cursor.execute("SELECT * FROM editors WHERE UPPER(eid) = UPPER(:id)",{ "id":id })
				row = cursor.fetchone()
			except sqlite3.Error as e:
				print("Something went wrong with sqlite3")
				print(e)
				return

			# Case : invalid id or editor with wrong password
			if row == None or row["pwd"] != pwd:
				print("Invalid credentials. Try again?")
				resp = self.getUserYesOrNo()
				if resp:
					continue
				else:
					return
			# Case : editor with right password
			else:

				print("Welcome editor " + id)
				editorMenu(self._db, id)
				break


	# Starts the register screen
	def registerScreen(self):

		# Get connection object and cursor object
		conn = self._db.getConn()
		cursor = self._db.getCursor()


		while True:
			print("----- Register -----")
			
			# Get proper id 
			id = input("Provide ID: ")
			if len(id) < 1 or len(id) > 4:
				print("ID must be between 1 to 4 characters")
				continue

			# Get proper name
			name = str(input("Provide name: "))
			if len(name) < 1:
				print("Please provide a name")
				continue
			# Since assignment does not specify more on the form of name
			# I won't check additional constraints like space at start or something. 

			# Get proper password
			pwd = str(getpass("Provide password: "))
			if len(pwd) < 1:
				input("Please provide a password")
				continue
			# Again, assignment does not specify on form of password 
			# I won't check stuff like must be a secure password, must have mix of blah blah


			# ---- Check if id is unique... ---- # 

			# First it cannot have the same id as an editor's
			try:
				# Check if an editor with the given register id exists
				cursor.execute("SELECT 1 FROM editors WHERE UPPER(eid) = UPPER(:id) LIMIT 1", { "id": id } )
				res = cursor.fetchone()
			except sqlite3.Error as e:
				print("Something went wrong with sqlite3")
				print(e)
				print()
				return

			# If id is already taken by an editor then try again
			if res != None:
				print("Invalid ID. Try again?")
				resp = self.getUserYesOrNo()
				if resp:
					continue
				else:
					break

			# Now check if id already exists as customer id 
			try:
				cursor.execute("SELECT 1 FROM customers WHERE UPPER(cid) = UPPER(:id) LIMIT 1", { "id": id} )
				res = cursor.fetchone()
			except sqlite3.Error as e:
				print("Something went wrong with sqlite3")
				print(e)
				print()
				return

			if res != None:
				input("Invalid ID. Try again?")
				resp = self.getUserYesOrNo()
				if resp:
					continue
				else:
					break

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



class CustomerMenu(Menu):

	def __init__(self, db, id, name):
		# Call the superclass constructor
		super().__init__(db)
		# Keep track of basic user information
		self._id = id
		self._name = name
		# Keep track of session if started
		self._sid = None
		self._sidStart = None   # Session start datetime
		# Keep track of currently watching movie
		self._mid = None
		self._midStart = None   # Movie watching start datetime


	def start(self):
		
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
				print("Starting a session")
				self.startSession()
			elif resp == "2":
				# Do search movie stuff
				print()
			elif resp == "3":
				# Do end movie stuff
				print()
				self.endWatchMovie()
			elif resp == "4":
				# Do end session stuff
				print()
			elif resp == "5":
				print("Logging out")
				return
			elif resp == "6":
				print("Exiting program")
				self.closeProgram()
			else:
				input("Invalid selection. Try again...")
				continue



	# Prompts a user to start a session
	def startSession(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		cursor.execute("SELECT MAX(sid) FROM sessions")
		max_id = cursor.fetchone()[0]
		if max_id == None:
			new_id = 1
		else:
			new_id = int(max_id) + 1
		if self.sidStart == None:
			session_date = datetime.date.today()
			session_start_time = time.time()
			cursor.execute("""INSERT INTO sessions VALUES (?,?,?,NULL);""", (new_id, user_info["id"], session_date))
			self.sidStart = session_start_time
			print("Session started successfully")
			conn.commit()
		else:
			print("There is already a session running")


	# The end watch movie functionality
	def endWatchMovie(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		# Check if a movie is being currently watched
		if self._mid == None:
			# If no movies being watched then return
			print("No movie is being watched.")
			return
		
		# Find minutes watched
		diffTime = datetime.datetime.now() - self._midStart
		watchMins = diffTime.total_seconds() // 60

		# Get runtime of movie (and also title)
		cursor.execute('''
				SELECT title, runtime 
				FROM movies
				WHERE mid = :mid
				''', {"mid": self._mid})
		row = cursor.fetchone()
		runtime = row["runtime"]
		mtitle = row["title"]
		
		# Check if current movie has finished watching
		if watchMins > runtime:
			print("No movie is being watched")
			watchMins = runtime
		else:
			print("You are currently watching " + mtitle)
			print("Do you want to stop watching it?")
			resp = self.getUserYesOrNo()
			# If reply is no then return    
			if not resp:
				print("Going back to main menu")
				return

		# End watching movie
		cursor.execute('''
				UPDATE watch 
				SET duration = :watchtime 
				WHERE mid = :mid AND sid = :sid AND cid = :cid
				''', {"mid":mid, "sid":sid, "cid":cid, "watchtime":watchMins})
		self._mid = None
		self._midStart = None
		conn.commit()
		return



class EditorMenu(Menu):

	def __init__(self, db, id):
			# Call the superclass constructor
			super().__init__(db)
			# Keep track of basic user information
			self._id = id


	def start(self):

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
				return
			elif resp == "4":
				print("Exitting program")
				self.closeProgram()
			else:
				input("Invalid selection. Try again...")
				continue

	#Returns a list of movie pairings and their respective number of customers
	#timerange = 'monthly','annual',or 'alltime'
	#Output_format: List of tuples of the form (mid, mid,number of customers, indicator = "0"(not in recommendations) or "1"(in recommendations))
	def report(self, timerange):

		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		if timerange == 'monthly':
			datestring = { 'date' : (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d') }
		elif timerange == 'annual':
			datestring = { 'date' : (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d') }
		elif timerange == 'alltime':
			datestring = { 'date' : '' }
		else:
			raise Exception("report() function parameter invalid. It should be 'monthly', 'annual', or 'alltime'.")
			return

		cursor.execute("""WITH watched AS (SELECT w.sid, w.cid, w.mid FROM watch w, movies m WHERE w.mid = m.mid AND (w.duration + w.duration) >= m.runtime),
						watchedwithrange AS (SELECT DISTINCT w.mid, w.cid FROM watched w, sessions s WHERE w.sid = s.sid AND s.sdate >= :date),
						pairings AS (SELECT w1.mid AS mid1, w2.mid as mid2, COUNT(*) AS count FROM watchedwithrange w1, watchedwithrange w2 WHERE w1.cid = w2.cid AND w1.mid != w2.mid GROUP BY w1.mid, w2.mid ORDER BY count DESC),
						pairingswithindic AS ( SELECT mid1, mid2, count, (1) as indic FROM pairings WHERE EXISTS( SELECT * FROM recommendations WHERE pairings.mid1 = watched AND pairings.mid2 = recommended))
						SELECT mid1, mid2, count, indic FROM pairings left outer join pairingswithindic using (mid1,mid2,count);""", datestring);
		p = cursor.fetchall()
		conn.rollback()
		return p

	#Prompts a user for movie keywords and
	#returns a list of all movies ordered by number of matches
	#Output_format: list of tuples of the form (mid, title, numberofmatches)
	def search4movies(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		#User Searches for movie
		movie_input = str(input("Search for a movie: "))

		#Identify keywords of user input
		split_input = movie_input.split()

		#Make runtime be a temporary 'number of matches' column
		cursor.execute("""UPDATE movies
						SET runtime = 0;
							""")

		#increment the 'number of matches' for each row
		for x in split_input:
			cursor.execute("""UPDATE movies
						SET runtime = runtime + 1
						WHERE title LIKE '%'||:x||'%'
						OR EXISTS ( SELECT * FROM casts c, moviePeople p WHERE movies.mid = c.mid AND p.pid = c.pid AND p.name LIKE '%'||:x||'%')
						OR EXISTS ( SELECT * FROM casts c WHERE movies.mid = c.mid AND c.role LIKE '%'||:x||'%');""",{'x' : x})

		#select and order results
		cursor.execute("""SELECT mid, title, runtime
					FROM movies
					WHERE runtime > 0
					ORDER BY runtime DESC;""")
		rows = cursor.fetchall()
		conn.rollback()
		return rows
		  

	#Prompts for movie details and cast members and adds them to the database if granted by the user
	def addaMovie(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		while True:
			try:
				movie_id = int(input("Enter the movie_id: "))
				title = str(input("Enter the title: " ))
				year = int(input("Enter the year: "))
				runtime = int(input("Enter the runtime: " ))
				cursor.execute("""INSERT INTO movies VALUES (?,?,?,?);""",(movie_id, title, year, runtime))
			except ValueError:
				print('Invalid input. Try again.')
				continue
			except sqlite3.IntegrityError:
				print("Movie id taken. Try again.")
				continue
			else:
				break
		while True:
			while True:
				try:
					cast_id = int(input("Enter cast id (integer): "))
				except ValueError:
					print('Invalid Input.Try again.')
					continue
				else:
					break
			cursor.execute("""SELECT m.name, m.birthyear FROM casts c, moviePeople m WHERE c.pid = m.pid AND c.pid = :cast_id;""", {'cast_id' : cast_id })
			person = cursor.fetchall()
			if len(person) == 0:
				print("The person does not exist in the database.")
				try:
					name = str(input("Enter name of person: " ))
					birthyear = int(input("Enter birthyear (integer): " ))
				except ValueError:
					print("Invalid Input. Try again.")
					continue
				else:
					role = str(input("Enter the role: "))
					cursor.execute("""INSERT INTO moviePeople VALUES (?,?,?);""", (cast_id, name, birthyear))
					cursor.execute("""INSERT INTO casts VALUES (?,?,?);""", (movie_id, cast_id, role))
			else:
				print('Name:' + str(person[0][0]) + '\nBirthYear: ' + str(person[0][1]))
				print("Provide role for this person ? ")
				if getUserYesOrNo() == 1:
					role = str(input("Enter the role: " ))
					cursor.execute("""INSERT INTO casts VALUES (?,?,?);""", (movie_id, cast_id, role))
			print("Add more cast members ?")
			if getUserYesOrNo() == 0:
				break
		print("Save movie in the database ?")
		if getUserYesOrNo() == 1:
			conn.commit()
			return
		conn.rollback()
	

	
def main():
	# Get commandline arguments
	if len(sys.argv) < 3:
		print("Insufficient number of arguments. Please provide database path name and schema path name")
		return
	else if len(sys.argv) > 3:
		print("Too many arguments")
		return

	DBPATH = sys.argv[2]
	SCHEMAPATH = sys.argv[3]

	if not os.path.exists(DBPATH) or not os.path.exists(SCHEMAPATH):
		print("Please give a valid file")
		return


	# Create database object and open 
	db = Database()
	success = db.open(DBPATH, SCHEMAPATH)
	# Check if opening was successful. If not, exit program
	if not success:
		print("Exiting program.")
		exit()

	# Now here, we can do stuff with database 
	# Start our start screen
	initScreen = StartMenu(db)
	initScreen.start()


# Run below if this file is directly being executed
if __name__ == "__main__":
	main()
