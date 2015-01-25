#!/usr/bin/python
import math, datetime, time, threading
import Adafruit_CharLCD as LCD

events = [('PhD Defense', '06/22/2015'),
          ('Cross Country Trip', '03/09/2015'),
          ('Cross Country Trip II', '06/23/2015')]
timeFormat = '%m/%d/%Y'

def calculateAndPrintMessage(tevent, lcd, eventName, eventDatetime, timeFormat):
    '''Calculates and prints the number of days and hours from the current date
    to the date of the event.

    ::param tevent::        Event object used to signal and stop the current 
                            process externally.
    ::param lcd::           LCD object for displaying information.
    ::param eventName::     Name of the event.
    ::param eventDatetime:: Date and time of the event.
    ::param timeFormat::    Format of the time stamp listed with the event.
    '''
    while not tevent.isSet():
        print("Event: " + eventName)
        lcd.clear()
        nowDatetime = datetime.datetime.today()
        futureDatetime = datetime.datetime.strptime(eventDatetime, timeFormat)
        delta = futureDatetime - nowDatetime
        days = delta.days
        hours = delta.seconds / 3600	

        message = eventName + " in\n"
        countdownStatement = ''
        if days is 1:
            countdownStatement = countdownStatement + "{0} day "
        else:
            countdownStatement = countdownStatement + "{0} days "

        if hours is 1:
            countdownStatement = countdownStatement + "{1} hour"
        else:
            countdownStatement = countdownStatement + "{1} hours"

        countdownStatement = countdownStatement.format(days, hours)
        message = message + countdownStatement
        lcd.message(message)

        if lcd._cols < len(eventName) or lcd._cols < len(countdownStatement):
            maxLen = max(len(eventName), len(countdownStatement))
            scrollMessage(lcd, lcd._cols, maxLen)
        tevent.wait(60)

def scrollMessage(lcd, lcd_columns, length):
    '''Scrolls the current message based on the difference between number of
    columns and length of message.

    ::param lcd::           LCD object for scrolling information.
    ::param lcd_columns::   The number of columns on the screen.
    ::param length::        Length of the message.
    '''
    scrollRange = range(length-lcd_columns)
    for i in scrollRange:
        time.sleep(0.5)
        lcd.move_left()
        time.sleep(1)
    for i in scrollRange:
        time.sleep(0.5)
        lcd.move_right()
        time.sleep(1)

def moveToNextEvent(index, eventSignalThread, lcd):
    '''Creates a new thread for the next event in the list.

    ::param index::             The number of the event to be displayed.
    ::param eventSignalThread:: Event object used to indicate when the
                                calculateAndPrint message should cease
                                operations.
    ::param lcd::               LCD object for displaying object.
    ::returns::                 Thread object with new event loaded.
    '''
    currentEvent = events[index]
    newEventThread = threading.Thread(target=calculateAndPrintMessage, args=(eventSignalThread, lcd, currentEvent[0], currentEvent[1], timeFormat))
    return newEventThread

def startProgram(events):
    '''Starts the countdown program and entry-point for program.

    ::param events:: List of events to be displayed.
    '''
    index = 0
    currentFuture = events[index]
    preposition = " in\n" 
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd_columns = lcd._cols
    eventSignalThread = threading.Event()
    currentEventThread = threading.Thread(target=calculateAndPrintMessage, args=(eventSignalThread, lcd, currentFuture[0], currentFuture[1], timeFormat))
    try:
        while True:
            if lcd.is_pressed(LCD.UP):
                index = (index + 1) % len(events)
                eventSignalThread.set()
                # Waits until the current thread reads the signal to stop.
                currentEventThread.join()
                currentEventThread = moveToNextEvent(index, eventSignalThread, lcd)
            elif lcd.is_pressed(LCD.DOWN):
                index = (index - 1) % len(events)
                eventSignalThread.set()
                # Waits until the current thread reads the signal to stop.
                currentEventThread.join()
                currentEventThread = moveToNextEvent(index, eventSignalThread, lcd)

            if currentEventThread is not None and not currentEventThread.isAlive():
                eventSignalThread.clear()
                currentEventThread.start()
                time.sleep(1)
    except (KeyboardInterrupt):
        if currentEventThread is not None and currentEventThread.isAlive():
            eventSignalThread.set()
            # Waits until the current thread reads the signal to stop.
            currentEventThread.join()
            print("Count Down Ended.  Goodbye!")

if __name__ == '__main__':
    startProgram(events)
