try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import numpy
import pandas
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# plat and plong are locations from the matlab file
plat = numpy.loadtxt(open("rainfalllat3.csv", "rb"), delimiter=",")
plong = numpy.loadtxt(open("rainfalllong3.csv", "rb"), delimiter=",")

# output file saves all the
output_file = []
used_locations = []

# websearch takes in a in_lat and in_lon and searches the nws website for that location. It pulls the 24hr data and add it to the outfile.
def webserach(in_lat, in_lon):
    url = "https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/cgi_readH5.py?lat=" + str(in_lat) + "&lon=" + str(in_lon) + "&type=pf&data=depth&units=english&series=pds"
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    a = html.find('quantiles')
    if (a == -1):
        return -1
    b = html.find(';', a)
    exec(html[a:b], globals())
    output_file.append(quantiles[9])
    return ''

# inradius takes in a in_lat and in_long and starts with a given radius. It will try nearby locations until it finds a relatively close location and adds it. It documents the actual location used in a file
def inradius(in_lat, in_long, radius):
    if (radius > 3):
        output_file.append([])
        used_locations.append([0,0])
        return
    lats = [in_lat, in_lat + radius, in_lat - radius]
    longs = [in_long, in_long + radius, in_long - radius]
    for lat1 in lats:
        for long1 in longs:
            output = webserach(lat1, long1)
            if (type(output) != int):
                used_locations.append([lat1,long1])
                return 0
    return inradius(in_lat, in_long, radius + 0.01)

# runs on all the locations
print()
for i in range(len(plat)):
    lat = plat[i]
    lon = plong[i]
    inradius(lat, lon, 0.01)
    if (i%100 == 0):
        print(i)

# writes to rainfall.csv and used_locations.csv
df = pandas.DataFrame(output_file)
df.to_csv('rainfall.csv', header= False, index= False)
df2 =  pandas.DataFrame(used_locations)
df2.to_csv('used_locations.csv', header= False, index= False)
