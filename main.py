import sqlite3
import os
import time
import datetime
from getpass import getpass

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
		resp = input("N or Y: ").strip().upper()
		if resp == "Y":
			return True
		elif resp == "N":
			return False
		else:
			input("Invalid response. Try again...")


def InitScreen():	

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
			loginScreen()
		elif resp == "2":
			print()
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


		# ---- Check if id is unique... ----

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
			resp = getUserYesOrNo()
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
			resp = getUserYesOrNo()
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
			print("Starting a session")
			startSession()
		elif resp == "2":
			# Do search movie stuff
			print()
		elif resp == "3":
			# Do end movie stuff
			print()
			endWatchMovie()
		elif resp == "4":
			# Do end session stuff
			print()
		elif resp == "5":
			print("Logging out")
			user_info["id"] = None
			user_info["name"] = None
			return
		elif resp == "6":
			print("Exiting program")
			closeProgram()
		else:
			input("Invalid selection. Try again...")
			continue

# FIXME: temp variables. unfortunately.
#mid = 110
#sid = 1
#cid = "c500"
#movieStart = datetime.datetime.now()

def endWatchMovie():
	# The clarifcation states that only one movie is watched at a time.
	# So we will not include the functionality 
	# "if multiple movie is being watched, you have the choice to select one"
	# Because it doesn't make sense. 
	#FIXME: remove global variables
	global mid, sid, cid, movieStart

	# Check if a movie is being currently watched
	if mid == None:
		# If no movies being watched then return
		print("No movie is being watched.")
		return
	
	# Find minutes watched
	diffTime = datetime.datetime.now() - movieStart
	watchMins = diffTime.total_seconds() // 60

	# Get runtime of movie (and also title)
	cursor.execute('''
			SELECT title, runtime 
			FROM movies
			WHERE mid = :mid
			''', {"mid":mid})
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
		resp = getUserYesOrNo()
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
	mid = None
	conn.commit()
	return






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

#Returns a list of movie pairings and their respective number of customers
#timerange = 'monthly','annual',or 'alltime'
#Output_format: List of tuples of the form (mid, mid,number of customers, indicator = "None"(not in recommendations) or "1"(in recommendations))
def report(timerange):
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
def search4movies():
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
def addaMovie():
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
	
# Prompts a user to start a session
def startSession():
	cursor = conn.cursor()
	cursor.execute("SELECT MAX(sid) FROM sessions")
	max_id = cursor.fetchone()[0]
	if max_id == None:
		new_id = 1
	else:
		new_id = int(max_id) + 1
	if user_info["session start time"] == None:
		session_date = datetime.date.today()
		session_start_time = time.time()
		cursor.execute("""INSERT INTO sessions VALUES (?,?,?,NULL);""", (new_id, user_info["id"], session_date))
		user_info["session start time"] = session_start_time
		print("Session started successfully")
		conn.commit()
	else:
		print("There is already a session running")
	
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
