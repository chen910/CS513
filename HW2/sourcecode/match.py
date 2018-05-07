import csv
import sys
from scipy.stats import norm
from entity import Probe, Link, Segment
from math import radians, sin, cos, sqrt, atan2


def readfileName():
    if len(sys.argv) == 3:
        ProbeFile = sys.argv[1]
        LinkFile = sys.argv[2]
    else:
        print("Please input the ProbePoints file and LinkData file.")
        sys.exit(1)

    return ProbeFile, LinkFile

def readProbe(fileName, probeReadNumber):
    print("reading probe data...")
    count = 0
    probeList =[]
    with open(fileName, newline='') as csvfile:
        probe = csv.reader(csvfile)
        # probe= csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in probe:
            aprobe = Probe(row)
            probeList.append(aprobe)
            # print(aprobe.coord)
            count += 1
            if count >= probeReadNumber:
                break
    print("finished.")
    return probeList


def readLink(fileName):
    print("reading link data...")
    listOfLink =[]
    with open(fileName, newline='') as csvfile:
        link = csv.reader(csvfile)
        for row in link:            
            shape =[]
            for coord in row[14].split('|'):
                lat, lon, _ = coord.split('/')
                shape.append((float(lat), float(lon)))
            alink = Link(row, shape)
            listOfLink.append(alink)
    # print(len(listOfLink))
    print("finished.")
    return listOfLink

# def calProbeDist(probeList):
#     print("start calculate probe distance.")
#     curProbe = probeList[0]
#     for i in range(1, len(probeList) - 1):
#         nextProbe = probeList[i]
#         h = calHaversine(curProbe.coord, nextProbe.coord)
#         curProbe.probeDist = h
#         # print(curProbe.probeDist)
#         curProbe = probeList[i]


    # print("finished.")

def calProbeDist(probeList):
    print("calculating probe distance...")

    prevId = '0'
    prevIndex = 0
    prevStartPoint,prevEndpoint = None, None
    for index, probe in enumerate(probeList):

        currId = probe.id
        if(currId != prevId):
                prevStartPoint = probeList[prevIndex].coord
                if(index != 0):
                    prevEndpoint = probeList[index - 1].coord
                if(prevId != '0'):
                    probeList[prevIndex].probeDist = calHaversine(prevStartPoint, prevEndpoint)
                    #print(curr_id, prevId, prevIndex, prevStartPoint,prevEndpoint)
                prevId = currId
                prevIndex = index
                
        
        if(index == len(probeList) - 1):
            prevStartPoint = probeList[prevIndex].coord
            prevEndpoint = probeList[index].coord
            probeList[prevIndex].probeDist = calHaversine(prevStartPoint, prevEndpoint)

    print("finished.")

def calHaversine(point1, point2):                             
    lat1 = point1[0]
    lon1 = point1[1]
    lat2 = point2[0]
    lon2 = point2[1]

    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    lat = lat2 - lat1
    lon = lon2 - lon1

    a = sin(lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    calHaversine =  6371000 * c  # earth radius = 6371000

    return calHaversine

def calCandidate(probeList, listOfLink):
    print("calculating candidate link for probe...")
    probeDist = None
    for probe in probeList:
            if(probe.probeDist != None):
                probeDist = probe.probeDist
            min = sys.maxsize
            probePoint = probe.coord
            x, y = None, None
            # print(probe_point)

            for link in listOfLink:
                
                linkPoint = link.coord[0]
                # print(temp_link_point)
                if(calHaversine(probePoint,linkPoint) > probeDist):
                    continue

                minDist = sys.maxsize                      
                refNode = None
                directionOfTravel = None   
                for i in range(len(link.coord)-1):

                    segPoints = link.coord
                    currPoint = segPoints[i]
                    nextPoint = segPoints[i+1]
                    tSegment = Segment(currPoint, nextPoint)  

                    projPoint= calProjection(probePoint, tSegment)

                    dist = calHaversine(probePoint, projPoint)

                    if dist < minDist:
                        minDist = dist
                        x = projPoint[0] 
                        y = projPoint[1]
                        # print(currPoint)
                        # print(nextPoint)

                if minDist < 20:
                    prob = norm.pdf(minDist,0,20)
                    probe.candidateLink.append([minDist, prob, (x, y), link.id]) 
                    probe.refNode = link.coord[0]
                    probe.direction = link.direction
    print("finished.")

def calProjection(probePoint, segPoints):
    
    x = probePoint[0]
    y = probePoint[1]
    x1, y1 = segPoints.s1[0], segPoints.s1[1]
    x2, y2 = segPoints.s2[0], segPoints.s2[1]

    tmp = (x2 - x1) * (x - x1) + (y2 - y1) * (y - y1); 
    if (tmp <= 0):
        return segPoints.s1

    d2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1); 
    if (tmp >= d2): 
        return segPoints.s2

    r = tmp / d2; 
    px = x1 + (x2 - x1) * r; 
    py = y1 + (y2 - y1) * r;

    return (px, py)

