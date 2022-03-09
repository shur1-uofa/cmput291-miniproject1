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
	# Return False if failure or True if success
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


	# Create database at DBPATH by running the sql in SCHEMAPATH file
	# Return True if success. False otherwise
	def createDB(self, DBPATH, SCHEMAPATH):

		with open(SCHEMAPATH, 'r') as f:
			script = f.read()
			try:
				# Set up connection
				self._conn = sqlite3.connect(DBPATH)
				# Set up cursor (with Row rowfactory option)
				self._conn.row_factory = sqlite3.Row
				self._cursor = self._conn.cursor()

				# Run the script given inside SCHEMAPATH
				self._cursor.executescript(script)
				self._conn.commit()

			except sqlite3.Error as e:
				print("Database failed to be created")
				print(e)
				# Remove the database file we tried to create 
				os.remove(DBPATH)
				return False

		return True


	# Connect to database given by DBPATH
	# Return True if success. False otherwise
	def connectToDB(self, DBPATH):

		try:
			# Set up connection
			self._conn = sqlite3.connect(DBPATH)
			# Set up cursor with Row rowfactory option
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
		# Until and "Y" or "N" response is given, keep looping
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
		# Delete database object (which also closes DB by its destructor)
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
			id = input("ID: ")
			pwd = getpass("Password: ") 

			# Try logging in as customer
			try:
				# See if a customer with given input id exists in customers table
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
				# Go into customer menu
				newMenu = CustomerMenu(self._db, id, row["name"])
				newMenu.start()
				break

			# Try logging in as editor
			try:
				# Check if an editor with given input id is in editors table
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
				# Go into editor menu
				newMenu = EditorMenu(self._db, id)
				newMenu.start()
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
				cursor.execute("""
						SELECT 1 FROM editors 
						WHERE UPPER(eid) = UPPER(:id) LIMIT 1
						""", { "id": id } )
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
				cursor.execute("""
						SELECT 1 FROM customers 
						WHERE UPPER(cid) = UPPER(:id) LIMIT 1
						""", { "id": id} )
				res = cursor.fetchone()
			except sqlite3.Error as e:
				print("Something went wrong with sqlite3")
				print(e)
				print()
				return

			# If id is taken by customer then give a try again prompt
			if res != None:
				print("Invalid ID. Try again?")
				resp = self.getUserYesOrNo()
				if resp:
					continue
				else:
					break

			# At this point, ID should be good to go
			try:
				# Insert the new customer information to DB
				cursor.execute("INSERT INTO customers VALUES(?, ?, ?)", (id, name, pwd))
				conn.commit()
			except sqlite3.Error as e:
				print("Could not add your registration information")
				print(e)
				print()
				return

			print("Successfully registered.")
			print()
			newMenu = CustomerMenu(self._db, id, name)
			newMenu.start()
			break

		return


