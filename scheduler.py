import logFilter
import sys, getopt, os


def printHelpMessage():
    print(sys.argv[0], 'summarizes the scheduler activity from the CD server logs')
    #print(sys.argv[0], '-i pattern [-i pattern] -e pattern [-i pattern]')


def logEntryHandler(logEntry):
    '''handles one log entry'''

    print(''.join(logEntry), end='')


def prepareFilters():
    '''prepares the patterns to filter the scheduleStepsTrigger* logs'''

    includePatterns = []
    excludePatterns = []

    includePatterns.append('\| scheduleStepsTrigger0')

    return (includePatterns, excludePatterns)

def main(argv):
    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))
    lf = logFilter.getLogFiles(cwd)
    (includePatterns, excludePatterns) = prepareFilters()
    logFilter.processMultipleLogFiles(lf, logEntryHandler, includePatterns, excludePatterns)


if __name__ == "__main__":
    main(sys.argv[1:])