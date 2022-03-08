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
		print("----- Initial Screen -----")
		print("Select your options")
		print("Login - 1")
		print("Register (as customer) - 2")
		print("Exit program - 3")
		# Call strip function to ignore spaces
		resp = str(input("Type in your selection: ")).strip()

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
		id = str(input("ID: ")).strip().upper()
		pwd = str(input("Password: ")).strip()
		
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
		id = str(input("Provide ID: ")).strip()
		name = str(input("Provide name: "))
		#FIXME: password must be not visible at time of typing
		pwd = str(input("Provide password: "))
		
		if len(pwd) < 1 or len(name) < 1 or len(id) < 1:
			input("Please input appropriate fields...")
			continue

		# First it cannot have the same id as an editor's
		try:
			cursor.execute("SELECT 1 FROM editors WHERE UPPER(eid) = UPPER(:id) LIMIT 1", { "id": id } )
			res = cursor.fetchone()
		except sqlite3.Error as e:
			print("Something went wrong with sqlite3")
			print(e)
			print()
			return

		# If id is already taken by an editor
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

#Returns a list of movie pairings and their respective number of customers
#timerange = 'monthly','annual',or 'alltime'
#Output_format: List of tuples of the form (mid, mid,number of customers, indicator = "0"(not in recommendations) or "1"(in recommendations))
def report(timerange):

    # make the watch table only have 'watched' movies
    cursor.execute("""CREATE TEMP TABLE watched AS SELECT w.sid, w.cid, w.mid FROM watch w, movies m WHERE w.mid = m.mid AND (w.duration + w.duration) >= m.runtime;""")

    # make the watch table only have values in the timerange
    if timerange == 'monthly':
        cursor.execute("""CREATE TEMP TABLE watchedwithrange AS SELECT DISTINCT w.mid, w.cid FROM watched w, sessions s WHERE w.sid = s.sid AND s.sdate >= date('now','-30 days');""")
    elif timerange == 'annual':
        cursor.execute("""CREATE TEMP TABLE watchedwithrange AS SELECT DISTINCT w.mid, w.cid FROM watched w, sessions s WHERE w.sid = s.sid AND s.sdate >= date('now','-365 days');""")
    elif timerange == 'alltime':
        cursor.execute("""CREATE TEMP TABLE watchedwithrange AS SELECT DISTINCT w.mid, w.cid FROM watched w, sessions s WHERE w.sid = s.sid;""")
    else:
        print("Invalid timerange.")
        return

    # for each customer, do the cartesian product of the movies they've watched and group them
    cursor.execute("""CREATE TEMP TABLE pairings AS SELECT w1.mid AS mid1, w2.mid as mid2, COUNT(*) AS count FROM watchedwithrange w1, watchedwithrange w2 WHERE w1.cid = w2.cid AND w1.mid != w2.mid GROUP BY w1.mid, w2.mid ORDER BY count DESC;""")
    
    #set up indicator column for each tuple
    cursor.execute("""ALTER TABLE pairings ADD indicator DEFAULT 0;""")
    cursor.execute("""UPDATE pairings SET indicator = 1 WHERE EXISTS( SELECT * FROM recommendations WHERE pairings.mid1 = watched AND pairings.mid2 = recommended);""")
    
    cursor.execute("""SELECT * FROM pairings;""")
    p = cursor.fetchall()
    return p
    conn.rollback()

#Prompts a user for movie keywords and
#returns a list of all movies ordered by number of matches
#Output_format: list of tuples of the form (mid, title, year, numberofmatches)
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
                        WHERE title LIKE '%'||:x||'%'""",{'x' : x})

        #select and order results
        cursor.execute("""SELECT *
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