# This is our CustomerMenu class.
# It encapsulates login information of the customer and
# has various methods related to the Customer
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

			if resp == "1":
				# Do start session stuff
				print("Starting a session")
				self.startSession()
			elif resp == "2":
				# Do search movie stuff
				self.search4movies()
			elif resp == "3":
				# Do end movie stuff
				print()
				self.endWatchMovie()
			elif resp == "4":
				# Do end session stuff
				print()
				self.endSession()
			elif resp == "5":
				print("Logging out")
				self.endSession()
				return
			elif resp == "6":
				print("Exiting program")
				print("Ending session")
				self.endSession()
				self.closeProgram()
			else:
				input("Invalid selection. Try again...")
				continue

	def search4movies(self):
		#Prompt user and get results
		print("---Searching for a movie---")
		user_input = str(input("Search for a movie: "))
		# Query for movies with the given user_input
		movieResults = self.getSearchResults(user_input)
		
		if len(movieResults) == 0:
			input("No matches. Enter anything to continue ")
			return
		
		movieIndex = 0
		
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()
		
		while True:
			# Print out movie choices
			print("---Page "+ str(int(movieIndex/4)+1) +" search results for '" +user_input +"'---\n")
			x = 0
			while x < 5:
				try:
					cursor.execute("""SELECT year, runtime FROM movies WHERE mid = :mid2;""",{'mid2' : movieResults[movieIndex+x][0]})
					movie_details = cursor.fetchone()
					print("    " + str(movieResults[movieIndex+x][1]) + " ("+ str(movie_details[0])+") "+" ("+ str(movie_details[1])+" minutes) - " + str(x+1))
				except IndexError:
					break
				x += 1
			
			# Print out other choices
			print("\nSee more matches? - " + str(x+1))
			print("See previous matches? - " + str(x+2))
			print("Exit? - "+ str(x+3))
				
			resp = str(input("\nYour selection: ")).strip()
				
			# Response is see more matches
			if resp == str(x+1):
				if movieIndex + 5 < len(movieResults):
					movieIndex += 5
				else:
				 input("No more matches. Enter anything to continue")
			# Response is exit
			elif resp == str(x+3):
				break
			# Response is previous matches
			elif resp == str(x+2):
				if movieIndex - 5 >= 0:
					movieIndex -= 5
				else:
					input("You've reached the starting page. Enter anything to continue")
			# Movie is selected
			elif resp >= '1' and resp <= str(x):
				#get movie details
				cursor.execute("""SELECT year, runtime FROM movies WHERE mid = :mid2;""", {'mid2': movieResults[movieIndex+int(resp)-1] [0]})
				yrAndRt = cursor.fetchone()
				cursor.execute("""SELECT c.pid, p.name FROM casts c, moviePeople p WHERE c.mid = :mid2 AND c.pid = p.pid;""", {'mid2' : movieResults[movieIndex+int(resp)-1] [0]})
				castsIdAndName = cursor.fetchall()
				cursor.execute("""WITH customerd AS (SELECT DISTINCT c.cid FROM customers c, watch w WHERE w.cid = c.cid AND w.mid = :mid2) SELECT COUNT(*) FROM customerd;""", {'mid2': movieResults[movieIndex+int(resp)-1] [0]})
				views = cursor.fetchone()
					
				while True:
					#print movie details and cast member choices
					print("---"+ str(movieResults[movieIndex+int(resp)-1] [1])+"---")
					print("Views: "+ str(views[0]))
					print("Year of release: "+ str(yrAndRt[0]))
					print("Runtime: " + str(yrAndRt[1]) + " minutes")
					print("Cast members: \n")
					y = 1	
					for x in castsIdAndName:
						print("    " + x[1] + " - " + str(y))
						y+=1
					#print other choices
					print("\nWatch movie? - " + str(y))
					print("Exit? - " + str(y+1))
					resp2 = str(input("\nYour Selection: "))
						
					#response is watch the movie
					if resp2 == str(y):
						if self._sid == None:
							input("You cannot watch this movie because you have not started a session.")
						else:
							if self._mid != None:
								cursor.execute("""SELECT title FROM movies WHERE mid = :mid2;""", {'mid2' : self._mid})
								p = cursor.fetchone()
								print("You have stopped watching " + p[0]+" and ", end ="")
							self.startWatchMovie(movieResults[movieIndex+int(resp)-1] [0])
							input("You have started watching "+ movieResults[movieIndex+int(resp)-1] [1] + ". Enter anything to continue ")  
					# response is exit
					elif resp2 == str(y+1):
						break
					#response is follow a movie person
					elif resp2 >= '1' and resp2 < str(y):
						try:
							cursor.execute("""INSERT INTO follows VALUES (?,?);""", (self._id, castsIdAndName[int(resp2)-1][0]))
							conn.commit()
							input("You followed " + castsIdAndName[int(resp2)-1][1] + ". Enter anything to continue ")
						except sqlite3.IntegrityError:
							input("You are already following this person. Enter anything to continue ")
					else:
						input("Invalid Input. Enter anything to continue ")

	#Prompts a user for movie keywords and
	#returns a list of all movies ordered by number of matches
	#Output_format: list of tuples of the form (mid, title, numberofmatches)
	def getSearchResults(self, movie_input):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

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
						WHERE UPPER(title) LIKE '%'||:x||'%'
						OR EXISTS ( SELECT * FROM casts c, moviePeople p WHERE movies.mid = c.mid AND p.pid = c.pid AND UPPER(p.name) LIKE '%'||:x||'%')
						OR EXISTS ( SELECT * FROM casts c WHERE movies.mid = c.mid AND UPPER(c.role) LIKE '%'||:x||'%');""",{'x' : x.upper()})

		#select and order results
		cursor.execute("""SELECT mid, title, runtime
					FROM movies
					WHERE runtime > 0
					ORDER BY runtime DESC;""")
		rows = cursor.fetchall()
		conn.rollback()
		return rows
	
	# Prompts a user to start a session
	def startSession(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		# Get a new session id by setting it as MAX(sid) + 1 
		cursor.execute("SELECT MAX(sid) FROM sessions")
		max_id = cursor.fetchone()[0]
		if max_id == None:
			new_id = 1
		else:
			new_id = int(max_id) + 1

		# Start a session if a session isn't going on (self._sid == None)
		if self._sid == None:
			# Get sdate and session start datetime 
			session_date = datetime.date.today()
			session_start_time = datetime.datetime.now()
			
			cursor.execute("""INSERT INTO sessions VALUES (?,?,?,NULL);""", (new_id, self._id, session_date))
			
			# Set object private variables
			self._sid = new_id
			self._sidStart = session_start_time
			print("Session started successfully")
			conn.commit()
		# Otherwise, return
		else:
			print("There is already a session running")
	
	# Prompts a user to end a session and end a moviebeing watched in the session
	def endSession(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		# Check if a session is not running
		if self._sid == None:
			# If no session is running currently then return
			print("No session is running currently")
			return

		# Check if a movie is being currently watched
		if self._mid != None:
		
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
				watchMins = runtime
			else:
				print("You are currently watching " + mtitle)
				print("Do you want to stop watching it and end the session?")
				resp = self.getUserYesOrNo()
				# If reply is no then return    
				if not resp:
					print("Going back to main menu")
					return

			# End watching movie
			cursor.execute('''
					UPDATE watch 
					SET duration = :watchtime 
					WHERE mid = :mid AND sid = :sid AND UPPER(cid) = UPPER(:cid)
					''', {"mid":self._mid, "sid":self._sid, "cid":self._id, "watchtime":watchMins})
			# Update object private variables
			self._mid = None
			self._midStart = None
			conn.commit()

		# Find minutes of the session
		sessionTime = datetime.datetime.now() - self._sidStart
		sessionMins = sessionTime.total_seconds() // 60

		# End session
		cursor.execute('''
				UPDATE sessions 
				SET duration = :sessiontime 
				WHERE sid = :sid AND UPPER(cid) = UPPER(:cid)
				''', {"sid":self._sid, "cid":self._id, "sessiontime":sessionMins})
		# Update object private variables
		self._sid = None
		self._sidStart = None
		print("Your session has now ended")
		conn.commit()
		return


	# Start watching a movie with given mid (also end watching a movie if there is one being watched)
	def startWatchMovie(self, mid):
		# Get cursor and conn object
		cursor = self._db.getCursor()
		conn = self._db.getConn()

		# Since one movie can be watched at a time, stop watching the current movie
		if self._mid != None:
			# Stop watching the movie
			# Get difference in minutes
			diffTime = datetime.datetime.now() - self._midStart
			watchMins = diffTime.total_seconds() // 60

			# Get runtime of movie watching
			cursor.execute('''
					SELECT runtime
					FROM movies
					WHERE mid = :mid
					''', {"mid":self._mid})
			row = cursor.fetchone()

			# If watchtime exceeds runtime then set watchtime to be runtime
			if watchMins > row["runtime"]:
				watchMins = runtime

			# End watching movie
			cursor.execute('''
					UPDATE watch
					SET duration = :watchtime
					WHERE mid = :mid AND sid = :sid AND UPPER(cid) = UPPER(:cid)
					''', {"mid":self._mid, "sid":self._sid, "cid":self._id, "watchtime":watchMins})
			self._mid = None
			self._midStart = None
			# Commit after we start watching a movie

		# Now watch a movie
		# If in the same session, the movie has been watched then...
		# Idk, the assignment spec did not cover this.
		# Since there is no mention of continuing where you left off at
		# I will just start the movie from begining..

		cursor.execute("""
				SELECT * FROM watch 
				WHERE sid = :sid AND UPPER(cid) = UPPER(:cid) AND mid = :mid
				""", {"sid":self._sid, "cid":self._id, "mid":mid})
		# If the movie has already been watched in the same session...
		if len(cursor.fetchall()) != 0:
			# Then set the watch duration to be NULL
			cursor.execute("""
					UPDATE watch
					SET duration = NULL
					WHERE sid = :sid AND UPPER(cid) = UPPER(:cid) AND mid = :mid
					""", {"sid":self._sid, "cid":self._id, "mid":mid})
		else:
			# Otherwise we add in a new row to watch table with NULL duration
			cursor.execute("INSERT INTO watch VALUES (?, ?, ?, NULL)", (self._sid, self._id, mid))
		
		conn.commit()
		self._mid = mid
		self._midStart = datetime.datetime.now()
		return


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
				WHERE mid = :mid AND sid = :sid AND UPPER(cid) = UPPER(:cid)
				''', {"mid":self._mid, "sid":self._sid, "cid":self._id, "watchtime":watchMins})
		# Update object private vars
		self._mid = None
		self._midStart = None
		conn.commit()
		return


# The EditorMenu class stores functions 
# that is related to editors
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

			if resp == "1":
				# Do add movie stuff
				print("--- Add a movie ---")
				self.addaMovie()
			elif resp == "2":
				# Do update recommends stuff
				print()
				self.updateRecommends()
			elif resp == "3":
				print("Logging out")
				return
			elif resp == "4":
				print("Exitting program")
				self.closeProgram()
			else:
				input("Invalid selection. Try again...")
				continue


	
	def updateRecommends(self):
		# Get type of report
		print("Select your date range")
		print("Monthly - 1")
		print("Annual - 2")
		print("All-Time - 3")
		resp = input("Type in your selection: ").strip()

		# Get appropriate data
		rept = None
		if resp == "1":
			rept = self.report("monthly")
		elif resp == "2":
			rept = self.report("annual")
		elif resp == "3":
			rept = self.report("alltime")
		else:
			print("Invalid response")
			return

		# If there is no report then return
		if len(rept) == 0:
			print("Empty report")
			return

		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		# Print out the data along with indices
		index = 1
		for row in rept:
			rowString = str(index) + ". "
			rowString += str(row["count"]) + " Customers watched mid " + str(row["mid1"]) + " "
			rowString += "also watched mid " + str(row["mid2"])
			# If row is in recommendations list then get its score
			if row["indic"] == 1:
				rowString += " IN recommendations list score "
				# Get score
				cursor.execute("""
						SELECT score 
						FROM recommendations 
						WHERE watched = :wid AND recommended = :rid
						""", { "wid":row["mid1"], "rid":row["mid2"]})
				score = cursor.fetchone()["score"]
				rowString += str(score)
			# Otherwise dont have to get the score
			elif row["indic"] == None:
				rowString += " NOT in recommendations list"
			
			print(rowString)
			index += 1
	

		while True:
			# Ask for the user to choose an index
			print("Select a pair by its index")
			try:
				selected = int(input("Type in the index here ").strip())
			except ValueError:
				print("Please give an integer")
				continue

			# If index given is invalid then say invalid
			if selected < 1 or selected >= index:
				print("Invalid index. Try again?")
				resp = self.getUserYesOrNo()
				if not resp:
					print("Leaving")
					return
				continue
			# Get data of the selected row
			row = rept[selected-1]
			
			# Ask the user what to do with it
			print("What would you like to do with it?")
			# Case : not in recommendation list
			if row["indic"] == None:
				while True:
					print("Add to recommendations list - 1")
					print("Back - 2")
					resp = input("Type in your selection: ")
					
					if resp == "1":
					
						# Get score
						print("What score will you give it? ")
						score = ""
						while True:
							try:
								score = float(input("Input score here: ").strip())
								break
							except ValueError:
								print("Please give an float value")
								continue
	
						# Insert into database
						cursor.execute("INSERT INTO recommendations VALUES(?, ?, ?)", 
								(row["mid1"], row["mid2"], score))
						conn.commit()
						print("Added to recommendation list")
						return
					elif resp == "2":
						break
					else:
						input("Please type a valid selection...")
						continue

			# Case : in recommendations list
			elif row["indic"] == 1:
				while True:
					print("Update score in recommendations list - 1")
					print("Remove from recommendations list - 2")
					print("Back - 3")
					resp = input("Type in your selection: ")

					if resp == "1":	
						# Get the score
						print("To what score will you update it to?")
						score = ""
						while True:
							try:
								score = float(input("Input score here: ").strip())
								break
							except ValueError:
								print("Please given a float value")
								continue
						# Now update it
						cursor.execute("""
								UPDATE recommendations SET score = :score 
								WHERE watched = :wid AND recommended = :rid
								""", {"score":score, "wid": row["mid1"], "rid": row["mid2"]})
						conn.commit()
						print("Updated the score")
						return

					elif resp == "2":
						# Delete from recommendations
						cursor.execute("""
								DELETE FROM recommendations
								WHERE watched = :wid AND recommended = :rid
								""", {"wid": row["mid1"], "rid": row["mid2"]})
						conn.commit()
						print("Removed from recommendations")
						return
					elif resp == "3":
						break
					else:
						input("Please type a valid selection...")
						continue

			

	#Returns a list of movie pairings and their respective number of customers
	#timerange = 'monthly','annual',or 'alltime'
	#Output_format: List of tuples of the form (mid, mid,number of customers, indicator = "None"(not in recommendations) or "1"(in recommendations))
	def report(self, timerange):

		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		# Check the time range given
		if timerange == 'monthly':
			datestring = { 'date' : (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d') }
		elif timerange == 'annual':
			datestring = { 'date' : (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d') }
		elif timerange == 'alltime':
			datestring = { 'date' : '' }
		else:
			raise Exception("report() function parameter invalid. It should be 'monthly', 'annual', or 'alltime'.")
			return

		cursor.execute("""
				WITH watched AS 
					(SELECT w.sid, w.cid, w.mid 
					FROM watch w, movies m 
					WHERE w.mid = m.mid AND (w.duration + w.duration) >= m.runtime),
				watchedwithrange AS 
					(SELECT DISTINCT w.mid, w.cid 
					 FROM watched w, sessions s 
					 WHERE w.sid = s.sid AND s.sdate >= :date),
				pairings AS 
					(SELECT w1.mid AS mid1, w2.mid as mid2, COUNT(*) AS count 
					 FROM watchedwithrange w1, watchedwithrange w2 
					 WHERE w1.cid = w2.cid AND w1.mid != w2.mid 
					 GROUP BY w1.mid, w2.mid 
					 ORDER BY count DESC),
				pairingswithindic AS 
					( SELECT mid1, mid2, count, (1) as indic 
					  FROM pairings 
					  WHERE EXISTS( 
						  SELECT * FROM recommendations 
						  WHERE pairings.mid1 = watched AND pairings.mid2 = recommended
						)
					)
				SELECT mid1, mid2, count, indic 
				FROM pairings left outer join pairingswithindic 
				using (mid1,mid2,count);""", datestring);
		p = cursor.fetchall()
		conn.rollback()
		return p

	#Prompts for movie details and cast members and adds them to the database if granted by the user
	def addaMovie(self):
		# Get cursor and conn objects
		conn = self._db.getConn()
		cursor = self._db.getCursor()

		while True:
			try:
				movie_id = int(input("Enter the movie id: "))
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
			# Ask for valid cast id 
			while True:
				try:
					cast_id = int(input("Enter cast id: "))
				except ValueError:
					print('Invalid Input. Try again.')
					continue
				else:
					break

			# Get cast person information
			cursor.execute("""
					SELECT m.name, m.birthyear 
					FROM casts c, moviePeople m 
					WHERE c.pid = m.pid AND UPPER(c.pid) = UPPER(:cast_id);
					""", {'cast_id' : cast_id })
			person = cursor.fetchall()

			# If cast person does not exist, add to database
			if len(person) == 0:
				print("The person does not exist in the database. Adding to database...")
				try:
					name = str(input("Enter name of person: " ))
					birthyear = int(input("Enter birthyear: " ))
				except ValueError:
					print("Invalid Input. Try again.")
					continue
				else:
					role = str(input("Enter the role: "))
					cursor.execute("""INSERT INTO moviePeople VALUES (?,?,?);""", (cast_id, name, birthyear))
					cursor.execute("""INSERT INTO casts VALUES (?,?,?);""", (movie_id, cast_id, role))
			# Cast person exists
			else:
				# Print cast person basic info
				print('Name:' + str(person[0][0]) + '\nBirthYear: ' + str(person[0][1]))
				
				# Add role to cast person in movie with given mid
				print("Provide role for this person ? ")
				if self.getUserYesOrNo() == 1:
					role = str(input("Enter the role: " ))
					cursor.execute("""INSERT INTO casts VALUES (?,?,?);""", (movie_id, cast_id, role))
			print("Add more cast members ?")
			if self.getUserYesOrNo() == 0:
				break
		print("Save movie in the database ?")
		if self.getUserYesOrNo() == 1:
			conn.commit()
			return
		conn.rollback()
	

	
def main():
	# Get commandline arguments
	if len(sys.argv) < 3:
		print("Insufficient number of arguments. Please provide database path name and schema path name")
		return
	elif len(sys.argv) > 3:
		print("Too many arguments")
		return

	# Get our file paths
	DBPATH = sys.argv[1]
	SCHEMAPATH = sys.argv[2]

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
