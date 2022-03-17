import re
import os
from zipfile import ZipFile
import datetime

tmpDir = "temp"


def getLogFiles(directory):
    '''get the log files (commander*.log, commander*.log.zip) in a directory'''

    logFiles = []
    for f in os.listdir(directory):
        if f.startswith("commander") and (f.endswith(".log") or f.endswith(".log.zip")):
            #print("{0} is a log file.".format(f))
            logFiles.append(f)

    # sort it
    logFiles.sort()

    return logFiles


def processMultipleLogFiles(logFileList, logEntryHandler = None, includePatterns = [], excludePatterns = []):
    '''process the log files in logFileList'''

    cwd = os.getcwd()
    try:
        os.mkdir(cwd + "/" + tmpDir)
    except OSError as error:
        print(error)

    for logFile in logFileList:
        processOneLogFile(logFile, logEntryHandler, includePatterns, excludePatterns)


def unzipOneLogFile(logFile):
    '''unzip the log file if it's zipped'''

    if logFile.endswith(".log"):
        # the log file is not zipped, do nothing
        return logFile

    # extract the zipped log file
    with ZipFile(logFile, "r") as zipObj:
        zipObj.extractall(tmpDir)

    unzippedLogFile = tmpDir + "/" + logFile[:-4]

    return unzippedLogFile


def processOneLogFile(logFile, logEntryHandler, includePatterns, excludePatterns):
    '''process one log file and call logEntryHandler (if not None) on each log entry'''

    global logKeyword
    print("processing " + logFile)
    unzippedLogFile = unzipOneLogFile(logFile)
    fh = open(unzippedLogFile, 'r')

    (logEntry, firstLine) = nextLogEntry(fh)
    while logEntry:
        if isWantedEntry(logEntry, includePatterns, excludePatterns):
            if logEntryHandler is not None:
                logEntryHandler(logEntry)

        (logEntry, firstLine) = nextLogEntry(fh, firstLine)

    fh.close()

    # remove the extracted file
    if unzippedLogFile != logFile:
        os.remove(unzippedLogFile)


def nextLogEntry(logFileHandle, firstLine = ''):
    '''get next log entry from the current file'''

    logEntry = []
    if firstLine:
        logEntry.append(firstLine)

    line = logFileHandle.readline()
    if not line:
        # end of file
        return (logEntry, '')

    while line:
        newEntry = re.match("[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-9][0-9]T[0-9][0-9]", line)
        if newEntry:
            # the line begins a new entry
            if logEntry:
                # if we have already read a log entry
                break
            else:
                # starts a new log entry
                logEntry.append(line)
        else:
            logEntry.append(line)

        line = logFileHandle.readline()

    return (logEntry, line)


def isWantedEntry(logEntry, includePatterns, excludePatterns):
    '''check if the log entry is an interested one or not'''

    wanted = False
    excluded = False
    for line in logEntry:
        if includePatterns and wanted is False:
            for pattern in includePatterns:
                if re.search(pattern, line, re.M):
                    wanted = True
                    break

        if excludePatterns:
            for pattern in excludePatterns:
                if re.search(pattern, line, re.M):
                    excluded = True
                    break

        if excluded:
            wanted = False
            break

    return wanted


def getLogTime(logEntry):
    '''return the datetime of the log entry'''

    return datetime.datetime.strptime(logEntry[0][:23], "%Y-%m-%dT%H:%M:%S.%f")