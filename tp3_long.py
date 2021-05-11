#######################################################
# Term Project
#
# term_project.py
# Name: Jiayi Wang
# Andrew ID: jiayiwan
#######################################################

from cmu_112_graphics import *
import math

# File I/O - Cited from course website
# URL: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO

# read from the file
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

# write to the file - does not keep the original content
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

# keep track of the task name, ddl, and the most recent 5 weeks of performance
class Task(object):
    # name of the task, deadline, and four previous hours spent on the task
    def __init__(self,name,ddlDay,ddlHour,mode1,mode2,curTime,prevTime):
        self.name = name
        self.ddlDay = ddlDay
        self.ddlHour = ddlHour
        self.mode1 = mode1
        self.mode2 = mode2
        self.curTime = curTime
        self.prevTime = prevTime
    
    # shfit current raw time and previous EMA time
    def shiftTime(self,newTime):
        multiplier = 2/(1+4)
        prevTime = self.prevTime*(1-multiplier) + self.curTime*multiplier
        self.prevTime = int(prevTime)
        self.curTime = newTime
    
    def __gt__(self,other):
        # check if the task is earlier than the compared task
        if self.ddlDay > other.ddlDay:
            return True
        elif self.ddlDay == other.ddlDay and self.ddlHour > other.ddlHour:
            return True
        return False
    
    def toggle(self,mode):
        if mode == 'mode1':
            if self.mode1 == 'normal': self.mode1 = 'diff'
            elif self.mode1 == 'diff': self.mode1 = 'vdiff'
            elif self.mode1 == 'vdiff': self.mode1 = 'ediff'
            elif self.mode1 == 'ediff': self.mode1 = 'normal'
        elif mode == 'mode2':
            if self.mode2 == 'normal': self.mode2 = 'imp'
            elif self.mode2 == 'imp': self.mode2 = 'vimp'
            elif self.mode2 == 'vimp': self.mode2 = 'eimp'
            elif self.mode2 == 'eimp': self.mode2 = 'normal'

# will change to use decorator if worked later
memoizeDict = dict()
#######################################################
# main
####################################################### 

def appStarted(app):
    # set to start page for the user to select the next step
    app.mode = 'startMode'
    #writeFile('term1.txt','task1,2,7,diff,normal,360,240;task2,5,12,normal,imp
    # ,195,376') - uncommeted for initalizing value if didn't save correct value
    app.colorList = getColor()
    # three week calendars drawn in display mode
    app.cursor = 0
    app.stress = 'normal'
    readInfo(app)
    app.calendarwk1 = getEmptyCalendar()
    app.calendarwk2 = getEmptyCalendar()
    app.calendarwk3 = getEmptyCalendar()
    # check if there is a valid calendar, stop computation if not
    app.nocalendar = True
    curCalendar = newCalendar(app,app.calendar1)
    if checkCalendar(app,curCalendar,1):
        curCalendar = newCalendar(app,app.calendar2)
        if checkCalendar(app,curCalendar,2):
            curCalendar = newCalendar(app,app.calendar3)
            checkCalendar(app,curCalendar,3)
    
    app.hour = getHour(app) # keep track of total hour of workload
    app.image = None # image to download
    app.scrollX = 0
    app.custMessage = 'Click on calendar to make one-time event!'
    app.feedbackMessage = 'Click on cells to give feedback!'
    app.press = None # keep track of the pressed cell
    app.release = None # keep track of the realeased cell
    app.clicked = False # check whether a task is clicked
    app.message = None # display the task message - if exist, task object
    
    getBackground(app)
    getIcon(app)
    getDialogBox(app)

# get app object for dialog box
def getDialogBox(app):
    # Taken from website
    # URL: http://3png.com/a-15893221.html
    app.dialogbox1 = app.loadImage('dialogbox.png')
    # Idea of RGBA originated from website beow, but all the lines of code is 
    # entirely written by myself with no reference to other codes
    # URL: https://stackoverflow.com/questions/61619658/rgba-image-not-showing
    # -up-with-pillow-and-tkinter
    app.dialogbox1 = app.dialogbox1.convert('RGBA')
    for x in range(app.dialogbox1.width):
        for y in range(app.dialogbox1.height):
            r, g, b, a = app.dialogbox1.getpixel((x,y))
            if not ((r<60 and g<60 and b<60) or (r>250 and g>250 and b>250)):
                app.dialogbox1.putpixel((x,y),(r,g,b,0))
    app.dialogbox1 = app.scaleImage(app.dialogbox1,2/3)
    # dialog box for diaplayMode
    app.dialogbox2 = app.scaleImage(app.dialogbox1,2/3)
    app.dialogbox2 = app.dialogbox2.transpose(Image.FLIP_LEFT_RIGHT)
    # dialog box for customizeMode
    app.dialogbox3 = app.scaleImage(app.dialogbox1,2/3)

# get app object for the background
def getBackground(app):
    # usual backgrounds
    # Downloaded from website
    # URL: https://www.freepik.com/free-photo/hand-painted-watercolor-background
    # -with-sky-clouds-shape_9728603.htm#page=1&query=background&position=0
    image = app.loadImage('background1.png')
    app.background1 = app.scaleImage(image, 7/4)
    # the one transparent at certain location
    app.background2 = app.scaleImage(image, 7/4)
    app.background2 = app.background2.convert('RGBA')
    for x in range(app.background2.width):
        for y in range(app.background2.height):
            r,g,b,a = app.background2.getpixel((x,y))
            if (587<=x<938) and (160<=y<675):
                app.background2.putpixel((x,y),(r,g,b,0))
            else:
                app.background2.putpixel((x,y),(r,g,b,255))
          
# get app object for the icon
def getIcon(app):
    # Artist name: Yiyuan Tang
    app.icon = app.loadImage('icon1.png')
    app.icon1 = getImage(app,1)
    app.icon2 = getImage(app,2)
    app.icon3 = getImage(app,3)

# read info from files
def readInfo(app):
    info = readFile('setting.txt')
    app.cursor, app.stress = convertFile(info)
    content = readFile('term1.txt')
    app.taskList = convertOOP(content)
    content1 = readFile('term1cal1.txt')
    app.calendar1 = convertStrToCal(content1)
    content2 = readFile('term1cal2.txt')
    app.calendar2 = convertStrToCal(content2)
    content3 = readFile('term1cal3.txt')
    app.calendar3 = convertStrToCal(content3)

def convertFile(s):
    L = s.split(',')
    if len(L) != 2:
        return (0, 'normal')
    cursor = int(L[0])
    stress = L[1]
    return (cursor, stress)

def getEmptyCalendar():
    result = [['']*7 for _ in range(24)]
    return result

# get the current hours occupied by tasks
def getHour(app):
    result = 0
    for task in app.taskList:
        hour = getHourNum(task.curTime,task.prevTime)
        result += hour
    return result

# get a list of TKinter color
def getColor():
    colorList = ['medium aquamarine','olive drab','tomato','sandy brown',
        'pale violet red','medium slate blue','cadet blue','hot pink',
        'thistle','khaki','navajo white','cyan','bisque','plum','tan']
    return colorList
    
