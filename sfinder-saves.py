from collections import Counter
import argparse
import os
import re
import json
import subprocess

class Saves():
    # constants
    PIECES = ["T", "I", "L", "J", "S", "Z", "O"]
    
    # files
    pathFile = "output/path.csv"
    percentOutput = "output/savesPercent.txt"

    filteredPath = "resources/filteredPath.txt"
    filterOutput = "output/filteredSolves.txt"

    wantedSavesJSON = "resources/wantedSavesMap.json"
    fumenLabels = "resources/fumenLabels.js"
    fumenCombine = "resources/fumenCombine.js"
    fumenComment = "resources/fumenAddComment.js"
    bestSave = "bestSaves/"

    def __init__(self):
        self.__setupParser()

    def __setupParser(self):
        self.__parser = argparse.ArgumentParser(usage="<cmd> [options]", description="A tool for further expansion of the saves from path.csv")
        subparsers = self.__parser.add_subparsers()

        self.__setupPercentParser(subparsers)
        self.__setupFilterParser(subparsers)
    

    def __setupPercentParser(self, parser):
        percentParser = parser.add_parser("percent", help="Give the percents of saves using the path.csv file with wanted save expression")
        percentParser.set_defaults(func=self.__percentParse)
        percentParser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
        percentParser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
        percentParser.add_argument("-a", "--all", help="output all of the saves and corresponding percents (alternative to not having -k nor -w)", action="store_true")
        percentParser.add_argument("-p", "--pieces", help="pieces used on the setup (required unless there's -pc)", metavar="<string>", nargs='+')
        percentParser.add_argument("-pc", "--pc-num", help="pc num for the setup & solve (required unless there's -p)", metavar="<int>", type=int)
        percentParser.add_argument("-f", "--path", help="path file directory (default: output/path.csv)", metavar="<directory>", default=self.pathFile, type=str)
        percentParser.add_argument("-o", "--output", help="output file directory (default: output/saves.txt)", metavar="<directory>", default=self.percentOutput, type=str)
        percentParser.add_argument("-pr", "--print", help="log to terminal (default: True)", action="store_false")
        percentParser.add_argument("-fr", "--fraction", help="include the fraction along with the percent (default: True)", action="store_false")
        percentParser.add_argument("-fa", "--fails", help="include the fail queues for saves in output (default: False)", action="store_true")
        percentParser.add_argument("-os", "--over-solves", help="have the percents be saves/solves (default: False)", action="store_true")
    
    def __setupFilterParser(self, parser):
        filterParser = parser.add_parser("filter", help="filter path.csv of fumens that doesn't meet the wanted saves")
        filterParser.set_defaults(func=self.__filterParse)
        filterParser.add_argument("-w", "--wanted-saves", help="the save expression (required if there isn't -k)", metavar="<string>", nargs='+')
        filterParser.add_argument("-k", "--key", help="use wantedPiecesMap.json for preset wanted saves (required if there isn't a -w)", metavar="<string>", nargs='+')
        filterParser.add_argument("-p", "--pieces", help="pieces used on the setup (required unless there's -pc)", metavar="<string>", nargs='+')
        filterParser.add_argument("-pc", "--pc-num", help="pc num for the setup & solve (required unless there's -p)", metavar="<int>", type=int)
        filterParser.add_argument("-f", "--path", help="path file directory (default: output/path.csv)", metavar="<directory>", default=self.pathFile, type=str)
        filterParser.add_argument("-o", "--output", help="output file directory (default: output/filteredSolves)", metavar="<directory>", default=self.filterOutput, type=str)
        filterParser.add_argument("-pr", "--print", help="log to terminal (default: True)", action="store_false")
        filterParser.add_argument("-s", "--solve", help="setting for how to output solve (minimal, unique, None)(default: minimal)", choices={"minimal", "unique", "None"}, metavar="<string>", default="minimal", type=str)
        filterParser.add_argument("-t", "--tinyurl", help="output the link with tinyurl if possible (default: True)", action="store_false")
        filterParser.add_argument("-fc", "--fumen-code", help="include the fumen code in the output (default: False)", action="store_true")

    def handleParse(self, customInput=os.sys.argv[1:]):
        args = self.__parser.parse_args(customInput)
        if vars(args):
            args.func(args)
        else:
            print("No Command Inputted")

    def __percentParse(self, args):
        percentFuncArgs = {}

        # semi-required options
        wantedSaves = []
        if args.wanted_saves is not None:
            wantedSaves.extend(args.wanted_saves)
        if args.key is not None:
            with open(self.wantedSavesJSON, "r") as outfile:
                wantedSaveDict = json.loads(outfile.read())
            wantedSaves.extend([",".join(wantedSaveDict[k]) for k in args.key])
        wantedSaves = ",".join(wantedSaves)
        percentFuncArgs["All Saves"] = args.all

        if not wantedSaves and not args.all:
            # didn't have the wanted-saves nor a key
            print("Syntax Error: The options --wanted-saves (-w) nor --key (-k) was found")
            return
        
        pieces = ""
        pcNum = -1
        if args.pieces is not None:
            pieces = "".join(args.pieces).upper()
        elif args.pc_num is not None:
            pcNum = args.pc_num
        else:
            # didn't have the pieces nor a pc num
            print("Syntax Error: The options --pieces (-p) nor --pc-num (-pc) was found")
            return
        
        # options
        percentFuncArgs["Path File"] = args.path
        percentFuncArgs["Output File"] = args.output
        percentFuncArgs["Print"] = args.print
        percentFuncArgs["Fraction"] = args.fraction
        percentFuncArgs["Fails"] = args.fails
        percentFuncArgs["Over Solves"] = args.over_solves
        
        self.percent(wantedSaves, pieces, pcNum, percentFuncArgs)

    # return an dictionary including all the wantedSaves over the path file
    def percent(self, wantedSaves, pieces="", pcNum=-1, args={}):
        defaultArgs = {
            "Path File": self.pathFile,
            "Output File": self.percentOutput,
            "Print": True,
            "All Saves": False,
            "Fraction": True,
            "Fails": False,
            "Over Solves": False
        }
        defaultArgs.update(args)
        args = defaultArgs

        if not os.path.exists(args["Path File"]):
            print(f'The path to "{args["Path File"]}" could not be found!')
            return

        countWanted = {}
        wantedSavesFails = {}
        wantedStacks = []
        countAll = None
        storeAllPreviousQs = None
        if args["All Saves"]:
            countAll = {}
            if args["Fails"]:
                storeAllPreviousQs = []

        if wantedSaves:
            for wantedSave in wantedSaves.split(","):
                countWanted[wantedSave] = 0
                wantedStacks.append(self.__makeStack(wantedSave))

        # from pieces get the pieces given for the possible pieces in the last bag of the pc and it's length
        lastBag, newBagNumUsed = self.__findLastBag(pieces, pcNum)

        totalCases = self.__getPercentData(lastBag, newBagNumUsed, wantedStacks, countWanted, countAll, storeAllPreviousQs, wantedSavesFails, args)
        
        allStr = self.__formatPercentData(totalCases, countWanted, countAll, wantedSavesFails, args)
        with open(args["Output File"], "w") as infile:
            infile.write(allStr)
        
        if args["Print"]:
            print(allStr)
    
    def __getPercentData(self, lastBag, newBagNumUsed, wantedStacks, countWanted, countAll, storeAllPreviousQs, wantedSavesFails, args):
        totalCases = 0
        outfile = open(args["Path File"], "r")
        outfile.readline() # skip header row

        for line in outfile:
            line = line.split(",")
            # has solve?
            if line[1] != "0":
                bagSavePieces = lastBag - set(line[0][-newBagNumUsed:])
                savePieces = set(line[3].strip().split(";"))
                if '' in savePieces:
                    savePieces = set()
                
                allSaves = self.__createAllSavesQ(savePieces, bagSavePieces)
                if args["All Saves"]:
                    for save in allSaves:
                        if save in countAll:
                            countAll[save] += 1
                        else:
                            countAll[save] = 1
                            if args["Fails"]:
                                wantedSavesFails[save] = storeAllPreviousQs.copy()

                    if args["Fails"]:
                        storeAllPreviousQs.append(line[0])
                        for nonsave in set(wantedSavesFails.keys()) - set(allSaves):
                            wantedSavesFails[nonsave].append(line[0])

                for stack, wantedSave in zip(wantedStacks, countWanted):
                    if(self.parseStack(allSaves, stack)):
                        countWanted[wantedSave] += 1
                    else:
                        if args["Fails"]:
                            if wantedSave not in wantedSavesFails:
                                wantedSavesFails[wantedSave] = [line[0]]
                            else:
                                wantedSavesFails[wantedSave].append(line[0])
                totalCases += args["Over Solves"]

            if args["Fails"]:
                for wantedSave in wantedSavesFails:
                    if wantedSave not in wantedSavesFails:
                        wantedSavesFails[wantedSave] = [line[0]]
                    else:
                        wantedSavesFails[wantedSave].append(line[0])
                
            totalCases += not args["Over Solves"]
        
        outfile.close()
        
        return totalCases
    
    def __formatPercentData(self, totalCases, countWanted, countAll, wantedSavesFails, args):
        allStr = []
        for key, value in countWanted.items():
            if totalCases:
                percent = value / totalCases * 100
                percentStr = f'{key}: {percent:.2f}%'
                if args["Fraction"]:
                    percentStr += f' ({value}/{totalCases})'
            else:
                percentStr = f'{key}: {value}'
            
            if args["Fails"] and key in wantedSavesFails:
                percentStr += "\nFail Queues:\n"
                percentStr += ",".join(wantedSavesFails[key])
            allStr.append(percentStr)
        if args["All Saves"]:
            # format countAll to be tetris sorted
            sortedCountAll = {}
            for key in sorted(map(lambda x: self.getOrderValue(x)+x, countAll.keys())):
                sortedCountAll[key[len(key)//2:]] = countAll[key[len(key)//2:]]

            for key, value in sortedCountAll.items():
                if totalCases:
                    percent = value / totalCases * 100
                    percentStr = f'{key}: {percent:.2f}%'
                    if args["Fraction"]:
                        percentStr += f'({value}/{totalCases})'
                else:
                    percentStr = f'{key}: {value}'
                
                if args["Fails"] and key in wantedSavesFails:
                    percentStr += "\nFail Queues:\n"
                    percentStr += ",".join(wantedSavesFails[key])
                allStr.append(percentStr)
        
        return "\n".join(allStr)

    def __filterParse(self, args):
        filterFuncArgs = {}

        # semi-required options
        wantedSaves = []
        if args.wanted_saves is not None:
            wantedSaves.extend(args.wanted_saves)
        if args.key is not None:
            with open(self.wantedSavesJSON, "r") as outfile:
                wantedSaveDict = json.loads(outfile.read())
            wantedSaves.extend([",".join(wantedSaveDict[k]) for k in args.key])
        wantedSaves = ",".join(wantedSaves)

        if not wantedSaves:
            # didn't have the wanted-saves nor a key
            print("Syntax Error: The options --wanted-saves (-w) nor --key (-k) was found")
            return
        
        pieces = ""
        pcNum = -1
        if args.pieces is not None:
            pieces = "".join(args.pieces).upper()
        elif args.pc_num is not None:
            pcNum = args.pc_num
        else:
            # didn't have the pieces nor a pc num
            print("Syntax Error: The options --pieces (-p) nor --pc-num (-pc) was found")
            return
        
        # options
        filterFuncArgs["Path File"] = args.path
        filterFuncArgs["Output File"] = args.output
        filterFuncArgs["Print"] = args.print
        filterFuncArgs["Solve"] = args.solve
        filterFuncArgs["Tinyurl"] = args.tinyurl
        filterFuncArgs["Fumen Code"] = args.fumen_code
        
        self.filter(wantedSaves, pieces, pcNum, filterFuncArgs)

    # filter the path fumen's for the particular save
    def filter(self, wantedSaves, pieces="", pcNum=-1, args={}):
        defaultArgs = {
            "Path File": self.pathFile,
            "Output File": self.filterOutput,
            "Solve": "minimal",
            "Tinyurl": True,
            "Fumen Code": False
        }

        if not os.path.exists(args["Path File"]):
            print(f'The path to "{args["Path File"]}" could not be found!')
            return

        pathFileLines = []
        fumenSet = set()
        fumenAndQueue = {}

        self.__filterGetData(pathFileLines, fumenSet, fumenAndQueue)
        
        # from pieces get the pieces given for the possible pieces in the last bag of the pc and it's length
        lastBag, newBagNumUsed = self.__findLastBag(pieces, pcNum)

        # main section
        stack = self.__makeStack(wantedSaves.split(",")[0])
        self.__filterFumensInPath(stack, pathFileLines, fumenAndQueue, lastBag, newBagNumUsed)

        with open(self.filteredPath, "w") as infile:
            for line in pathFileLines:
                infile.write(",".join(line) + "\n")
        
        if args["Solve"] != "None":
            if args["Solve"] == "minimal":
                self.true_minimal(self.filteredPath, args["Output File"], args["Tinyurl"], args["Fumen Code"])
            elif args["Solve"] == "unique":
                self.uniqueFromPath(self.filteredPath, args["Output File"], args["Tinyurl"], args["Fumen Code"])
            
            if args["Print"]:
                with open(args["Output File"], "r") as outfile:
                    print(outfile.read())
    
    def __filterGetData(self, pathFileLines, fumenSet, fumenAndQueue):
        with open(self.pathFile, "r") as outfile:
            headerLine = outfile.readline().rstrip().split(",")
            pathFileLines.append(headerLine)
            for line in outfile:
                line = line.rstrip().split(",")
                pathFileLines.append(line)
                if line[4]:
                    fumens = line[4].split(";")
                else:
                    continue
                fumenSet.update(set(fumens))
        
        labelP = subprocess.Popen(["node", self.fumenLabels] + list(fumenSet), stdout=subprocess.PIPE)
        labels = labelP.stdout.read().decode().rstrip().split("\n")
        
        for label, fumen in zip(labels, fumenSet):
            fumenAndQueue[fumen] = label

    def __filterFumensInPath(self, stack, pathFileLines, fumenAndQueue, lastBag, newBagNumUsed):
        for line in pathFileLines[1:]:
            queue = Counter(line[0])
            if line[4]:
                fumens = line[4].split(";")
            else:
                continue
            for i in range(len(fumens)-1, -1, -1):
                savePiece = queue - Counter(fumenAndQueue[fumens[i]])

                bagSavePieces = lastBag - set(line[0][-newBagNumUsed:])
                allSave = [self.tetrisSort("".join(savePiece) + "".join(bagSavePieces))]
                if not self.parseStack(allSave, stack):
                    fumens.pop(i)
            line[4] = ";".join(fumens)
            line[1] = str(len(fumens))
    
    def true_minimal(self, pathFile="", output="", tinyurl=True, fumenCode=False):
        if not pathFile:
            pathFile = self.pathFile
        if not output:
            output = self.filterOutput

        os.system(f'sfinder-minimal {pathFile}')

        with open("path_minimal_strict.md", "r") as trueMinFile:
            trueMinLines = trueMinFile.readlines()
        
        totalCases = int(re.search("/ (\d+)\)", trueMinLines[2]).group(1))
        percents = []
        for line in trueMinLines[13::9]:
            numCoverCases = int(re.match("(\d+)", line).group(1))
            percent = numCoverCases / totalCases * 100
            percent = f'{percent:.2f}% ({numCoverCases}/{totalCases})'
            percents.append(percent)
        fumenLst = re.findall("(v115@[a-zA-Z0-9?/+]*)", trueMinLines[6])

        combineP = subprocess.Popen(["node", self.fumenCombine] + fumenLst, stdout=subprocess.PIPE)
        fumenCombineOut = combineP.stdout.read().decode().rstrip()
        commentP = subprocess.Popen(["node", self.fumenComment, fumenCombineOut] + percents, stdout=subprocess.PIPE)
        fumenLink = commentP.stdout.read().decode().rstrip()

        if fumenCode:
            fumenCode = fumenCode[21:]
        
        if tinyurl:
            try:
                line = self.make_tiny(fumenLink)
            except:
                line = "Tinyurl did not accept fumen due to url length"
        
        with open(output, "w") as infile:
            infile.write("True minimal: \n")
            infile.write(line)
            if fumenCode:
                infile.write("\n" + fumenCode)
    
    def uniqueFromPath(self, pathFile="", output="", tinyurl=True, fumenCode=False):
        if not pathFile:
            pathFile = self.pathFile
        if not output:
            output = self.filterOutput

        countSolve = {}
        with open(pathFile, "r") as outfile:
            outfile.readline()
            for totalCases, line in enumerate(outfile):
                fumens = line.rstrip().split(",")[-1]
                if fumens:
                    for fumen in fumens.split(";"):
                        if fumen not in countSolve:
                            countSolve[fumen] = 1
                        else:
                            countSolve[fumen] += 1
        
        totalCases += 1
        countSolve = sorted(countSolve.items(), key=lambda x:x[1], reverse=True)
        solves = []
        percents = []
        for fumen, count in countSolve:
            # add the fumen codes and percents to separate lists
            percent = count / totalCases * 100
            percents.append(f"{percent:.2f}% ({count}/{totalCases})")
            solves.append(fumen)
        
        # combine the fumen codes of the solves
        combineP = subprocess.Popen(["node", self.fumenCombine] + solves, stdout=subprocess.PIPE)
        fumenCombineOut = combineP.stdout.read().decode().rstrip()
        # add the comments to each page of the coverage of that solve
        commentP = subprocess.Popen(["node", self.fumenComment, fumenCombineOut] + percents, stdout=subprocess.PIPE)
        fumenLink = commentP.stdout.read().decode().rstrip()

        if fumenCode or len(countSolve) > 128:
            fumenCode = fumenLink[21:]

        if tinyurl:
            try:
                line = self.make_tiny(fumenLink)
            except:
                line = "Tinyurl did not accept fumen due to url length"
        
        with open(output, "w") as infile:
            infile.write("Unique Solves Filtered: \n")
            infile.write(line)
            if fumenCode:
                infile.write("\n" + fumenCode)

    def runBestSaves(self, pcNum, configs):
        if not self.checkFileExist(self.logFile):
            raise OSError("The log file for saves doesn't exist. May be due to sfinder error when running path prior.")
        
        # store the chance and the total cases of the setup
        chanceData = self.getFromLastOutput("  -> success = (\d+.\d{2}% \(\d+\/\d+\))", self.logFile)[0]
        if configs["Over PC Cases"]:
            totalCases = int(re.findall("\((\d+)/", chanceData)[0])
        else:
            totalCases = int(re.findall("/(\d+)[)]", chanceData)[0])

        data = self.calculateBestSavesList()
        if not data:
            return
        infile = open(self.savePieceOutput, "w")
        infile.write("Best Saves:\n")
        for save, count in data.items():
            percent = count / totalCases * 100
            infile.write(f'{save}: {percent:.2f} ({count}/{totalCases})\n')

        infile.close()
    
    def calculateBestSavesList(self, pcNum=2):
        # defaults to 2nd pc as it's the most common pc to use this for

        pieces = self.getFromLastOutput("  ([TILJSZOP1-7!,\[\]^*]+)", self.logFile)[0]
        # from pieces get the pieces given for the possible pieces in the last bag of the pc and it's length
        lastBag, newBagNumUsed = self.__findLastBag(pieces)

        path = f'{self.bestSave}PC-{pcNum}.txt'
        if not self.checkFileExist(path):
            raise OSError(f'The best saves for "{pcNum}" have not been found yet. However, you can create your own if you create the file "{path}".')

        with open(path, "r") as outfile:
            bestSaves = {line.rstrip(): 0 for line in outfile}

        with open(self.pathFile, "r") as outfile:
            outfile.readline()
            for line in outfile:
                line = line.split(",")
                if line[1] == "0":
                    continue

                bagSavePieces = lastBag - set(line[0][-newBagNumUsed:])
                savePieces = set(line[3].strip().split(";"))
                if '' in savePieces:
                    savePieces = set()
                
                allSaves = self.__createAllSavesQ(savePieces, bagSavePieces)

                for save in bestSaves:
                    currBool = False
                    for s in save.split("/"):
                        currBool = currBool or self.__compareQueues(allSaves, s)
                    if currBool:
                        bestSaves[save] += 1
                        break
            
        return bestSaves

    # determine the length of the last bag based on queue
    def __findLastBag(self, pieces, pcNum):
        if not pieces:
            if pcNum != -1:
                lastBag = set(self.PIECES)
                newBagNumUsed = (pcNum * 3) % 7 + 1
                return set(lastBag), newBagNumUsed
            else:
                raise SyntaxError("One of pieces or pcNum must be filled out")

        if not re.match("[!1-7*]", pieces[-1]):
            raise SyntaxError("The pieces inputted doesn't end with a bag")
        
        # what kind of bag is the last part
        lastPartPieces = re.findall("\[?([\^tiljszoTILJSZO*]+)\]?P?[1-7!]?", pieces.split(",")[-1])
        if lastPartPieces:
            lastPartPieces[-1]
        else:
            raise SyntaxError("The pieces inputted doesn't end with a bag")
        
        # number of pieces used in the next bag
        newBagNumUsed = pieces[-1]
            

        # turn the piece input into data for determining saves
        if lastPartPieces[0] == "*":
                # all pieces used
                lastBag = self.PIECES
        elif lastPartPieces[0] == "^":
                # remove the pieces from the bag
                lastBag = set(self.PIECES) - set([piece.upper() for piece in lastPartPieces[1:]])
        else:
                # only these pieces in the bag
                lastBag = set([piece.upper() for piece in lastPartPieces])

        # determine the number of pieces the last bag has
        if newBagNumUsed.isnumeric():
            newBagNumUsed = int(newBagNumUsed)
        elif newBagNumUsed == "!":
            # it must be !
            newBagNumUsed = len(lastBag)
        else:
            # case without a number or ! (just *)
            newBagNumUsed = 1

        return set(lastBag), newBagNumUsed
    
    def make_tiny(self, url): 
        import contextlib 
    
        try: 
            from urllib.parse import urlencode           
        
        except ImportError: 
            from urllib import urlencode 
        from urllib.request import urlopen

        request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))     
        with contextlib.closing(urlopen(request_url)) as response:                       
            return response.read().decode('utf-8 ')
    
    # finds all the saves and adds them to a list
    def __createAllSavesQ(self, savePieces, bagSavePieces, solveable=True):
        allSaves = []
        if solveable and not savePieces:
            lstSaves = list(bagSavePieces)
            saves = [self.tetrisSort("".join(lstSaves))]
            return saves
        for p in savePieces:
            lstSaves = list(bagSavePieces)
            lstSaves.append(p)
            saves = self.tetrisSort("".join(lstSaves))
            allSaves.append(saves)
        return allSaves

    # turn the wantedPieces into a multi-depth stack to easily parse through
    def __makeStack(self, wantedPieces, index=0, depth=0):
        stack = []

        queue = ""
        operatorHold = ""
        while index < len(wantedPieces):
            char = wantedPieces[index]

            # finish for normal queue
            if queue and not re.match("[TILJSZO]", char):
                stack.append(self.tetrisSort(queue))
                queue = ""
                
            # regex queue
            if char == "/":
                queue = re.search("(/.*?/)", wantedPieces[index:])
                if queue:
                    queue = queue.group(1)
                else:
                    raise SyntaxError("Wanted Saves: Missing ending '/' in regex queue")
                stack.append(queue)
                index += len(queue) - 1
                queue = ""

            # normal queue
            elif re.match("[TILJSZO]", char):
                queue += char

            # negator
            elif char == "!":
                stack.append("!")
            # avoider
            elif char =="^":
                stack.append("^")

            # operator
            elif char == "&" or char == "|":
                if operatorHold == char:
                    stack.append(operatorHold*2)
                    operatorHold = ""
                elif len(operatorHold) == 1:
                    raise SyntaxError("Wanted Saves: Operator inputted incorrectly should be && or ||")
                else:
                    operatorHold += char
                
            # parentheses
            elif char == "(":
                lst, i = self.__makeStack(wantedPieces, index+1, depth+1)
                stack.append(lst)
                index = i
            elif char == ")":
                if depth != 0:
                    return stack, index
                else:
                    raise SyntaxError("Wanted Saves: Missing opening parentheses")
            # error
            else:
                raise SyntaxError(f"Wanted Saves: Input has unknown character '{char}'")
            index += 1
        
        if queue:
            stack.append(self.tetrisSort(queue))
            queue = ""

        # check if back to the top layer
        if depth == 0:
            return stack
        else:
            raise SyntaxError("Wanted Saves: Missing closing parentheses")
    
    def __compareQueues(self, allSaves, queue, diff=False):
        # check regex queue
        if re.match("/.*/", queue):
            if not diff:
                for save in allSaves:
                    if re.search(queue[1:-1], save):
                        return True
            else:
                for save in allSaves:
                    if not re.search(queue[1:-1], save):
                        return True
        
        # normal queue
        else:
            for save in allSaves:
                index = 0
                for piece in save:
                    if index == len(queue):
                        break
                    if piece == queue[index]:
                        index += 1
                if diff:
                    if index != len(queue):
                        return True
                elif index == len(queue):
                        return True
        
        return False                

    def parseStack(self, allSaves, stack, distributeNOT=False, distributeAvoid=False):
        negate = distributeNOT
        avoid = distributeAvoid
        operator = ""
        currBool = False
        for ele in stack:
            if ele == "!":
                negate = not negate
            elif ele == "^":
                avoid = not avoid

            elif self.isOperator(ele):
                operator = ele
            
            elif self.isQueue(ele) or type(ele) == type([]):
                if self.isQueue(ele):
                    saveable = self.__compareQueues(allSaves, ele, diff=avoid)
                    if negate:
                        saveable = not saveable
                else:
                    saveable = self.parseStack(allSaves, ele, negate, avoid)
                negate = distributeNOT
                avoid = distributeAvoid
                if operator:
                    if operator == "&&":
                        if distributeNOT or distributeAvoid:
                            currBool = currBool or saveable
                        else:
                            currBool = currBool and saveable
                    elif operator == "||":
                        if distributeNOT or distributeAvoid:
                            currBool = currBool and saveable
                        else:
                            currBool = currBool or saveable
                    else:
                        raise RuntimeError("WantedParse: Operator variable got a non-operator (please contact dev)")
                else:
                    currBool = saveable

            else:
                raise RuntimeError("WantedParse: Stack includes string that's not a queue nor operator (please contact dev)")
        return currBool
    
    # sorts the pieces inputted
    def tetrisSort(self, queue):
        # order of the pieces TILJSZO
        PIECEORDER = {
            "T":"1", "1":"T",
            "I":"2", "2":"I",
            "L":"3", "3":"L",
            "J":"4", "4":"J",
            "S":"5", "5":"S",
            "Z":"6", "6":"Z",
            "O":"7", "7":"O"
        }

        numQ = ""
        for p in queue:
            numQ += PIECEORDER[p]

        numQ = "".join(sorted(list(numQ)))
        queue = ""

        for c in numQ:
            queue += PIECEORDER[c]

        return queue
    
    def getOrderValue(self, queue):
        PIECEORDER = {
            "T":"1",
            "I":"2",
            "L":"3",
            "J":"4",
            "S":"5",
            "Z":"6",
            "O":"7"
        }

        val = ""
        for p in queue:
            val += PIECEORDER[p]
        
        return val

    def isOperator(self, operator):
        return operator == "&&" or operator == "||"

    def isQueue(self, queue):
        if queue[0] == "/":
            return True
        return re.match("[TILJSZO]+", str(queue))

