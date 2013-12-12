import sys
import zipfile
from bisect import bisect_right
import numpy
import scipy.interpolate

from defs import *


class Map(object):
    def __init__(self):
        self.spline = None
    
    def get_spline(self):
        if self.spline is None:
            lons = numpy.mean(numpy.array([self.longitudes[:-1], self.longitudes[1:]]), axis=0)
            lats = numpy.mean(numpy.array([self.latitudes[:-1], self.latitudes[1:]]), axis=0)
            self.spline = scipy.interpolate.RectBivariateSpline(lats, lons, self.data)
        
        return self.spline
    
    def scale(self, x):
        return (x / 999.0) * (self.maxval - self.minval) + self.minval
    
    def get_data_point(self, lat, lon):
        i = self.find_slot(self.latitudes, lat)
        j = self.find_slot(self.longitudes, lon)
        
        return self.scale(self.data[i][j])
    
    def get_all_points(self):
        pts = []
        for r in self.data:
            r2 = []
            for x in r:
                x2 = self.scale(x)
                r2.append(x2)
            pts.append(r2)
        return pts
    
    def find_slot(self, edges, x):
        pos = bisect_right(edges, x) - 1
        pos = pos % (len(edges) - 1)
        return pos

def load_map(filename):
    mp = Map()
    mp.name = filename
    try:
        f = open(filename, 'rt')
        zf = None
    except IOError:
        zipname = filename[:-9] + '.zip'
        zf = zipfile.ZipFile(zipname, 'r')
        f = zf.open(filename, 'r')
    
    while True:
        ln = f.readline().strip()
        if ln == '':
            break
        name,value = ln.split(',')
        setattr(mp, name, value)
    
    mp.width,mp.height = map(int, f.readline().strip().split(','))
    mp.longitudes = map(float, f.readline().strip().split(','))
    mp.latitudes = map(float, f.readline().strip().split(','))
    mp.minval,mp.maxval = map(float, f.readline().strip().split(',', 2)[:2])
    
    mp.data = numpy.loadtxt(f, dtype=numpy.int16, delimiter=',')
    
    f.close()
    if zf is not None:
        zf.close()
    
    return mp

def make_map(data, lons, lats, name):
    mp = Map()
    
    mp.name = name
    
    mp.width = len(lons)
    mp.height = len(lats)
    mp.longitudes = lons
    mp.latitudes = lats
    mp.data = data
    
    return mp

def create_map(width, height, data, name):
    mp= Map()
    mp.width = width
    mp.height = height
    mp.data = data
    mp.minval = 0
    mp.maxval = 999
    mp.name = name
    return mp

def save_map(mp):
    filename = mp.name + '.csv'
    f = open(filename, 'wt')
    print >>f, 'name,%s' % mp.name
    print >>f
    print >>f, '%d,%d' % (len(mp.longitudes), len(mp.latitudes))
    print >>f, '%s' % ','.join('%0.4f' % x for x in mp.longitudes)
    print >>f, '%s' % ','.join('%0.4f' % x for x in mp.latitudes)
    print >>f, '1,999'
    numpy.savetxt(f, mp.data, fmt='%.18e', delimiter=',', newline='\n')
    f.close()

def frange(x, y, jump):
    while x < y:
        yield x
        x += jump

def plot(mp):
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt

    map = Basemap(projection='mill', llcrnrlon=0,llcrnrlat=-90,urcrnrlon=360,urcrnrlat=90)
    
    map.drawcoastlines(linewidth=0.25)
    
    map.drawmeridians(numpy.arange(0,360,30))
    map.drawparallels(numpy.arange(-90,90,30))

    data = mp.data
    
    lons, lats = map.makegrid(mp.width, mp.height)
    x, y = map(*numpy.meshgrid(mp.longitudes, mp.latitudes))
    #clevs = range(200, 325, 5)
    clevs = list(frange(0, 8, 0.25))
    cs = map.contourf(x, y, data, clevs, cmap=plt.cm.jet)
    
    cbar = map.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('K')
    
    lon, lat = 174.7772, -41.2889
    xpt,ypt = map(lon,lat)
    map.plot(xpt,ypt,'bo')
    
    plt.title(mp.name)
    plt.gcf().set_size_inches(10,10)
    plt.savefig(mp.name + '.png',dpi=100)
    #plt.show()


def main():
    if len(sys.argv) > 2:
        start_year = int(sys.argv[1])
        stop_year = int(sys.argv[2])
    else:
        start_year = min(YEAR)
        stop_year = max(YEAR) + 1
    YEARS = range(start_year, stop_year)
    
    print 'Running from %d to %d' % (start_year, stop_year)
    var = 'tas'
    level = 0
    deg_lats = numpy.array(range(-90, 90)) + 0.5
    deg_lons = numpy.array(range(0, 360)) + 0.5
    diffsq_sum = numpy.zeros((180, 360))
    num_entries = 0
    m1 = 10000000
    m2 = 0
    for year in YEARS:
        model_data = {}
        
        deg_datas = []
        
        for model in MODELS:
            name = NAME % locals()
            mp = load_map(name)
            #model_data[model] = mp
            
            lon, lat = 174.7772, -41.2889
            temp = mp.get_data_point(lat, lon)
            temp2 = mp.scale(mp.get_spline().ev(lat, lon)[0])
            
            deg_data = mp.scale(mp.get_spline()(deg_lats, deg_lons))
            deg_datas.append(deg_data)
            m1 = min(m1, numpy.min(deg_data))
            m2 = max(m2, numpy.max(deg_data))
        mean_data = numpy.mean(deg_datas, axis=0)
        diffs = [data - mean_data for data in deg_datas]
        for d in diffs:
            diffsq_sum = diffsq_sum + numpy.square(d)
            num_entries += 1
    
    #print m1, m2
    
    var_data = diffsq_sum / num_entries
    sd_data = numpy.sqrt(var_data)
    m1 = numpy.min(sd_data)
    m2 = numpy.max(sd_data)
    sd_map = make_map(sd_data, deg_lons, deg_lats, 'sd %d-%d' % (min(YEARS), max(YEARS)))
    plot(sd_map)
    save_map(sd_map)
    print 'Mean variance was: %0.4f' % numpy.mean(var_data)


if __name__ == '__main__':
    main()