def pointMatch(probeList):
    print("calculating match points...")
    for index, currProbe in enumerate(probeList): 
        # print(len(currProbe.candidateLink))
        if len(currProbe.candidateLink) == 0:          
            continue

        if index == 0:
            max = -1
            maxCandidate = tuple()
            for candidate in currProbe.candidateLink:
                if candidate[1] > max:
                    max = candidate[1]
                    maxCandidate = candidate

            currProbe.matchedLink = maxCandidate
            # print(maxCandidate)
            continue

        prevProbe = probeList[index - 1]                         
        

        if not prevProbe.candidateLink or currProbe.id != prevProbe.id:

            max = -1
            maxCandidate = tuple()
            for candidate in currProbe.candidateLink:

                if candidate[1] > max:
                    max = candidate[1]
                    maxCandidate = candidate

            currProbe.matchedLink = maxCandidate
            continue



        d = calHaversine(currProbe.coord, prevProbe.coord)
        Fs = None
        maxFs = -1

        for currCandidate in currProbe.candidateLink:

            currMax = -1
            TempProb = 1    
            for prevCandidate in prevProbe.candidateLink:
                w = calHaversine(currCandidate[2], prevCandidate[2])
                if w == 0:
                    w = 0.1 
                TransProb = d / w

                Fs = prevCandidate[1] + currCandidate[1] * TempProb * TransProb
                
                if Fs > currMax:
                    currMax = Fs
            currCandidate[1] = currMax
            
            if currMax >maxFs:
                maxFs = currMax
                maxMatchedCandidate = currCandidate

        currProbe.matchedLink = maxMatchedCandidate                           
        # print(maxMatchedCandidate)
    print("finished.")

def output(fileName, probeList, listOfLink):

    sampleID = None
    dateTime = None
    sourceCode = None
    latitude = None
    longitude = None
    altitude = None
    speed = None
    heading = None
    linkPVID = None
    direction = None
    distFromRef = None
    distFromLink = None

    with open(fileName,'w', newline ='') as csvfile:
        output = csv.writer(csvfile)

        for probe in probeList:
        
            if not probe.candidateLink:
                continue

            sampleID = probe.id
            dateTime = probe.time
            sourceCode = probe.source
            latitude = probe.coord[0]
            lontitude = probe.coord[1]
            altitude = probe.alt
            speed = probe.speed
            heading = probe.heading
            linkPVID = probe.matchedLink[3]
            direction = probe.direction
            distFromRef = calHaversine(probe.coord, probe.refNode)
            distFromLink = probe.matchedLink[0]

            output.writerow((sampleID,dateTime,sourceCode,latitude,lontitude,altitude,speed,heading,linkPVID,direction,distFromRef,distFromLink))
    print("output finished.")

def main():
    probeReadNumber = 10000
    ProbeFile, LinkFile = readfileName()
    probeList = readProbe(ProbeFile, probeReadNumber)
    calProbeDist(probeList)
    # for probe in probeList:
    #     print(probe.probeDist)
    listOfLink = readLink(LinkFile)
    calCandidate(probeList, listOfLink)
    pointMatch(probeList)
    outputName = "Partition6467MatchedPoints.csv"
    output(outputName, probeList, listOfLink)


if __name__ == '__main__':
    main()