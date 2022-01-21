import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkcalendar import DateEntry
import datetime
from datetime import date as dateString

import os

import dataEdit as de

hoverColor = "#abddff";
# leaveColor = "white";


selectedAssignment = None;
database = de.initDatabase("./usrData/database.db", "./SQL/schema.sql");
# database = de.initDatabase(":memory:", "schema.sql"); #For Testing

#Custom Classes Start
#Button Wrapper to save path with button
class tagButton(tk.Button):
    def __init__(self, master, tag=None, *args, **kwargs):
        tk.Button.__init__(self, master, *args, **kwargs)
        self.master, self.tag = master, tag
#DateEntry Wrapper to save path with DateEntry
class tagDate(DateEntry):
    def __init__(self, master, tag=None, **kwargs):
        DateEntry.__init__(self, master, **kwargs)
        self.master, self.tag = master, tag
#Custom Classes End

#Event Handlers Start
#Highlight on mouseOver
def onEnter(event):
    if(selectedAssignment != event.widget):
        event.widget['background'] = hoverColor
#Remove onEnter Highlight
def onExit(event):
    if(selectedAssignment != event.widget):
        event.widget['background'] = 'systemButtonFace'

#For DateEntry elements
def entryChange(entry, cal):
    oldDate = dateString.fromisoformat(de.pathData(entry.tag, database)[1])
    changeDate(cal, entry, entry.tag, oldDate, entry.get_date()) #
    pass

#For calendar day select
def calClick(cal, eventList):
    global selectedAssignment;
    selectedDate = cal.selection_get()

    #Clear eventList and add events if they exist
    eventList.delete(0, "end")
    eventIDs = cal.get_calevents(date=selectedDate)
    for i in range(0, len(eventIDs)):
        eventList.insert(i, cal.calevent_cget(eventIDs[i], "text"))
        print(eventList.index(i))

    if selectedAssignment is not None:
        dateEnt = selectedAssignment.master.children["!tagdate"];
        oldDate = dateEnt.get_date()

        changeDate(cal, dateEnt, selectedAssignment.tag, oldDate, selectedDate);
        selectedAssignment["background"] = "systemButtonFace";
        selectedAssignment = None;
        # cal.selection_set(selectedDate)

    pass

#For button assignment select
def selectAssignment(event):
    global selectedAssignment;
    button = event.widget;
    if selectedAssignment is not None:
        selectedAssignment["background"] = "systemButtonFace";
        if selectedAssignment == button:
            selectedAssignment = None;
            return;

    selectedAssignment = button
    button['background'] = hoverColor
#Event Handlers End

#Helper method that changes date information on the calendar and updates the database
def changeDate(cal, entry, path, oldDate, newDate):
    _, name, _ = de.updateDate(database, path, newDate);
    fileName = os.path.basename(path);

    if oldDate != "Null":
        eventIDs = cal.get_calevents(date=oldDate);
        toRemove = "Null"
        for ID in eventIDs:
            eventName = cal.calevent_cget(ID, "text");
            if(eventName == fileName):
                toRemove = ID
        cal.calevent_remove(toRemove, date=oldDate)

    cal.calevent_create(newDate, name, "file")
    entry.set_date(newDate)
    return

#Gives all buttons hoverColor change
def buttonSetup(button):
    button.bind("<Enter>", onEnter)
    button.bind("<Leave>", onExit)

#Handle double click on event list element
def eventOpen(e):
    list = e.widget;
    selection = list.curselection()
    # selection.
    pass

#Setup tkinter window
window = tk.Tk();
menuBar = tk.Menu(window)
# menuBar.add_command(label="Test", command=test)
window.config(menu=menuBar)
style = ttk.Style(window)
style.theme_use("winnative")
window.title("Data Scrape")
photo = tk.PhotoImage(file = "images/favicon.png")
window.iconphoto(False, photo)

#major frameCreation
frameFiles = tk.Frame(window);
frameCalendar = tk.Frame(window);
frameDayInfo = tk.Frame(window);

#frameDayInfo code start
tk.Label(master=frameDayInfo, text="Selected Day Info:").pack()
eventList = tk.Listbox(master=frameDayInfo, width="40")
eventList.bind("<Double-1>", (lambda e: eventOpen(e))) #os.startfile(path, "open")
eventList.pack()
#frameDayInfo code end

tk.Label(master = frameFiles, text = "Files Labled TODO:").pack()

#Get a current list of TODO files in folder structure
de.updateFiles(database)
data = de.getData(database)

#create Calendar
calendar = Calendar(frameCalendar, selectmode = 'day')
calendar.tag_config("file", background="green")

#create buttons and date selectors for each TODO file
for path, name, date in data:
    #Place everything for one file in same frame for easier management
    buttonFrame = tk.Frame(master=frameFiles);

    buttonSelect = tagButton(master=buttonFrame, text=name, tag=path)
    buttonSetup(buttonSelect)

    buttonSelect.bind("<Button-1>", (lambda e: selectAssignment(e)));
    buttonSelect.pack(side="left")

    buttonOpen = tk.Button(master = buttonFrame, text = "Open");
    buttonSetup(buttonOpen);
    buttonOpen.bind("<Button-1>", (lambda e, path=path: os.startfile(path, "open")));
    buttonOpen.pack(side="left");


    dateEnt = tagDate(master=buttonFrame, tag=path)

    if date != "Null":
        dateTimeObj = dateString.fromisoformat(date);
        dateEnt.set_date(dateTimeObj);
        calendar.calevent_create(dateTimeObj, name, "file")
    else:
        dateEnt.delete(0, "end");
    dateEnt.bind("<<DateEntrySelected>>", (lambda e, dateEnt=dateEnt : entryChange(dateEnt, calendar)))
    dateEnt.pack(side="right")
    buttonFrame.pack()


calendar.bind("<<CalendarSelected>>", (lambda e: calClick(calendar, eventList)))

tk.Label(master = frameCalendar, text = "Calendar:").pack()
calendar.pack()

#Pack completed frames
frameFiles.pack(side="left")
frameDayInfo.pack(side="right")
# frameCalendar.place(relx=.5, rely=.5, anchor="center")
frameCalendar.pack(side="right")

window.mainloop();
