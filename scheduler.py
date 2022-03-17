import logFilter
import sys, os
import re
import matplotlib.pyplot as plt
import pandas as pd


gScheduerActivities = pd.DataFrame()

def printHelpMessage():
    print(sys.argv[0], 'summarizes the scheduler activity from the CD server logs')
    #print(sys.argv[0], '-i pattern [-i pattern] -e pattern [-i pattern]')


def schedulerLogEntryHandler(logEntry):
    '''gather the log entries of one scheduler iteration and call processSchedulerOneIterationLogEntries to process it'''

    # a scheduler log entry only has one line
    line = logEntry[0]

    if hasattr(schedulerLogEntryHandler, 'gotFirstIteration'):
        # already got the first iteration, 99.999% cases
        if re.search(r'\| operationDeadlineTrigger\[name=scheduleStepsTrigger[0-9]\]: deadline elapsed', line, re.M):
            # a new iteration starts, process currentIterationLogEntries
            if hasattr(schedulerLogEntryHandler, 'currentIterationLogEntries'):
                processSchedulerOneIterationLogEntries(schedulerLogEntryHandler.currentIterationLogEntries)

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


def processSchedulerOneIterationLogEntries(iterationLogEntries):
    '''process the log entries of one scheduler iteration'''

    iterationStart = logFilter.getLogTime(iterationLogEntries)
    iterationEnd = logFilter.getLogTime(iterationLogEntries[-1:])
    # get the duration (in ms) from the log timestamp. It's accurate enough
    iterationDuration = (iterationEnd - iterationStart).microseconds / 1000
    runnableSteps = 0
    processedSteps = 0
    scheduledSteps = 0
    if isFreeIteration(iterationLogEntries) is False:
        # find runnableSteps, processedSteps, scheduledSteps
        for line in iterationLogEntries:
            rpsLine = re.search(r'Runnable steps (.*); processed steps (.*); scheduled steps (.*);', line, re.M)
            if rpsLine:
                runnableSteps = rpsLine.group(1)
                processedSteps = rpsLine.group(2)
                scheduledSteps = rpsLine.group(3)
                break

    addSchedulerActivity(iterationStart, iterationEnd, int(iterationDuration), int(runnableSteps), int(processedSteps), int(scheduledSteps))

    # for line in iterationLogEntries:
    #     print(line, end='')
    # print(iterationStart, iterationEnd, iterationDuration, runnableSteps, processedSteps, scheduledSteps)
    # print('\n\n\n')


def addSchedulerActivity(iterationStart, iterationEnd, iterationDuration, runnableSteps, processedSteps, scheduledSteps):
    '''add one iteration activity to the global gScheduerActivities'''

    global gScheduerActivities
    newActivity = pd.DataFrame(
        {
            'start': [iterationStart],
            'end': [iterationEnd],
            'duration': [iterationDuration],
            'runnable': [runnableSteps],
            'processed': [processedSteps],
            'scheduled': [scheduledSteps]
        }
    )
    gScheduerActivities = pd.concat([gScheduerActivities, newActivity])


def summarizeSchedulerActivity():
    '''summarize the scheduler's activities'''

    global gScheduerActivities

    start = gScheduerActivities.iloc[0]['start']
    end = gScheduerActivities.iloc[-1]['end']
    iterations = len(gScheduerActivities)
    duration = end - start
    freq = iterations / duration.total_seconds()
    totalRunnable = gScheduerActivities['runnable'].sum()
    totalProcessed = gScheduerActivities['processed'].sum()
    totalScheduled = gScheduerActivities['scheduled'].sum()
    ActivitiesNotProcessedAllRunnableSteps = gScheduerActivities[gScheduerActivities['processed'] < gScheduerActivities['runnable']]

    print('From {} to {} ({}), the scheduler run {} times'.format(start, end, str(duration), iterations))
    print('On average, the scheduler runs {} times every second. '.format(freq), end='')
    print('Please note by default the scheduler can sleep maximim 10 minutes if the server is not busy.')
    print('Total runnable steps: {}. Please note runnable steps might be added multiple times if not processed/scheduled in an interation.'.format(totalRunnable))
    print('Total processed steps: {}'.format(totalProcessed))
    print('Total scheduled steps: {}'.format(totalScheduled))
    print('There are {} times that not all runnable steps were processed. '.format(len(ActivitiesNotProcessedAllRunnableSteps)), end='')
    print('Please consider that the system is too busy if this happened many times!')

def isFreeIteration(iterationLogEntries):
    '''check if the iteration is free. In other words, there's no runnable steps to process.'''

    return len(iterationLogEntries) <= 6


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
    summarizeSchedulerActivity()


if __name__ == "__main__":
    main(sys.argv[1:])