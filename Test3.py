from lxml import html
import cssselect
from math import radians, cos, sin, asin, sqrt, degrees
from matplotlib.pyplot import *
import datetime

def haversine(coord1, coord2):
  # convert decimal degrees to radians
  lon1, lat1, lon2, lat2 = map(radians, [float(coord1[1]), float(coord1[0]), float(coord2[1]), float(coord2[0])])

  # haversine formula
  dlon, dlat = tuple([float(lon2 - lon1), float(lat2 - lat1)])
  a = sin(dlat/2)**2 + (cos(lat1) * cos(lat2) * sin(dlon/2)**2)
  c = 2 * asin(sqrt(a))
  r = 6371 # Radius of earth in kilometers. Use 3956 for miles
  return c*r

def euc_dis(coord1, coord2):
    dx1, dy1, dx2, dy2 = tuple([float(coord1[1]), float(coord1[0]), float(coord2[1]), float(coord2[0])])
    x = (dx1 - dx2) * cos((dy1 + dy2)/2)
    y = dy1 - dy2
    return sqrt(x**2 + y**2)

k1 = "doc.kml"
k2 = "2doc.kml"

def get_data(fkml):
    data = open(fkml, 'r').read()
    doc = html.fromstring(data.encode())
    prev_coord = []
    prev_time = None
    total = 0
    dist = []
    time = []
    for pm in doc.cssselect('Placemark'):
        tmp = pm.cssselect('track')
        name = pm.cssselect('name')[0].text_content()
        if len(tmp):
            # Track Placemark
            tmp = tmp[0]  # always one element by definition
            for desc in tmp.iterdescendants():
                content = desc.text_content()
                if desc.tag == 'when':
                    y = content.split("T")[1].replace("Z", "").split(":")
                    if prev_time == None:
                        prev_time = datetime.datetime(1, 1, 1, int(y[0]), int(y[1]), int(y[2].split(".")[0]), int(float(y[2].split(".")[1]) * 1000))
                    t = (datetime.datetime(1, 1, 1, int(y[0]), int(y[1]), int(y[2].split(".")[0]), int(float(y[2].split(".")[1]) * 1000)) - prev_time).total_seconds()
                    time.append(t/60)
                    #prev_time = datetime.datetime(1, 1, 1, int(y[0]), int(y[1]), int(y[2].split(".")[0]), int(float(y[2].split(".")[1]) * 1000))
                elif desc.tag == 'coord':
                    if prev_coord == []:
                        prev_coord = content.split(" ")
                    dis = haversine(content.split(" "), prev_coord)#haversine(float(content.split(" ")[1]), float(content.split(" ")[0]), float(prev_coord[1]), float(prev_coord[0]))
                    #print(content.split(" "), prev_coord)
                    total = total + dis
                    dist.append(total)
                    prev_coord = content.split(" ")
                    #print(dis)
    return dist, time

def get_speed(time, dist):
    speed = []
    for i in range(1, 644):
        s = (dist[i-1] - dist[i+1])/((time[i-1] - time[i+1])/60)
        speed.append(s)
    return speed


dist1, time1 = get_data(k1)
speed1 = get_speed(time1, dist1)

plot(time1[0:-2], speed1)
xlabel("Time (Seconds)")
ylabel("Speed (Kmph)")

dist2, time2 = get_data(k2)
speed2 = get_speed(time2, dist2)

plot(time2[0:-2], speed2)
legend(["28-08-2020", "26-08-2020"])
