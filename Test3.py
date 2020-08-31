from lxml import html
import cssselect
from math import radians, cos, sin, asin, sqrt, degrees
from matplotlib.pyplot import *
import datetime
import os

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

def get_speed(time, dist, accuracy):
    speed = []
    sub = int(accuracy/2)
    for i in range(0, len(dist)):
        if (i - sub) < 0 and (i + sub) < len(dist):
            s = (dist[i] - dist[i+sub])/((time[i] - time[i+sub])/60)
        elif (i - sub) > 0 and (i + sub) >= len(dist):
            s = (dist[i-sub] - dist[len(dist) - 1])/((time[i-sub] - time[len(dist) - 1])/60)
        elif (i - sub) < 0 and (i + sub) >= len(dist):
            s = (dist[i] - dist[len(dist) - 1])/((time[i] - time[len(dist) - 1])/60)
        else:# (i - sub) > 0 and (i + sub) < len(dist):
            s = (dist[i-sub] - dist[i+sub])/((time[i-sub] - time[i+sub])/60)
        speed.append(s)
    return speed

def get_running_times(running_threshold, speed, accuracy):
    over_threshold = []
    start = 0
    sub = accuracy/2
    im_high = False
    for i, d in enumerate(speed):
        if d >= running_threshold and not im_high:
            start = int(i - sub)
            im_high = True
        if im_high and d < running_threshold:
            im_high = False
            over_threshold.append([start, int(i + sub)])
    return over_threshold

def get_total_running_distance(dist, run_times):
    distance = 0
    for pair in run_times:
        distance = distance + abs(dist[pair[0]] - dist[pair[1]])
    return distance

def get_avg_speed(dist, time, run_times):
    avg = 0
    for pair in run_times:
        avg += (dist[pair[0]] - dist[pair[1]])/((time[pair[0]] - time[pair[1]])/60)
    return avg/len(run_times)

def get_top_speed_per_run_interval(speed, run_times):
    max_per_run = []
    for pair in run_times:
        max_per_run.append(max(speed[pair[0]:pair[1]]))
    return max_per_run
def main():
    running_threshold = 8
    accuracy = 26
    ks = [x for x in os.listdir(os.getcwd()) if os.path.isfile(x) and x.endswith(".kml")]
    for k in ks:
        dist, time = get_data(k)
        speed = get_speed(time, dist, accuracy)
        run_times = get_running_times(running_threshold, speed, accuracy)
        print("Summary for {}:".format(k))
        print("\tTotal Distance Ran: {:.2f} km".format(get_total_running_distance(dist, run_times)))
        print("\tAverage Running Speed: {:.2f} km/h".format(get_avg_speed(dist, time, run_times)))
        for i, r in enumerate(get_top_speed_per_run_interval(speed, run_times)):
            print("\tMax Speed for interval {}: {:.2f} km/h".format(i+1, r))
        figure(0)
        plot(dist, speed)
        figure(1)
        plot(dist, time)
        figure(2)
        plot(time, speed)
        
    figure(0)
    xlabel("Distance (Kilometers)")
    ylabel("Speed (Km/h)")
    legend(ks)
    figure(1)
    xlabel("Distance (Kilometers)")
    ylabel("Time (Minutes)")
    legend(ks)
    figure(2)
    xlabel("Time (Minutes)")
    ylabel("Speed (Km/h)")
    legend(ks)
    show()
if __name__ == "__main__":
    main()