# take in the string and assign information to Task class, return with a list
def convertOOP(s):
    result = []
    if s == '': return result
    instanceList = s.split(';')
    for i in range(len(instanceList)):
        item = instanceList[i]
        newList = item.split(',')
        name = newList[0]
        ddlDay = int(newList[1])
        ddlHour = int(newList[2])
        mode1 = newList[3]
        mode2 = newList[4]
        curTime = int(newList[5])
        prevTime = int(newList[6])
        curTask = Task(name,ddlDay,ddlHour,mode1,mode2,curTime,prevTime)
        result.append(curTask)
    return result
    
def convertDay(app,s):
    s1={'Monday','Tuesday','Wednesday','Thursday','Friday'}
    if not s in s1:
        app.showMessage('ddlDay is not a valid number')
    elif s == 'Monday': return 2
    elif s == 'Tuesday': return 3
    elif s == 'Wednesday': return 4
    elif s == 'Thursday': return 5
    elif s == 'Friday': return 6
    return None

#######################################################
# start mode
#######################################################

def startMode_mousePressed(app,event):
    if (app.width/4 <= event.x < app.width*3/4):
        if app.height*7/16 <= event.y < app.height*9/16:
            #choose to make a weekly calendar
            app.mode = 'inputMode'
        elif app.height/2 <= event.y < app.height*3/4:
            #choose to give a feedback
            app.mode = 'feedbackMode'
        elif app.height*3/4 <= event.y < app.height:
            #choose to view the current schedule
            app.mode = 'displayMode'
    # if click on INTRODUCTION button, go to intro page
    elif (app.width-100<=event.x<app.width-20 and app.height//4-50<=event.y
            <app.height//4-15):
        app.mode = 'introMode'
    # if click on SETTINGS button, go to settings page
    elif (app.width-100<=event.x<app.width-20 and app.height//4<=event.y
            <app.height//4+35):
        app.mode = 'settingsMode'

def startMode_redrawAll(app,canvas):
    drawBackground1(app,canvas)
    drawDialogBox1(app,canvas)
    drawText(app,canvas)
    drawIcon(app,canvas,1)
    drawSettings(app,canvas)
    drawPage(app,canvas)
    drawIntroductionButton(app,canvas)
    drawProducer(app,canvas)

def drawProducer(app,canvas):
    producer = 'Produced by Jiayi Wang'
    canvas.create_text(app.width-10,app.height-25,text = producer,
                        anchor = 'se')
    '''
    If you could see it, thanks so much for all the help you've provided
    through the TP season!! You are the best mentor :)'''
    contributor = 'Many Great Ideas Contributed by Winston Zha'
    canvas.create_text(app.width-10,app.height-10,text = contributor,
                        anchor = 'se') 

def drawDialogBox1(app,canvas):
    canvas.create_image(100,100,image=ImageTk.PhotoImage(app.dialogbox1))

# draw icon
def drawIcon(app,canvas,size):
    if size == 1:
        canvas.create_image(app.width*2/3,150,
                            image=ImageTk.PhotoImage(app.icon1))
    elif size == 2:
        canvas.create_image(app.width/6,115,image=ImageTk.PhotoImage(app.icon2))
    else:
        canvas.create_image(app.width-50,115,
                            image=ImageTk.PhotoImage(app.icon3))

# get the color of the background if pixel of icon is almost white
def getImage(app,num):
    image1 = app.icon.convert('RGBA')
    image2 = app.background1.convert('RGBA')
    for x in range(image1.width):
        for y in range(image1.height):
            r,g,b,a = image1.getpixel((x,y))
            if (r>250 and g>250 and b>250):
                image1.putpixel((x,y),(r,g,b,0))
            else:
                image1.putpixel((x,y),(r,g,b,255))
    if num == 1:
        image1 = app.scaleImage(image1,1/2)
    elif num == 2:
        image1 = app.scaleImage(image1,1/4)
        image1 = image1.transpose(Image.FLIP_LEFT_RIGHT)
    elif num == 3:
        image1 = app.scaleImage(image1,1/4)
    return image1

def drawBackground1(app,canvas):
    canvas.create_image(300,350,image=ImageTk.PhotoImage(app.background1))
    
def drawIntroductionButton(app,canvas):
    canvas.create_rectangle(app.width-100,app.height//4-50,app.width-20,
                        app.height//4-15, fill = 'sandy brown')
    canvas.create_text(app.width-60, app.height//4-20, text = 'Introduction',
                    font = f'Arial 10 bold', anchor='s')

def drawSettings(app,canvas):
    canvas.create_rectangle(app.width-100,app.height//4, app.width-20,
                        app.height//4+35, fill = 'steelBlue4')
    canvas.create_text(app.width-60,app.height//4+30, text = 'Settings',
                    font = f'Arial 10 bold', anchor='s')

def drawText(app,canvas):
    text = '''\
Hello, welcome to 
Weekly Scheduling!'''
    canvas.create_text(20, app.height//10-10,text = text, 
                        font = f'Arial 18 bold',anchor = 'nw')
    hintText = 'click below to choose mode'
    canvas.create_text(20, app.height//5-10, text = hintText,
                        font = f'Arial 18', anchor = 'nw')

def drawPage(app,canvas):
    text = 'New Task'
    canvas.create_oval(app.width/4,app.height*7/16,app.width*3/4,
                        app.height*9/16, fill = 'lightSkyBlue2', width = 2)
    canvas.create_text(app.width//2, app.height//2, text = text,
                        font = f'Arial 15 bold')

    text = 'Feedback'
    canvas.create_oval(app.width/4,app.height*10/16,app.width*3/4,
                        app.height*12/16, fill = 'lightSkyBlue2', width = 2)
    canvas.create_text(app.width//2, app.height*11/16, text = text,
                        font = f'Arial 15 bold')

    text = 'Calendar'
    canvas.create_oval(app.width/4,app.height*13/16,app.width*3/4,
                        app.height*15/16, fill = 'lightSkyBlue2', width = 2)
    canvas.create_text(app.width//2, app.height*14/16, text = text,
                        font = f'Arial 15 bold')

#######################################################
# settings mode
#######################################################
def settingsMode_mousePressed(app,event):
    # if click on 'Back', go back to start page
    if (app.width-50<=event.x<app.width-10) and (10<=event.y<40):
        app.mode = 'startMode'
    elif (100<=event.x<200) and (220<=event.y<260):
        app.stress = 'normal'
    elif (250<=event.x<350) and (220<=event.y<260):
        app.stress = 'morning'
    elif (400<=event.x<500) and (220<=event.y<260):
        app.stress = 'night'
    # if click on 'Save', save the current app.taskList to file
    elif (10<=event.x<50) and (10<=event.y<40):
        app.showMessage('Nice! Save is successful, please wait :)')
        content = convertInfo(app)
        writeFile('setting.txt',content)
    
# convert the setting information into string
def convertInfo(app):
    cursor = str(app.cursor)
    stressMode = app.stress
    L = [cursor,stressMode]
    result = ','.join(L)
    return result

def settingsMode_redrawAll(app,canvas):
    drawBackground1(app,canvas)
    canvas.create_text(app.width//2,50,text = 'Settings',
                        fill = 'brown', font = f'Arial 30 bold')
    drawBack(app,canvas)
    drawSave(app,canvas)
    drawStressMode(app,canvas)
    drawMealTime(app,canvas)

def settingsMode_mouseReleased(app,event):
    if 400<=event.y<500:
        if 100<=event.x<200:
            app.cursor = 0
        elif 200<=event.x<300:
            app.cursor = 1
        elif 300<=event.x<400:
            app.cursor = 2
        elif 400<=event.x<500:
            app.cursor = 3

# draw meal time selection in setting mode
def drawMealTime(app,canvas):
    canvas.create_text(50,350,text = '* Click below to select meal time',
                        anchor = 'nw', font = f'Arial 15 bold')
    canvas.create_line(150,450,450,450,width = 4)
    canvas.create_oval(130,440,150,460,fill = 'black')
    canvas.create_oval(450,440,470,460,fill = 'black')
    pos = app.cursor*100+150
    canvas.create_line(pos,430,pos,470,fill = 'blue',width = 2)
    canvas.create_text(150,500,text = '0',font = f'Arial 10')
    canvas.create_text(250,500,text = '1')
    canvas.create_text(350,500,text = '2')
    canvas.create_text(450,500,text = '3')
    canvas.create_text(130,500,text = 'Hour(s)',anchor = 'ne')

# draw morning/night person in setting mode
def drawStressMode(app,canvas):
    canvas.create_text(50,150,text='* Click below to select your preference',
                        anchor = 'nw', font = f'Arial 15 bold')
    color = 'deepSkyBlue2'
    if app.stress == 'normal': color = 'dodgerBlue4'
    canvas.create_rectangle(100,220,200,260,fill=color)
    canvas.create_text(150,240,text='Normal',font=f'Arial 15')
    color = 'deepSkyBlue2'
    if app.stress == 'morning': color = 'dodgerBlue4'
    canvas.create_rectangle(250,220,350,260,fill=color)
    canvas.create_text(300,240,text='Morning',font=f'Arial 15')
    color = 'deepSkyBlue2'
    if app.stress == 'night': color = 'dodgerBlue4'
    canvas.create_rectangle(400,220,500,260,fill=color)
    canvas.create_text(450,240,text='Night',font=f'Arial 15')

#######################################################
# introduction mode
#######################################################

def introMode_mousePressed(app,event):
    if (app.width-50<=event.x<app.width-10) and (10<=event.y<40):
        app.mode = 'startMode'

def introMode_redrawAll(app,canvas):
    drawBackground1(app,canvas)
    canvas.create_text(app.width//2,50,text = 'Introduction', 
                        fill ='brown', font = f'Arial 30 bold')
    drawBack(app,canvas)
    drawIntroduction(app,canvas)

def drawIntroduction(app,canvas):
    text = readFile('instruction.txt')
    canvas.create_text(app.width//2,70,text = text, font = f'Arial 8 bold',
                        anchor = 'n')

#######################################################
# input schedule mode
#######################################################

# Exponential Moving Average Formula - formula cited from website
# URL: https://www.investopedia.com/terms/e/ema.asp
# get the number of hours of a task
def getHourNum(curTime,prevTime):
    size = 4
    multiplier = 2/(size+1)
    result = curTime*multiplier + prevTime*(1-multiplier)
    hourRatio = 1/60
    return math.ceil(result*hourRatio)

def inputMode_mousePressed(app,event):
    # if click on 'Back', back to start mode
    if (app.width-50<=event.x<app.width-10) and (10<=event.y<40):
        app.showMessage('Remember to save your change!')
        reply = app.getUserInput('Enter upper case YES to go back')
        if reply == 'YES':
            app.mode = 'startMode'
    # if click on 'Delete', let the user delete the task
    elif (app.width-60<=event.x<app.width-10) and (50<=event.y<80):
        deleteTask(app)
    # if click on 'Create', create new task
    elif (10<=event.x<60) and (50<=event.y<80):
        if len(app.taskList) > 15:
            app.showMessage('You have too much tasks')
            return
        getNewTask(app)
    # if click on 'Save', save the current app.taskList to file
    elif (10<=event.x<50) and (10<=event.y<40):
        app.showMessage('Nice! Save is successful, please wait :)')
        writeInfo(app)
        curCalendar = newCalendar(app,app.calendar1)
        if not checkCalendar(app,curCalendar,1):
            app.nocalendar = True
            return
        curCalendar = newCalendar(app,app.calendar2)
        if not checkCalendar(app,curCalendar,2):
            app.nocalendar = True
            return
        curCalendar = newCalendar(app,app.calendar3)
        if not checkCalendar(app,curCalendar,3):
            app.nocalendar = True
            return
        app.showMessage('Check for your new calendar now!')
    # if click on 'Customize', go to customizing calendar
    elif (app.width-100<=event.x<app.width-20) and (app.height//4-50<=event.y
            <app.height//4-15):
        app.mode = 'customizeMode'

# write all necessary current information into different files - storage
def writeInfo(app):
    content = convertString(app.taskList)
    writeFile('term1.txt',content)
    content1 = convertCalToStr(app.calendar1)
    writeFile('term1cal1.txt',content1)
    content2 = convertCalToStr(app.calendar2)
    writeFile('term1cal2.txt',content2)
    content3 = convertCalToStr(app.calendar3)
    writeFile('term1cal3.txt',content3)

# check if calendar is valid and assign app calendar
def checkCalendar(app,calendar,num):
    if calendar == None:
        app.nocalendar = True
        app.showMessage('No valid plan, please try to change your schedule')
        return False
    else:
        app.nocalendar = False
        if num == 1:
            app.calendarwk1 = calendar
        elif num == 2:
            app.calendarwk2 = calendar
        elif num == 3:
            app.calendarwk3 = calendar
        return True

def inputMode_redrawAll(app,canvas):
    drawBackground1(app,canvas)
    canvas.create_text(app.width//2,app.height//20,text = 'New Task',
                    font=f'Arial 20 bold')
    drawTask(app,canvas)
    drawBack(app,canvas)
    drawDelete(app,canvas)
    drawSave(app,canvas)
    drawCreate(app,canvas)
    drawCustomize(app,canvas)

def drawCustomize(app,canvas):
    canvas.create_rectangle(app.width-100,app.height//4-50,app.width-20,
                        app.height//4-15, fill = 'wheat')
    canvas.create_text(app.width-60, app.height//4-20, text = 'Customize',
                    font = f'Arial 10 bold', anchor='s')

def drawCreate(app,canvas):
    canvas.create_rectangle(10,50,60,80, fill = 'sandy brown')
    canvas.create_text(35,65, text = 'Create', font = f'Arial 10 bold')

def drawSave(app,canvas):
    canvas.create_rectangle(10,10,50,40, fill = 'bisque2')
    canvas.create_text(30,25,text = 'Save', font = f'Arial 10 bold')

def drawDelete(app,canvas):
    canvas.create_rectangle(app.width-60,50,app.width-10,80, 
                            fill = 'DarkSeaGreen3')
    canvas.create_text(app.width-35,65,text = 'Delete', font = f'Arial 10 bold')

def drawTask(app,canvas):
    r = 5
    offSet = app.height//4
    for i in range(len(app.taskList)):
        color = app.colorList[i]
        sortedList = sortedTaskList(app)
        task = sortedList[i]
        canvas.create_oval(app.width//10-r,app.height//20*i+offSet,
                app.width//10+r,app.height//20*i+2*r+offSet, fill = color)
        ddlDay = convertStrDay(task.ddlDay)
        hour = getHourNum(task.curTime,task.prevTime)
        text = f'Task: {task.name}'
        canvas.create_text(app.width//10+2*r,app.height//20*i+offSet,text=text,
                        font = f'Arial 8 bold', anchor = 'nw', fill = color)
        text = f"Deadline: {ddlDay} {task.ddlHour} o'clock"
        canvas.create_text(app.width//10+150,app.height//20*i+offSet,text=text,
                        font = f'Arial 8 bold', anchor = 'nw', fill = color)
        text = f'Workload: {hour} hour'
        if hour != 1:
            text += 's'
        canvas.create_text(app.width//10+350,app.height//20*i+offSet,text=text,
                        font = f'Arial 8 bold', anchor = 'nw', fill = color)

def drawBack(app,canvas):
    canvas.create_rectangle(app.width-50, 10, app.width-10, 40, 
                        fill = 'skyBlue2')
    canvas.create_text(app.width-30,25,text = 'Back',font = f'Arial 10 bold')

# check if the name is valid
def isValidName(name):
    if name == None: return False
    # name does not contain comma or semicolon
    nameSet = set(name)
    if ',' in nameSet or ';' in nameSet:
        return False
    # name does not contain period - used for denoting empty in calendar
    elif '.' in nameSet: return False
    # name cannot contain what separates the string in memoization
    elif '@#$%^' in name:
        return False
    return True

# get a new task obeject
def getNewTask(app):
    while True:
        name = app.getUserInput('Enter your task name')
        if name == None: return
        if isValidName(name): break
        else: app.showMessage('Invalid name, please try again :)')

    dayText = "Enter the day of deadline (Ex. 'Monday')"
    while True:
        ddlDay = app.getUserInput(dayText)
        if ddlDay == None: return
        if isValidDay(ddlDay):
            ddlDay = convertDay(app,ddlDay)
            break
        else:
            app.showMessage('Invalid day, please try again :)')

    hourText = 'Enter (1-24) the hour of deadline'
    while True:
        deadlineHour = app.getUserInput(hourText)
        if deadlineHour == None: return
        if isValidHour(deadlineHour):
            ddlHour = int(deadlineHour)
            break
        else:
            app.showMessage("Invalid hour, please try again:)")

    # the workload serves as the first EMA(y-1)
    while True:
        workload = app.getUserInput('Enter (in minutes) the predicted workload')
        if workload == None: return
        if isValidWorkload(app,workload):
            break
        else:
            app.showMessage("Invalid workload, please try again:)")
    
    # difficult & important are 'normal' by default
    mode1 = 'normal'
    mode2 = 'normal'
    task = Task(name,ddlDay,ddlHour,mode1,mode2,int(workload),int(workload))
    if not pseudoIn(task, app.taskList):
        app.taskList.append(task)
        app.hour = getHour(app)
    elif pseudoIn(task,app.taskList):
        app.showMessage('You already used this name, please try again :)')

# check if the input is valid to interpret
def isValidDay(s):
    s1={'Monday','Tuesday','Wednesday','Thursday','Friday'}
    if s in s1:
        return True
    return False

# check if the input is valid to interpret
def isValidHour(s):
    if s == None: return False
    # if cannot convert to integer, return False
    if not s.isdigit(): return False
    hour = int(s)
    # if the hour is between 1 and 24, inclusively, return True
    if 0<hour<=24: return True
    return False

def isValidWorkload(app,s):
    if s == None: return False
    #check if input can be interpreted
    if not s.isdigit():
        app.showMessage('Invalid workload, please try again :)')
        return False
    curHour = math.ceil(int(s)/60)
    # if exceeds 70 hours per week, do not take more
    if app.hour+curHour > 70: 
        app.showMessage('You have exceeded the maximum workload per week!')
        return False
    return True

# delete the task instance with the input name
def deleteTask(app):
    deleteName = app.getUserInput('Enter a task name to delete')
    for task in app.taskList:
        if task.name == deleteName:
            app.taskList.remove(task)
            return
    if deleteName == None or deleteName == '':
        app.showMessage('You did not enter anything~')
        return
    app.showMessage('No such task exists')

# convert the list of OOP object into a string for file storing
def convertString(L):
    result=''
    for task in L:
        curList = [task.name,str(task.ddlDay),str(task.ddlHour),task.mode1,
                task.mode2,str(task.curTime),str(task.prevTime)]
        curStr = ",".join(curList)
        result += curStr + ";"
    result = result.strip(';')
    return result

def convertStrDay(n):
    if n < 0 or n >= 7:
        app.showMessage('You have invalid day information')
    elif n == 0: return 'Saturday'
    elif n == 1: return 'Sunday'
    elif n == 2: return 'Monday'
    elif n == 3: return 'Tuesday'
    elif n == 4: return 'Wednesday'
    elif n == 5: return 'Thursday'
    elif n == 6: return 'Friday'

#######################################################
# customize future three weeks of calendar
#######################################################

def customizeMode_keyPressed(app,event):
    if event.key == 'Right':
        if app.scrollX > -700:
            app.scrollX -= 10
    elif event.key == 'Left':
        if app.scrollX < 0:
            app.scrollX += 10

def customizeMode_mousePressed(app,event):
    app.custMessage = 'Click on calendar to make one-time event!'
    # if click on 'Back', back to input mode
    if (app.width-50<=event.x<app.width-10) and (10<=event.y<40):
        app.mode = 'inputMode'
    # if click on task
    elif (200<=event.x<550) and (200<=event.y<680):
        if not clickCalendar(app,event,200,200,'press'):
            if not clickCalendar(app,event,550,200,'press'):
                clickCalendar(app,event,900,200,'press')

def customizeMode_mouseReleased(app,event):
    # if click on 'Clear'
    if 10<=event.x<160:
        if 300<=event.y<350:
            clearWeekCalendar(app,'1')
        elif 375<=event.y<425:
            clearWeekCalendar(app,'2')
        elif 450<=event.y<500:
            clearWeekCalendar(app,'3')
        elif 525<=event.y<575:
            clearWeekCalendar(app,'ALL')
    elif (200<=event.x<550) and (200<=event.y<680):
        if not clickCalendar(app,event,200,200,'release'):
            if not clickCalendar(app,event,550,200,'release'):
                clickCalendar(app,event,900,200,'release')

# clear week calendar
def clearWeekCalendar(app,num):
    if num == '1' or num =='ALL':
        app.calendar1 = getEmptyCalendar()
    if num == '2' or num == 'ALL':
        app.calendar2 = getEmptyCalendar()
    if num == '3' or num == 'ALL':
        app.calendar3 = getEmptyCalendar() 

# click on calendar cells, make new tasks (events)
def clickCalendar(app,event,xStart,yStart,mode):
    cellWidth = 50
    cellHeight = 20
    for row in range(24):
        for col in range(7):
            x1 = xStart+cellWidth*col+app.scrollX
            x2 = x1+cellWidth
            y1 = yStart+cellHeight*row
            y2 = y1+cellHeight
            if (x1 <= event.x < x2) and (y1 <= event.y < y2):
                if mode == 'press':
                    if xStart == 200:
                        app.press = (row,col,app.calendar1)
                    elif xStart == 550:
                        app.press = (row,col,app.calendar2)
                    else:
                        app.press = (row,col,app.calendar3)
                elif mode == 'release':
                    app.release = (row,col)
                    if xStart == 200:
                        app.release = (row,col,app.calendar1)
                    elif xStart == 550:
                        app.release = (row,col,app.calendar2)
                    else:
                        app.release = (row,col,app.calendar3)
                    makeTask(app)
                return True

# make task based on mousePressed and mouseReleased
def makeTask(app):
    rowStart,colStart,cal1 = app.press
    rowStop,colStop,cal2 = app.release
    if cal1 != cal2:
        app.showMessage('Cannot make task across weeks!')
        return
    changeCalendar(app,rowStart,colStart,rowStop,colStop,cal1)

# check if the internal of the clicks already has tasks
def isValidClick(app,rowStart,colStart,rowStop,colStop,calendar):
    for col in range(colStart,colStop+1):
        for row in range(24):
            if col == colStart and row < rowStart:
                pass
            elif col == colStop and row > rowStop:
                pass
            else:
                if calendar[row][col] != '':
                    app.custMessage = 'This time period already has tasks'
                    return False
    return True

# convert a calendar to write into a string for file storage
def convertCalToStr(calendar):
    result = ''
    for row in range(24):
        curResult = ''
        for col in range(7):
            task = calendar[row][col]
            if task == '':
                curResult += '.' + ','
            else:
                curResult += task.name + ','
        curResult = curResult.strip(',')
        result += curResult + ';'
    result = result.strip(';')
    return result

#convert a calendar-string back to the calendar with same task name info
def convertStrToCal(calendar):
    result = []
    rows = calendar.split(';')
    for item in rows:
        cells = item.split(',')
        for i in range(len(cells)):
            cell = cells[i]
            if cell == '.':
                cells[i] = ''
            else:
                cells[i] = makeNewTask(cell)
        result.append(cells)
    return result

# make a new task based on the name wanted for the task
def makeNewTask(cell):
    ddlDay = 7
    ddlHour = 24
    mode1 = 'normal'
    mode2 = 'normal'
    curTime = 0
    prevTime = 0
    task = Task(cell,ddlDay,ddlHour,mode1,mode2,curTime,prevTime)
    return task

def deleteEvent(app):
    if not app.press == app.release:
        return
    else:
        row, col, calendar = app.press
        task = calendar[row][col]
        text = f'''\
The current event is: ({task.name})
enter YES if you want to delete this event'''
        confirm = app.getUserInput(text)
        if confirm != 'YES':
            return
        for i in range(24):
            for j in range(7):
                item = calendar[i][j]
                if isinstance(item,Task) and item.name == task.name:
                    calendar[i][j] = ''

# add tasks for the desired cell and calendar
def changeCalendar(app,rowStart,colStart,rowStop,colStop,calendar):
    if not isValidClick(app,rowStart,colStart,rowStop,colStop,calendar):
        deleteEvent(app)
        return
    while True:
        name = app.getUserInput('Enter the task name')
        if isValidName(name): break
        elif name == None: return
        else: app.showMessage('Invalid task name, please try again :)')
    # these information does not really matter, assign a value for OOP
    ddlDay, ddlHour = 7, 24
    mode1 = mode2 = 'normal'
    curTime = prevTime = 0
    task = Task(name,ddlDay,ddlHour,mode1,mode2,curTime,prevTime)
    if isInCalendar(app,task):
        app.showMessage('This event name is already used, please try again :)')
        return
    for i in range(24):
        for j in range(7):
            if isValidCell(rowStart,colStart,rowStop,colStop,i,j):
                calendar[i][j] = task

# check if the name already used in the calendars:
def isInCalendar(app,task):
    for row in range(24):
        for col in range(7):
            item1 = app.calendar1[row][col]
            item2 = app.calendar2[row][col]
            item3 = app.calendar3[row][col]
            if item1 != '':
                if task.name == item1.name: return True
            if item2 != '':
                if task.name == item2.name: return True
            if item3 != '':
                if task.name == item3.name: return True
    return False

# check if the cell is valid 
def isValidCell(rowStart,colStart,rowStop,colStop,i,j):
    if j < colStart or j >colStop: return False
    elif j == colStart and i < rowStart: return False
    elif j == colStop and i > rowStop: return False
    return True
     
def customizeMode_redrawAll(app,canvas):
    drawCustCal(app,canvas)
    drawBackground2(app,canvas)
    drawIcon(app,canvas,2)
    canvas.create_line(200,200,200,680)
    canvas.create_line(550,200,550,680)
    drawHour(app,canvas,200,200)
    drawBack(app,canvas)
    drawClear(app,canvas)
    drawDialogBox2(app,canvas)
    drawCustMessage(app,canvas)

def drawCustMessage(app,canvas):
    canvas.create_text(app.width//2,60,text=app.custMessage,
                        font = f'Arial 10 bold')

def drawDialogBox2(app,canvas):
    canvas.create_image(300,50,image = ImageTk.PhotoImage(app.dialogbox2))

def drawClear(app,canvas):
    canvas.create_rectangle(10,300,160,350,fill = 'peach puff')
    canvas.create_text(85,325,text = 'Clear Week 1', font = f'Arial 10 bold')
    canvas.create_rectangle(10,375,160,425,fill = 'peach puff')
    canvas.create_text(85,400,text = 'Clear Week 2', font = f'Arial 10 bold')
    canvas.create_rectangle(10,450,160,500,fill = 'peach puff')
    canvas.create_text(85,475,text = 'Clear Week 3', font = f'Arial 10 bold')
    canvas.create_rectangle(10,525,160,575,fill = 'peach puff')
    canvas.create_text(85,550,text = 'Clear ALL', font = f'Arial 10 bold')

def drawCustCal(app,canvas):
    #draw the three connected calendar together
    drawCell(app,canvas,200,200,app.calendar1)
    drawDay(app,canvas,205,200)
    canvas.create_text(375+app.scrollX,180,text='Week 1',font = 'Arial 10 bold')
    drawCell(app,canvas,550,200,app.calendar2)
    drawDay(app,canvas,555,200)
    canvas.create_text(725+app.scrollX,180,text='Week 2',font = 'Arial 10 bold')
    drawCell(app,canvas,900,200,app.calendar3)
    drawDay(app,canvas,905,200)
    canvas.create_text(1025+app.scrollX,180,text='Week 3',font='Arial 10 bold')

#######################################################
# input performance feedback mode
#######################################################

def feedbackMode_mousePressed(app,event):
    # if click on 'Back', back to start mode
    if (app.width-50<=event.x<app.width-10) and (10<=event.y<40):
        app.showMessage('Remember to save your change!')
        reply = app.getUserInput('Enter upper case YES to go back')
        if reply == 'YES':
            app.mode = 'startMode'
    # if click on 'Save', save the current app.taskList to file
    elif (10<=event.x<50) and (10<=event.y<40):
        app.showMessage('Nice! Save is successful, please wait :)')
        shiftWeek(app)
        writeInfo(app)
        curCalendar = newCalendar(app,app.calendar1)
        if not checkCalendar(app,curCalendar,1):
            return
        curCalendar = newCalendar(app,app.calendar2)
        if not checkCalendar(app,curCalendar,2):
            return
        curCalendar = newCalendar(app,app.calendar3)
        if not checkCalendar(app,curCalendar,3):
            return
        app.feedbackMessage = 'Check for your new calendar now!'
    checkClickTask(app,event)
    checkClickCell(app,event)

# shift week once feedback made in the feedback mode
def shiftWeek(app):
    app.calendar1 = app.calendar2
    app.calendar2 = app.calendar3
    app.calendar3 = getEmptyCalendar()

# check which cell is clicked on
def checkClickCell(app,event):
    offSet = app.height//4
    sortedList = sortedTaskList(app)
    for i in range(len(sortedList)):
        if (offSet+app.height//20*i)<=event.y<(offSet+app.height//20*(i+1)):
            task = sortedList[i]
            # check if click on 'difficult'
            if 250<=event.x<400:
                task.toggle('mode1')
            # check if click on 'important'
            elif 400<=event.x<550:
                task.toggle('mode2')
            changeList(app,task)
            return
            
# check which task is clicked on
def checkClickTask(app,event):
    if event.x<50 or event.x>=200: return
    offSet = app.height//4
    sortedList = sortedTaskList(app)
    for i in range(len(sortedList)):
        if (offSet+app.height//20*i)<=event.y<(offSet+app.height//20*(i+1)):
            task = sortedList[i]
            changeParameter(app,task)
            app.hour = getHour(app)
            return

# changes curTime and give feedback on whether started late
def changeParameter(app,task):
    newWorkload = app.getUserInput('Enter (in minutes) your actual'+
                                ' workload this week')
    confirm = app.getUserInput('Enter YES to confirm giving this feedback')
    if confirm == 'YES':
        if newWorkload != None and newWorkload.isdigit():
            newWorkload = int(newWorkload)
            task.shiftTime(newWorkload)
            changeList(app,task)
            text = '''\
        Thanks for your feedback, 
        please do not make any repetitive feedback!'''
            app.feedbackMessage = text
        else:
            app.feedbackMessage = 'Invalid feedback, please try again :)'
    
# change the list content because task.curTime and task.prevTime changed
def changeList(app,task):
    for i in range(len(app.taskList)):
        item = app.taskList[i]
        if item.name == task.name:
            app.taskList[i] = task
            return

def feedbackMode_redrawAll(app,canvas):
    drawBackground1(app,canvas)
    drawIcon(app,canvas,3)
    drawDialogBox3(app,canvas)
    drawBack(app,canvas)
    drawSave(app,canvas)
    drawTaskName(app,canvas)
    drawFeedbackCell(app,canvas)
    canvas.create_text(app.width//2+50,50,text=app.feedbackMessage,
                    font=f'Arial 10 bold')
    
# draw the cells for feedback
def drawFeedbackCell(app,canvas):
    offSet = app.height//4
    canvas.create_text(325,offSet-10,text='Difficult',
                        font = f'Arial 15 bold')
    canvas.create_text(475,offSet-10,text='Important',
                        font = f'Arial 15 bold')
    sortedList = sortedTaskList(app)
    for i in range(len(sortedList)):
        task = sortedList[i]
        color = getMode1Color(task)
        canvas.create_rectangle(250,app.height//20*i+offSet,400,
                            app.height//20*(i+1)+offSet,fill=color)
        color = getMode2Color(task)
        canvas.create_rectangle(400,app.height//20*i+offSet,550,
                            app.height//20*(i+1)+offSet,fill=color)

# return the color of different mode
def getMode1Color(task):
    if task.mode1 == 'normal':
        return 'white'
    elif task.mode1 == 'diff':
        return 'rosy brown'
    elif task.mode1 == 'vdiff':
        return 'indian red'
    elif task.mode1 == 'ediff':
        return 'firebrick'

def getMode2Color(task):
    if task.mode2 == 'normal':
        return 'white'
    elif task.mode2 == 'imp':
        return 'light sky blue'
    elif task.mode2 == 'vimp':
        return 'dodger blue'
    elif task.mode2 == 'eimp':
        return 'blue4'

def drawTaskName(app,canvas):
    offSet = app.height//4
    canvas.create_text(125,offSet-10,text = 'Task List',
                        font = f'Arial 20 bold', anchor = 's')
    sortedList = sortedTaskList(app)
    for i in range(len(sortedList)):
        task = sortedList[i]
        color = app.colorList[i]
        size = 8
        canvas.create_rectangle(50,app.height//20*i+offSet,200,
                            app.height//20*(i+1)+offSet, fill = color)
        canvas.create_text(125,app.height//20*(i+1/2)+offSet,
                        text=f'{task.name}', font = f'Arial {size} bold')

#######################################################
# display new schedule mode
#######################################################

def displayMode_mousePressed(app,event):
    app.clicked = False
    # if click on 'Back'
    if (app.width-50<=event.x<app.width-10) and (10<=event.y<40):
        app.mode = 'startMode'
    # if click on 'Download'
    elif (10<=event.x<85) and (10<=event.y<40):
        app.image = app.getSnapshot()
        app.saveSnapshot()
    # if click on tasks
    clickTask(app,event)
    clickCell(app,event,200,200)
    clickCell(app,event,550,200)
    clickCell(app,event,900,200)

# if click on certain cell, show message
def clickCell(app,event,xStart,yStart):
    # ignore all click outside the calendar
    if not (200<=event.x<550 and 200<=event.y<680):
        return
    #locate the cell
    cellWidth = 50
    cellHeight = 20
    for row in range(24):
        for col in range(7):
            x1 = xStart+cellWidth*col+app.scrollX
            x2 = x1+cellWidth
            y1 = yStart+cellHeight*row
            y2 = y1+cellHeight
            # if click on the cell
            if (x1 <= event.x < x2) and (y1 <= event.y < y2):
                if xStart == 200:
                    task = app.calendarwk1[row][col]
                elif xStart == 550:
                    task = app.calendarwk2[row][col]
                else:
                    task = app.calendarwk3[row][col]
                if task == '': return
                else:
                    app.clicked = True
                    app.message = task

# show corresponding message if click on task
def clickTask(app,event):
    if event.x<10 or event.x>=160: return
    offSet = app.height//4 + 30
    sortedList = sortedTaskList(app)
    for i in range(len(sortedList)):
        if (offSet+app.height//25*i)<=event.y<(offSet+app.height//25*(i+1)):
            task = sortedList[i]
            # other functions to show message
            return

# find the best valid calendar, return None if no valid calendar found
def newCalendar(app,calendar):
    sortedList = sortedTaskList(app)
    result = helperCalendar(app,0,0,sortedList,calendar)
    #delete information after each run because task information may change
    memoizeDict.clear()
    return result

# convert the arguements into a new string
def convertKey(row,col,L):
    result = ''
    # use something to separate each argument
    result += '@#$%^' + str(row)
    result += '@#$%^' + str(col)
    listStr = convertString(L)
    result += '@#$%^' + listStr
    return result

'''
# pseudo-code: my basic ideas
def helperCalendar(app,startRow,startCol,taskIndex):
    # check memoization
    if args in memoizeDict, return value
    # base case
    if the index is the last one
    return the drawing of the best solution by looping over all valid ones
    # return None if no valid solution exists

    #recursive case
    find the current task within sorted list
    find the deadline of the task
    from start of the task, draw the board for workload-many cells
    find the best solution to the next level
    merge them and return the best current calendar
'''

# recursive helper function that finds the best calendar
def helperCalendar(app,startRow,startCol,sortedList,calendar):
    # convert the argument into string
    checkKey = convertKey(startRow,startCol,sortedList)
    # if the result already in memoizeDict, return result
    if checkKey in memoizeDict: return memoizeDict[checkKey]
    # if nothing in the list
    if len(sortedList) == 0:
        return None
    task = sortedList[0]
    # find the deadline of a task
    rowStop = task.ddlHour
    colStop = task.ddlDay
    # find the hour of a task
    hour = getHourNum(task.curTime,task.prevTime)
    # base case - if at the last task
    if len(sortedList) == 1:
        result = baseBestCalendar(app,startRow,startCol,rowStop,colStop,hour,
        task,calendar)
        if result == None: return None
        result = mergeCalendar(calendar,result)
        return result
    else:
        result = recursiveBestCalendar(app, startRow,startCol,rowStop,colStop,
        hour, task,sortedList,checkKey,calendar)
        return result

def baseBestCalendar(app,startRow,startCol,rowStop,colStop,hour,task,calendar):
    # find the best solution
    bestSol = None
    for col in range(startCol,7):
        for row in range(24):
            if isValidCalendar(app,row,col,startRow,startCol,rowStop,colStop,
                                hour,calendar):
                # make the current calendar
                curCalendar = makeCalendar(app,row,col,hour,task,calendar)
                if curCalendar == None: break
                if app.stress == 'normal':
                    curStress = calculateStress(curCalendar)
                elif app.stress == 'morning':
                    curStress = calculateStressMorning(curCalendar)
                elif app.stress == 'night':
                    curStress = calculateStressNight(curCalendar)
                curDis = calculateDistribution(curCalendar)
                # if no solution existed
                if bestSol == None:
                    bestSol = curCalendar
                    stress = curStress
                    dis = curDis
                elif curStress < stress:
                    bestSol = curCalendar
                    stress = curStress
                    dis = curDis
                elif stress == curStress and curDis <= dis:
                    bestSol = curCalendar
                    dis = curDis                     
                    stress = curStress      
    return bestSol

# get the current information
def getCur(app,curCalendar,rest):
    curResult = mergeCalendar(curCalendar,rest)
    if app.stress == 'normal':
        curStress = calculateStress(curResult)
    elif app.stress == 'morning':
        curStress = calculateStress(curResult)
    elif app.stress == 'night':
        curStress = calculateStress(curResult)
    curDis = calculateDistribution(curResult)
    return curResult,curStress,curDis

def recursiveBestCalendar(app,startRow,startCol,rowStop,colStop,hour,task,
                            sortedList,checkKey,calendar):
    # recursive case
    bestSol = None
    for col in range(startCol,7):
        for row in range(24):
            if not (isValidCalendar(app,row,col,startRow,startCol,
            rowStop,colStop,hour,calendar)):
                pass
            else:
                # current task calendar
                curCalendar = makeCalendar(app,row,col,hour,task,calendar)
                if curCalendar == None: break
                # rest tasks calendar
                newRow, newCol = getNextStart(app,row,col,hour,calendar)
                rest = helperCalendar(app,newRow,newCol,sortedList[1:],
                                        calendar)
                # merge two calendar together
                if rest == None: pass
                else:
                    curResult, curStress, curDis = getCur(app,curCalendar,rest)
                    # keep tarck of best solution
                    if bestSol == None:
                        bestSol = curResult
                        stress = curStress
                        dis = curDis
                    elif curStress < stress:
                        bestSol = curResult
                        stress = curStress
                        dis = curDis
                    elif stress == curStress and curDis <= dis:
                        bestSol = curResult
                        dis = curDis
                        stress = curStress              
    # add bestSol to memoizeDict
    memoizeDict[checkKey] = bestSol
    # return best solution
    return bestSol

# make a calendar, given task to fill in and start row and col
def makeCalendar(app,row,col,hour,task,calendar):
    result = [['']*7 for _ in range(24)]
    # start from row and col
    curRow, curCol = row, col
    while hour > 0:
        if calendar[curRow][curCol] == '':
            if app.cursor == 0:
                result[curRow][curCol] = task
                hour -= 1
            elif (app.cursor == 1) and (not curRow == 11):
                result[curRow][curCol] = task
                hour -= 1
            elif (app.cursor == 2) and not (curRow == 11 or curRow == 12):
                result[curRow][curCol] = task
                hour -= 1
            elif (app.cursor == 3) and not (curRow == 11 or curRow == 12 or
                                            curRow == 13):
                result[curRow][curCol] = task
                hour -= 1
        if 0 <= curRow < 23:
            curRow += 1
        elif curRow == 23:
            curCol += 1
            curRow = 0
    return result

def mergeCalendar(L1,L2):
    result = [['']*7 for _ in range(24)]
    for row in range(24):
        for col in range(7):
            # if L1 at this index is not empty, put into result
            if L1[row][col] != '':
                result[row][col] = L1[row][col]
            # if L2 at this index is not empty, put into result
            elif L2[row][col] != '':
                result[row][col] = L2[row][col]
    return result

# check if the strat is valid
def isValidCalendar(app,row,col,startRow,startCol,rowStop,colStop,hour,
                    calendar):
    # if early than the startRow and startCol
    if col < startCol:
        return False
    elif col == startCol and row < startRow:
        return False
    stopRow, stopCol = getStop(app,row,col,hour,calendar)
    if stopRow == -1: return False
    if stopCol > colStop:
        return False
    elif stopCol == colStop and stopRow >= rowStop:
        return False
    return True

# calculates the stop of the task, given a determined calendar
def getStop(app,row,col,hour,calendar):
    while hour > 0:
        if not (0<=row<24 and 0<=col<7):
            return (-1,-1)
            app.showMessage('Your row and col starting index wrong')
        # if no task in the pre-determined calendar
        if calendar[row][col] == '':
            if app.cursor == 0:
                hour -= 1
            elif (app.cursor == 1) and (not row == 11):
                hour -= 1
            elif (app.cursor == 2) and not (row == 11 or row == 12):
                hour -= 1
            elif (app.cursor == 3) and not (row == 11 or row == 12 or
                                            row == 13):
                hour -= 1
        if 0 <= row < 23:
            row += 1
        elif row == 23:
            col += 1
            row = 0
    return (row,col)

# find the earliest possible start of the next task
def getNextStart(app,row,col,hour,calendar):
    curRow,curCol = getStop(app,row,col,hour,calendar)
    if not (0<=row<24 and 0<=col<7):
        app.showMessage('Your row and col starting index wrong')
    if 0 <= curRow < 23:
        curRow += 1
    elif curRow == 23:
        curCol += 1
        curRow = 0
    return (curRow, curCol) 

def sortedTaskList(app):
    newList = copy.deepcopy(app.taskList)
    mergeSort(newList)
    return newList

# quantify the stress of a list of calendar
def calculateStress(L):
    result = 0
    for i in range(24):
        for j in range(7):
            # if no work, skip this cell
            if L[i][j] == '': pass
            # if too early or too late, more stress
            elif i < 8 or i > 22:
                result += 40
            # if intermediate time, intermediate stress
            elif i < 10 or i > 18:
                result += 10
            # if appropriate time, less stress
            else:
                result += 5
    return result

def calculateStressMorning(L):
    result = 0
    for i in range(24):
        for j in range(7):
            if L[i][j] == '': pass
            elif i < 6 or i > 20:
                result += 40
            elif i < 8 or i > 16:
                result += 10
            else:
                result += 5
    return result

def calculateStressNight(L):
    result = 0
    for i in range(24):
        for j in range(7):
            if L[i][j] == '': pass
            elif i < 10 or i > 24:
                result += 40
            elif i < 12 or i > 22:
                result += 10
            else:
                result += 5
    return result
            
# quantify the distribution of work in a week - lower better
def calculateDistribution(L):
    totalWork = 0
    workList = []
    # find all working hour
    for i in range(24):
        todayWork = 0
        for j in range(7):
            if L[i][j] != '':
                totalWork += 1
                todayWork += 1
        workList.append(todayWork)
    day = 7
    avgWork = totalWork/day
    result = 0
    for item in workList:
        result += (item-avgWork)**2
    return result

#######################################################################
# merge and mergeSort - Cited from course website
# URL: https://www.cs.cmu.edu/~112/notes/notes-efficiency.html#sorting

def merge(a, start1, start2, end):
    index1 = start1
    index2 = start2
    length = end - start1
    aux = [None] * length
    for i in range(length):
        if ((index1 == start2) or
            ((index2 != end) and (a[index1] > a[index2]))):
            aux[i] = a[index2]
            index2 += 1
        else:
            aux[i] = a[index1]
            index1 += 1
    for i in range(start1, end):
        a[i] = aux[i - start1]
    return aux

def mergeSort(a):
    n = len(a)
    step = 1
    while (step < n):
        for start1 in range(0, n, 2*step):
            start2 = min(start1 + step, n)
            end = min(start1 + 2*step, n)
            merge(a, start1, start2, end)
        step *= 2
#####################################################################

def displayMode_keyPressed(app,event):
    if event.key == 'Right':
        if app.scrollX > -700:
            app.scrollX -= 10
    elif event.key == 'Left':
        if app.scrollX < 0:
            app.scrollX += 10

def displayMode_redrawAll(app,canvas):
    drawCalendar(app,canvas)
    drawBackground2(app,canvas)
    drawHour(app,canvas,200,200)
    drawBack(app,canvas)
    drawTaskList(app,canvas)
    drawDownload(app,canvas)
    drawIcon(app,canvas,3)
    drawDialogBox3(app,canvas)
    drawDisplayMessage(app,canvas)

def drawDialogBox3(app,canvas):
    canvas.create_image(350,50,image = ImageTk.PhotoImage(app.dialogbox3))

def drawBackground2(app,canvas):
    canvas.create_image(300,350,image=ImageTk.PhotoImage(app.background2))

# draw the message of the clicked cell
def drawDisplayMessage(app,canvas):
    if app.nocalendar:
        text = '''\
        No available calendar,
        please change your task schedule!'''
    elif not app.clicked:
        text = 'Click on the cell to see detailed information!'
    else:
        task = app.message
        if pseudoIn(task,app.taskList):
            name,mode1,mode2 = task.name,task.mode1,task.mode2
            text = makeText(app,1,name,mode1,mode2)
        elif task != '':
            name = task.name
            text = makeText(app,2,name)
    canvas.create_text(app.width//2+50,50,text=text,font=f'Arial 10 bold')

# return the text displayed when click on certain cell in calendar
def makeText(app,scenario,name,mode1 = 0,mode2 = 0):
    # if clicked on a weekly task
    if scenario == 1:
        text = f'You task name is: {name}!'
        if mode1 == 'diff':
            text += '\nThis task might be a little difficult.'
        elif mode1 == 'vdiff':
            text += '\nThis task is difficult.'
        elif mode1 == 'ediff':
            text += '\nGosh, this task is very difficult!'
        if mode2 == 'imp':
            text += '\nThis task is quite important.'
        elif mode2 == 'vimp':
            text += '\nThis task is really important.'
        elif mode2 == 'eimp':
            text += '\nWow, this task is super important!'
    # if clicked on a one-time event
    elif scenario == 2:
        text = f'Your event name is: {name}!'
    return text

def drawTaskList(app,canvas):
    offSet = app.height//4 + 30
    canvas.create_text(85,170,text = 'Task List',
                        font = f'Arial 20 bold')
    sortedList = sortedTaskList(app)
    for i in range(len(sortedList)):
        task = sortedList[i]
        color = app.colorList[i]
        size = 8
        canvas.create_rectangle(10,app.height//25*i+offSet,160,
                            app.height//25*(i+1)+offSet, fill = color)
        canvas.create_text(85,app.height//25*(i+1/2)+offSet,
                        text=f'{task.name}', font = f'Arial {size} bold')

def drawDownload(app,canvas):
    canvas.create_rectangle(10,10,85,40, fill = 'sandy brown')
    canvas.create_text(15,25,text = 'Download', font = f'Arial 10 bold',
                        anchor = 'w')
    
def drawCalendar(app,canvas):
    #draw the three connected calendar together
    drawCell(app,canvas,200,200,app.calendarwk1)
    drawDay(app,canvas,205,200)
    canvas.create_text(375+app.scrollX,180,text='Week 1',font = 'Arial 10 bold')
    drawCell(app,canvas,550,200,app.calendarwk2)
    drawDay(app,canvas,555,200)
    canvas.create_text(725+app.scrollX,180,text='Week 2',font = 'Arial 10 bold')
    drawCell(app,canvas,900,200,app.calendarwk3)
    drawDay(app,canvas,905,200)
    canvas.create_text(1025+app.scrollX,180,text='Week 3',font='Arial 10 bold')
    canvas.create_line(200,200,200,680)
    canvas.create_line(550,200,550,680)

# draw the day on top of the calendar
def drawDay(app,canvas,xStart,yStart):
    width = 50
    for i in range(7):
        dayList=['Sat','Sun','Mon','Tue','Wed','Thu','Fri']
        curDay = dayList[i]
        canvas.create_text(xStart+app.scrollX+width*i,yStart,text=curDay,
        font=f'Arial 10 bold', anchor = 'sw')

# draw the hour number on the left
def drawHour(app,canvas,xStart,yStart):
    height = 20
    for i in range(24):
        text = f'{i}:00'
        canvas.create_text(xStart,yStart+height*i,text=text,
                            font=f'Arial 10 bold',anchor= 'ne')
    
# draw individual hour cell of calendar
def drawCell(app,canvas,xStart,yStart,calendar):
    cellWidth = 50
    cellHeight = 20
    for i in range(24):
        for j in range(7):
            x1 = xStart+cellWidth*j+app.scrollX
            x2 = x1+cellWidth
            y1 = yStart+cellHeight*i
            y2 = y1+cellHeight
            task = calendar[i][j]
            if app.nocalendar and (calendar == app.calendarwk1 or
                calendar == app.calendarwk2 or calendar == app.calendarwk3):
                color = 'white'
                outline = 'black'
            elif task == '': 
                color = 'white'
                outline = 'black'
                x1 += 1
                x2 -= 1
                y1 += 1
                y2 -= 1
            else:
                x1 += 1/2
                x2 -= 1/2
                y1 += 1/2
                y2 -= 1/2
                if pseudoIn(task,app.taskList):
                    color = taskColor(app,task)
                    outline = color
                else:
                    outline = color = 'gray'
            canvas.create_rectangle(x1,y1,x2,y2,fill=color,
                        outline=outline)

# check if the task is in the task list
def pseudoIn(task,L):
    for  item in L:
        if item.name == task.name:
            return True
    return False

# get the corresponding color of a task
def taskColor(app,task):
    index = getIndex(app,task)
    return app.colorList[index]

# get the corresponding color index of a task
def getIndex(app,task):
    index = 0
    sortedList = sortedTaskList(app)
    for item in sortedList:
        if task.name == item.name:
            return index
        index += 1

#######################################################
runApp(width = 600, height = 700)