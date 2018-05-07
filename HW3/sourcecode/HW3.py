import sys
import math
import json
import random
import urllib
from urllib import request
from PIL import Image
import io

BINGMAP_KEY = "Ag_uivCHgdv2mkfQAFWg1GOW4I3zOANmwd-ew51vLfKxFIbZygjkitFoi7sPwMi1"

EARTH_RADIUS = 6378137;
MIN_LATITUDE = -85.05112878;
MAX_LATITUDE = 85.05112878;
MIN_LONGITUDE = -180;
MAX_LONGITUDE= 180;

def clip(n,minValue, maxValue):
    return min(max(n, minValue), maxValue)

def mapSize(levelOfDetail):
    return int(256 << levelOfDetail)

def groundResolution(latitude, levelOfDetail):
    latitude = clip(latitude, MIN_LATITUDE, MAX_LATITUDE)
    
    return math.cos(latitude * math.pi / 180) * 2 * math.pi * EARTH_RADIUS / mapSize(levelOfDetail)

def mapScale(latitude, levelOfDetail, screenDpi):
    return groundResolution(latitude, levelOfDetail) * screenDpi / 0.0254

def latLongToPixelXY(latitude, longitude, levelOfDetail):
    latitude = clip(latitude, MIN_LATITUDE, MAX_LATITUDE);
    longitude = clip(longitude, MIN_LONGITUDE, MAX_LONGITUDE);

    x = (longitude + 180) / 360
    sinLatitude = math.sin(latitude * math.pi / 180)
    y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi);

    mapsize = mapSize(levelOfDetail);
    pixelX = int(clip(x * mapsize + 0.5, 0, mapsize - 1))
    pixelY = int(clip(y * mapsize + 0.5, 0, mapsize - 1))

    return pixelX, pixelY   

def pixelXYToLatLong(pixelX, pixelY, levelOfDetail):
    mapSize = mapSize(levelOfDetail)
    x = (clip(pixelX, 0, mapSize - 1) / mapSize) - 0.5
    y = 0.5 - (clip(pixelY, 0, mapSize - 1) / mapSize)

    latitude =int(90 - 360 * math.atan(math.exp(-y * 2 * Math.PI)) / Math.pi)
    longitude = int(360 * x)

    return latitude, longitude

def pixelXYToTileXY(pixelX, pixelY):
    tileX = int(pixelX / 256)
    tileY = int(pixelY / 256)

    return tileX, tileY

def tileXYToPixelXY(tileXY):
    tileX, tileY = tileXY
    pixelX = tileX * 256
    pixelY = tileY * 256

    return pixelX, pixelY

