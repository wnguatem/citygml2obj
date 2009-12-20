#General modules:
import sys, os
import StringIO

#lxml for parsing gml:
from lxml import etree

#OGR for performing crs transformation
from osgeo import ogr

#server modules:
import _mysql
import datetime
from mod_python import util

#-- Global variables

# It will be assumed the gml-model is in SEPSG. TEPSG should be the epsg code from bing.
SEPSG, TEPSG = 28992,4326

# some namespaces for the gml parsing
GML = "{%s}" % 'http://www.opengis.net/gml'
CGML = "{%s}" % 'http://www.citygml.org/citygml/1/0/0'

def main(req,INFILE,OUTFILE,INFILE_DB,OUTFILE_DB):
    """
    Performs conversion, adds the model to DB, and redirects the user back to the main page. Note that this function is made to be called from a browser using mod_python et all.
    Input:
    - req: mod_python specific (something with the current http Request)
    - INFILE: the location of the cityGML file
    - OUTFILE: where to put the .obj file
    - INFILE_DB: reference string for the gml file to put in DB
    - OUTFILE_DB: reference string for the obj file to put in DB
    Output:
    - Redirects user to main php script 
    """
    data = convert(INFILE, OUTFILE)

    cPointLat,cPointLong,nof = data
    
    insertDB(OUTFILE_DB,cPointLat,cPointLong,INFILE_DB,nof)

    util.redirect(req, '../3d_bing_maps_viewer.php')


def insertDB(objFilePath,cPointLat,cPointLong,gmlFilePath,nof):
    """
    Insert information about uploaded file into mysql db
    Input:
    - objFilePath: reference string for the gml file
    - cPointLat: Latitude of the model in WGS84
    - cPointLong: Longitude of the model in WGS84 
    - gmlFilePath: reference string for the obj file
    - nof: Number of features in the model
    Output:
    - the above info will be in the DB
    """
    # Required information to connect to DB
    host = 'localhost'
    user = 'root'
    password = '1234'
    dbname = 'vis3'     
    
    # make DB connection
    db = _mysql.connect(host,user,password,dbname)

    # get current date
    now = datetime.datetime.now()
    date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    
    # Put information in DB
    db.query("""INSERT INTO bingModel (obj,cPointLat,cPointLong,gml,nof,date)
VALUES ('"""+str(objFilePath)+"""',"""+str(cPointLat)+""","""+str(cPointLong)+""",'"""+str(gmlFilePath)+"""',"""+str(nof)+""",'"""+date+"""')""")   

def transformPoint(sEPSG, tEPSG, xypoint):
    """
    Will transform the coordinates of a given point in sEPSG to the coordinates in tEPSG. Note that the height of the point in the sEPSG will be taken 0.
    Input:
    - sEPSG: source EPSG-code
    - tEPSG: target EPSG-code
    - xypoint: coordinates of the point in sEPSG
    Output:
    - Coordinates in tEPSG
    """
    #source SRS 
    sSRS=ogr.osr.SpatialReference()
    # circumvent a bug in ogr/proj4 that introduces a shift, when transforming from RD New to WGS84
    if (sEPSG == 28992):
        sSRS.ImportFromWkt("""
            PROJCS["Amersfoort / RD New",
            GEOGCS["Amersfoort",
                DATUM["Amersfoort",
                    SPHEROID["Bessel 1841",6377397.155,299.1528128,
                        AUTHORITY["EPSG","7004"]],
                    AUTHORITY["EPSG","6289"]],
                PRIMEM["Greenwich",0,
                    AUTHORITY["EPSG","8901"]],
                UNIT["degree",0.01745329251994328,
                    AUTHORITY["EPSG","9122"]],
                TOWGS84[565.237,50.0087,465.658,-0.406857,0.350733,-1.87035,4.0812],
                AUTHORITY["EPSG","4289"]],
            UNIT["metre",1,
                AUTHORITY["EPSG","9001"]],
            PROJECTION["Oblique_Stereographic"],
            PARAMETER["latitude_of_origin",52.15616055555555],
            PARAMETER["central_meridian",5.38763888888889],
            PARAMETER["scale_factor",0.9999079],
            PARAMETER["false_easting",155000],
            PARAMETER["false_northing",463000],
            AUTHORITY["EPSG","28992"]]
        """)
    else:
        sSRS.ImportFromEPSG(sEPSG) 

    #target SRS 
    tSRS=ogr.osr.SpatialReference() 
    tSRS.ImportFromEPSG(tEPSG) 

    poCT=ogr.osr.CoordinateTransformation(sSRS,tSRS) 

    x, y = xypoint
    return poCT.TransformPoint(x,y,0.)
    
def convert(infile, outfile):
    """
    Function that converts simple citygml to .obj
    Input:
    - infile: the location of the cityGML file
    - outfile: where to put the .obj file
    Output:
    - Wavefront .OBJ file, including model location and number of features in the header (first 4 lines)
    - data: tuple containing lat/long of the model in WGS84 and the number of features
    """

    def xyOffset(plist):
        """ 
        Calculates center-point of the model.
        """
        x = (min(plist[0])+max(plist[0]))/2
        y = (min(plist[1])+max(plist[1]))/2
        return (x,y)

    # parse the infile
    print 'Reading file...'
    tree = etree.parse(infile)
    # for storing vertices:
    vert = StringIO.StringIO()
    # for storing faces:
    fac = StringIO.StringIO()

    pointlist = []
    count = 0
    # loop through the ciyObjectMember elements, for all faces put the points in a set (so that they are not duplicated). Then extend the pointlist with that set. This gives every unique point an index
    for cOM in tree.iter(CGML+"cityObjectMember"):
        count += 1
        s = set([])
        for lR in cOM.iter(GML+"LinearRing"):
            for pos in lR:
                s.update([pos.text])
        pointlist += list(s)
        # with pointlist we can generate the face-lines in the .obj file:
        for lR in cOM.iter(GML+"LinearRing"):
            print >>fac, "f",
            for pos in range(len(lR)-1):
                print >>fac, pointlist.index(lR[pos].text)+1,
            print >>fac

    print 'translating points...'
    # initialize
    pointlistF = []
    for t in range(3):
        pointlistF.append([])

    # convert pointlist to floating points
    for v in pointlist:
        c = v.split()
        pointlistF[0].append(float(c[0]))
        pointlistF[1].append(float(c[1]))
        pointlistF[2].append(float(c[2]))

    # calculate offset
    offset = xyOffset(pointlistF)

    # Generate the vertex-lines in the .obj file. Also translate the points using the OFFSET
    for i in range(len(pointlistF[0])):
        print >>vert, "v %.7f %.7f %.2f" % ( pointlistF[0][i]-offset[0], pointlistF[1][i]-offset[1], pointlistF[2][i] )

    # write the file
    f = open(outfile, 'w')
    lg, lt, h = transformPoint(SEPSG,TEPSG,offset)
    f.write("#Location in WGS84 (lat,long):\n#%.9f,%.9f\n#Number of features:\n#%d\n" % (lt, lg, count))
    f.write(vert.getvalue())
    f.write(fac.getvalue())
    f.close()
    
    print 'Applied offset: %.9f, %.9f' % offset
    print 'EPSG %d location: %.9f, %.9f' % (TEPSG,lt,lg)

    return (lt, lg, count)

#if __name__ == "__main__":
#    main(INFILE,OUTFILE,cPointLat,cPointLong,nof)
