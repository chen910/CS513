import csv
import sys
import math
from entity import MatchedProbe, SlopeLink

def readfileName():
    if len(sys.argv) == 3:
        matchFile = sys.argv[1]
        LinkFile = sys.argv[2]
    else:
        print("Please input the matchedPoint file and LinkData file.")
        sys.exit(1)

    return matchFile, LinkFile

def readMatchData(fileName):
    print("reading matchedProbe data...")
    matchedProbeList =[]
    with open(fileName, newline='') as csvfile:
        probe = csv.reader(csvfile)
        for row in probe:            
            aprobe = MatchedProbe(row)
            matchedProbeList.append(aprobe)
            # print(aprobe.coord)
    # print(len(matchedProbeList))
    print("finished.")
    return matchedProbeList

def readLink(fileName):
    print("reading link data...")
    listOfLink =[]
    with open(fileName, newline='') as csvfile:
        link = csv.reader(csvfile)
        for row in link: 
            shape = []
            slopeInfo = []
            if row[14] != None:           
                points = row[14].split('|')
                # print(points[0].split('/'))
                lat, lon, alt = points[0].split('/')
                shape.append((float(lat), float(lon)))
                if alt != '':
                    alt = float(alt)
            if row[16] != '':
                slopeinfo = row[16].split('|') 
                for slope in slopeinfo:
                    s = slope.split('/')
                    slopeInfo.append((float(s[0]),float(s[1])))
            alink = SlopeLink(row, shape, alt, slopeInfo)
            listOfLink.append(alink)
    # print(len(listOfLink))
    print("finished.")
    return listOfLink

def evaSlope(matchedProbeList, listOfLink):
    print("evaluating slope...")
    slopeResult = []
    for point in matchedProbeList:
        # for index, link in enumerate(listOfLink):
        #     if link.id == point.linkID:
        #         link = listOfLink[index + 1]
        link = next((link for link in listOfLink if link.id == point.linkID))
        if len(link.slopeinfo) > 0:            
            matchRefDis = math.sqrt(abs(point.distFromRef ** 2 - point.distFromLink ** 2))
            slope = link.slopeinfo[0][1]
            for index in range(1, (len(link.slopeinfo))):
                if matchRefDis < link.slopeinfo[index][0]:
                    slope = link.slopeinfo[index-1][1]
            
            evaSlope = calSlope(point.distFromRef, link.alt, point.alt)
            # print(point.distFromRef, link.alt, point.alt)
            # print(evaSlope)
            slopeResult.append((point.linkID, point.lat, point.lon, evaSlope, slope, abs(evaSlope - slope)))

    print("finished.")
    return slopeResult

def calSlope(dist, alt1, alt2):

    return math.degrees(math.atan((alt2 - alt1) / dist))
 

def output(fileName, slopeResult):
    print("outputing...")
    with open(fileName,'w', newline ='') as csvfile:
        for row in slopeResult:
            output = csv.writer(csvfile)
            output.writerow((row))
    print("output finished.")

def main():
    # matchData = "Partition6467MatchedPoints.csv"
    matchFile, LinkFile = readfileName()
    matchedProbeList = readMatchData(matchFile)
    listOfLink = readLink(LinkFile)
    slopeResult = evaSlope(matchedProbeList, listOfLink)
    outputName = "LinkSlopeAndEvaSlope.csv"
    output(outputName, slopeResult)

if __name__ == '__main__':
    main()