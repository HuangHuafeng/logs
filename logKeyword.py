import logFilter
import sys, getopt, os


gIncludePatterns = []
gExcludePatterns = []


def printHelpMessage():
    print(sys.argv[0], 'filters the logs (commander*.log, commander*.log.zip) in the current folder')
    print(sys.argv[0], '-i pattern [-i pattern] -e pattern [-i pattern]')


def handleOptions(argv):
    '''handle the options in the command'''

    global gIncludePatterns
    global gExcludePatterns

    try:
        opts, args = getopt.getopt(argv,"hi:e:",["include=","exclude="])
    except getopt.GetoptError:
        printHelpMessage()
        sys.exit(2)

    if not opts:
        printHelpMessage()
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-h':
            printHelpMessage()
            sys.exit(0)
        elif opt in ("-i", "--include"):
            gIncludePatterns.append(arg)
        elif opt in ("-e", "--exclude"):
            gExcludePatterns.append(arg)


def lh(logEntry):
    print(''.join(logEntry), end='')

def main(argv):
    handleOptions(argv)
    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))
    lf = logFilter.getLogFiles(cwd)
    logFilter.processMultipleLogFiles(lf, lh, gIncludePatterns, gExcludePatterns)


if __name__ == "__main__":
    main(sys.argv[1:])