def tileXYToQuadKey(tileX, tileY, levelOfDetail):
    quadKey = ''
    for i in range(levelOfDetail, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if ((tileX & mask) != 0):
            digit += 1
        if ((tileY & mask) != 0):
            digit += 2
        quadKey += str(digit)

    return quadKey

def latLongToTileXY(latitude, longitude, levelOfDetail):
    pixelX, pixelY = latLongToPixelXY(latitude, longitude, levelOfDetail)
    return (pixelX, pixelY), pixelXYToTileXY(pixelX, pixelY)


def calCommonLevel(lat1, lon1, lat2, lon2):
    LevelDic = {
    13: 2097152,
    14: 4194304,
    15: 8388608,
    16: 16777216,
    17: 33554432,
    18: 67108864, 
    19: 134217728, 
    20: 268435456, 
    21: 536870912
    }
    point1 = [lat1, lon1]
    point2 = [lat1, lon2]
    point3 = [lat2, lon1]
    point4 = [lat2, lon2]
    listSamplePoint = [point1, point2, point3, point4]
    listLevelOfCorner = list(map(getMaxLevelOfPoint, listSamplePoint))
    assumeLevel = max(listLevelOfCorner)
    
    PixelOfLevel = LevelDic[assumeLevel]
    latGapAssumeLevel = MAX_LATITUDE * 2 / (PixelOfLevel / 256)
    lonGapAssumeLevel = MAX_LONGITUDE * 2 / (PixelOfLevel / 256)
    
    sampleNumlat = (lat1 - lat2) / latGapAssumeLevel
    sampleNumlon = (lon2 - lon1) / lonGapAssumeLevel
    sampleNum = int(sampleNumlat * sampleNumlon / 4)

    exp = 10000000
    for tmp in range(0, sampleNum):
        lat = random.randrange(int(lat2 * exp), int(lat1 * exp), int(latGapAssumeLevel * exp))
        lon = random.randrange(int(lon1 * exp), int(lon2 * exp), int(lonGapAssumeLevel * exp))
        listSamplePoint.append( [lat / exp, lon / exp] )

    levelOfDetail = max(list(map(getMaxLevelOfPoint, listSamplePoint)))

    return levelOfDetail

def quadKeyToTileXY(quadkeytail):

    size = len(quadkeytail)
    x1_offset = 0
    y1_offset = 0
    x4_offset = 256
    y4_offset = 256
    offset = 256

    for index in range(size):
        position = quadkeytail[index]
        offset /= 2
        if position == '0':
            x4_offset -= offset
            y4_offset -= offset

        elif position == '1':
            x1_offset += offset
            y1_offset = y1_offset
            x4_offset = x4_offset
            y4_offset -= offset

        elif position == '2':
            x1_offset = x1_offset
            y1_offset += offset
            x4_offset -= offset
            y4_offset = y4_offset  
          
        elif position == '3':
            x1_offset += offset
            y1_offset += offset

    return (x1_offset,y1_offset, x4_offset, y4_offset)

def getMaxLevelOfPoint(point):
    latitude, longitude = point[0], point[1]
    levelOfDetail = 21
    flag = True

    while flag:
        url = "http://dev.virtualearth.net/REST/V1/Imagery/Metadata/Aerial/%f,%f?zl=%d&key=%s" % (latitude, longitude, levelOfDetail, BINGMAP_KEY)
        json_file = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
        if json_file["resourceSets"][0]["resources"][0]["vintageStart"] == None or json_file["resourceSets"][0]["resources"][0]["vintageStart"] == "null":
            levelOfDetail -= 1
        else:
            flag = False

    return levelOfDetail

def makeImage(tileXY1, tileXY2, levelOfDetail):
    x1 = tileXY1[0]
    y1 = tileXY1[1]
    x2 = tileXY2[0]
    y2 = tileXY2[1]
    imageWidth = (x2 - x1 + 1) * 256
    imageHeight = (y2 - y1 + 1) * 256
    color = (255, 255, 255, 0)
    image = Image.new('RGBA', (int(imageWidth), int(imageHeight)), color)

    emptyquadkey = "000000000000000000000"                                                             
    emptyImage = getImage(emptyquadkey)
    emptyImageColor = emptyImage.getcolors()

    offsetY = 0
    for y in range(y1, y2 + 1):
        offsetX = 0
        for x in range(x1, x2 + 1):
            quadkey = tileXYToQuadKey(x, y, levelOfDetail)
            # print(quadkey)                   
            img = getImage(quadkey)

            quadkeytail = ""
            while img.getcolors() == emptyImageColor:
                quadkeytail = str(quadkey[-1]) + quadkeytail
                quadkey = quadkey[:-1]
                img = getImage(quadkey)
            if quadkeytail != "":
                bound = quadKeyToTileXY(quadkeytail)      
                img = img.crop(bound)
                img = img.resize((256,256))
            image.paste(img, (offsetX, offsetY))
            img.close()

            offsetX += 256
        offsetY += 256


    return image

def getImage(quadkey):
    url = "http://ecn.t3.tiles.virtualearth.net/tiles/a" + quadkey + ".jpeg?g=5682" 
    file = io.BytesIO(urllib.request.urlopen(url).read())                              
    return Image.open(file)



def cutImage(image, pixelXY1, pixelXY2,tileXY1, levelOfDetail):

    leftBound, topBound = tileXYToPixelXY(tileXY1)
    print(leftBound, topBound, pixelXY1[0], pixelXY1[1], pixelXY2[0], pixelXY2[1])
    leftCutBound = pixelXY1[0] - leftBound
    topCutBound = pixelXY1[1] - topBound
    rightCutBound = pixelXY2[0] -leftBound
    bottomCutBound = pixelXY2[1] -topBound

    bound = (leftCutBound, topCutBound, rightCutBound, bottomCutBound)
    cutImage = image.crop(bound)

    return cutImage

def getInput():
    if len(sys.argv) == 2:
        pointList = sys.argv[1].split(',')
        lat1, lon1, lat2, lon2 = map(lambda x : float(x), pointList)
    else:
        print("Wrong format.\nPlease input the <lat1,lon1,lat2,lon2>.")
        sys.exit(1)

    return lat1, lon1, lat2, lon2

def main():
    lat1, lon1, lat2, lon2 = getInput()
    print("The longitude and latitude of the bounding box is\n<%s, %s, %s, %s>" % (lat1, lon1, lat2, lon2))
    print("Calculating the common level...")
    levelOfDetail = calCommonLevel(lat1, lon1, lat2, lon2)
    print("The level of the bounded box is %s." % (levelOfDetail))
    pixelXY1, tileXY1 = latLongToTileXY (lat1, lon1, 20)
    pixelXY2, tileXY2 = latLongToTileXY (lat2, lon2, 20)
    print("Creating image...")
    image = makeImage(tileXY1, tileXY2, levelOfDetail)
    print("Image created.")
    image.save("./image.jpg")
    print("Creating cut image...")
    cutimage = cutImage(image, pixelXY1, pixelXY2,tileXY1, levelOfDetail) 
    cutimage.save("./cutImage.jpg")
    print("Cut image created.")

if __name__ == '__main__':
    main()

