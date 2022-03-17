import logFilter
import sys, os
import re


def printHelpMessage():
    print(sys.argv[0], 'summarizes the scheduler activity from the CD server logs')
    #print(sys.argv[0], '-i pattern [-i pattern] -e pattern [-i pattern]')


def schedulerLogEntryHandler(logEntry):
    '''gather the log entries of one scheduler iteration and call processSchedulerIterationLogEntries to process it'''

    # a scheduler log entry only has one line
    line = logEntry[0]

    if hasattr(schedulerLogEntryHandler, 'gotFirstIteration'):
        # already got the first iteration, 99.999% cases
        if re.search(r'\| operationDeadlineTrigger\[name=scheduleStepsTrigger[0-9]\]: deadline elapsed', line, re.M):
            # process currentIterationLogEntries
            if hasattr(schedulerLogEntryHandler, 'currentIterationLogEntries'):
                processSchedulerIterationLogEntries(schedulerLogEntryHandler.currentIterationLogEntries)

            # reset currentIterationLogEntries
            schedulerLogEntryHandler.currentIterationLogEntries = []
            schedulerLogEntryHandler.currentIterationLogEntries.append(line)
        else:
            # add the log entry to currentIterationLogEntries
            schedulerLogEntryHandler.currentIterationLogEntries.append(line)
    else:
        # wait for the first iteration
        if re.search(r'\| operationDeadlineTrigger\[name=scheduleStepsTrigger[0-9]\]: deadline elapsed', line, re.M):
            schedulerLogEntryHandler.gotFirstIteration = True
            schedulerLogEntryHandler.currentIterationLogEntries = []
            schedulerLogEntryHandler.currentIterationLogEntries.append(line)


def processSchedulerIterationLogEntries(iterationLogEntries):
    '''process the log entries of one scheduler iteration'''

    for line in iterationLogEntries:
        print(line, end='')
    print('\n\n\n')


# def logEntryHandler(logEntry):
#     '''handles one log entry'''

#     global gInSchedulerIteration

#     # a scheduler log entry only has one line
#     line = logEntry[0]
#     if gInSchedulerIteration is True:
#         if re.search(r'\| operationDeadlineTrigger\[name=scheduleStepsTrigger[0-9]\]: accepted new deadline', line, re.M):
#             gInSchedulerIteration = False
#             print(line)
#     else:
#         if re.search(r'\| operationDeadlineTrigger\[name=scheduleStepsTrigger[0-9]\]: deadline elapsed', line, re.M):
#             gInSchedulerIteration = True
#             print(line)


def prepareFilters():
    '''prepares the patterns to filter the scheduleStepsTrigger* logs'''

    includePatterns = []
    excludePatterns = []

    includePatterns.append(r'\| scheduleStepsTrigger[0-9]')

    return (includePatterns, excludePatterns)

def main(argv):
    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))
    lf = logFilter.getLogFiles(cwd)
    (includePatterns, excludePatterns) = prepareFilters()
    logFilter.processMultipleLogFiles(lf, schedulerLogEntryHandler, includePatterns, excludePatterns)


if __name__ == "__main__":
    main(sys.argv[1:])