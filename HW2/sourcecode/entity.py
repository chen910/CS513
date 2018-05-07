class Probe(object):
    def __init__(self, row):
        self.coord = (float(row[3]), float(row[4]))

        self.id =row[0]
        self.time = row[1]
        self.source = row[2]
        self.alt = row[5]
        self.speed = row[6]
        self.heading = row[7]
        self.probeDist = None
        self.direction = None
        self.refNode = None
        self.candidateLink = []
        self.matchedLink = tuple()


class Link(object):
    def __init__(self, row, shape):
        self.id = row[0]
        self.length = row[3]
        self.direction = row[5]

        self.coord = shape

class Segment(object):

    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2

class MatchedProbe(object):
    def __init__(self,row):
        self.lat = row[3]
        self.lon = row[4]
        self.sampleID = row[0]
        self.dateTime = row[1]
        self.sourceCode = row[2]
        self.alt = float(row[5])
        self.speed = row[6]
        self.heading = row[7]
        self.linkID = row[8]
        self.direction = row[9]
        self.distFromRef = float(row[10])
        self.distFromLink = float(row[11])
        self.elevation = None
        self.slope = None

class SlopeLink(object):
    def __init__(self, row, shape, alt, slopeInfo):
        self.id = row[0]
        self.coord = shape
        self.alt = alt
        self.slopeinfo = slopeInfo
