import sqlite3
import os
import scraper

#Setup a database with a given name and SQL layout
#Returns created Database
def initDatabase(dataName, schemaName):
        path = os.path.dirname(dataName)
        if path != "" and not os.path.exists(path):
            os.mkdir(path)

        database = sqlite3.connect(dataName)
        schema = open(schemaName, 'r').read()
        database.executescript(schema)

        return database

#Add a date to assignments table or change it if it already exists
def addAssignment(database, path, name, date):
    script = """
            insert into assignments (path, fileName, date)
            values ("{}","{}","{}")
            ON CONFLICT(path) DO UPDATE
            SET date = "{}";
            """.format(path, name, date, date)

    database.executescript(script)
    database.commit()

#Change an already existing date in assignments table
#Likely can find a way to just use addAssignment()
#returns updated data for use in gui
def updateDate(database, path, date):
    script = """
            UPDATE assignments
            SET date="{}" WHERE path="{}"
            """.format(date, path)

    database.executescript(script)
    database.commit()
    return database.execute("""SELECT * FROM assignments WHERE path="{}" """.format(path)).fetchone()

#Adds all files labled TODO to database
def updateFiles(database):
    files = scraper.getTODOfiles(r"C:\Users\ULTRA\Documents\School")
    #Add any new TODO files to the database
    #Should remove old records too?
    for file in files:
        path = file[0];
        name = file[1];
        date = "Null"
        script = """SELECT date FROM assignments WHERE path="{}" """.format(path)

        c = database.execute(script)
        savedDate = c.fetchone()
        if str(savedDate) != "None":
            date = savedDate[0];
        addAssignment(database, path, name, date)

#Returns all data from assignments table
def getData(database):
    c = database.cursor()
    c.execute("SELECT * FROM assignments;")
    values = c.fetchall()
    return values;

#Gives the fileName and date associated with a path
def pathData(path, database):
    return database.execute("""SELECT fileName, date FROM assignments WHERE path="{}" """.format(path)).fetchone()