def runTestCases():
    s = Saves()

    tests = open("resources/testOutputs.txt", "r")

    s.handleParse(customInput=["percent", "-w", "/[OSZ]/", "-k", "2ndSaves", "-a", "-pc", "2", "-f", "resources/testPath2.csv", "-pr"])
    with open(s.percentOutput, "r") as outfile:
        for out in outfile.readlines():
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 1")
    
    tests.readline()
    s.handleParse(customInput=["percent", "-w", "I", "-p", "*p7", "-fa", "-os", "-f", "resources/testPath2.csv", "-pr"])
    with open(s.percentOutput, "r") as outfile:
        for out in outfile.readlines():
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 2")

    tests.readline()
    s.handleParse(customInput=["percent", "-a", "-p", "*p7", "-fr", "-fa", "-os", "-f", "resources/testPath2.csv", "-pr"])
    with open(s.percentOutput, "r") as outfile:
        for out in outfile.readlines():
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 3")
    
    tests.readline()
    s.handleParse(customInput=["filter", "-w", "/T.*[LJ].*$/", "-pc", "1", "-f", "resources/testPath1.csv", "-pr", "-t"])
    with open(s.filterOutput, "r") as outfile:
        for out in outfile.readlines():
            assert out.rstrip() == tests.readline().rstrip()
        print("Pass Test 4")

    tests.close()

if __name__ == "__main__":
    s = Saves()
    s.handleParse("filter -w T||O -pc 2 -s unique".split())
    #runTestCases()
