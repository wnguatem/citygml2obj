# TODO: rotate coordinates by 90 degree clockwise around the X-axis
# TODO: triangulate/quadratize polygons
import sys, os
from lxml import etree
import StringIO
from osgeo import ogr

#-- Global variables
OUTFILE = "footprints_extruded.obj"
INFILE = "footprints_extruded.xml"
SEPSG, TEPSG = 28992,4326
# Offset to translate the object from global coordinates to 'local' coordinates
# OFFSET = [85430.08,446051.26] #specific for tu-delft campus

GML = "{%s}" % 'http://www.opengis.net/gml'
CGML = "{%s}" % 'http://www.citygml.org/citygml/1/0/0'

def main(argv):
    convert(INFILE, OUTFILE)

def transformPoint(sEPSG, tEPSG, xypoint):
    #source SRS 
    sSRS=ogr.osr.SpatialReference()
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
        infile
        outfile
    Output:
        - Wavefront .OBJ file
    """

    def xyOffset(plist):
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
    
    # loop through the ciyObjectMember elements, for all faces put the points in a set (so that they are not duplicated). Then extend the pointlist with that set. This gives every unique point an index
    for cOM in tree.iter(CGML+"cityObjectMember"):
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
    f = open(OUTFILE, 'w')
    lg, lt, h = transformPoint(SEPSG,TEPSG,offset)
    f.write("#Location in WGS84 (lat,long): \n#%.9f,%.9f\n" % (lt, lg))
    f.write(vert.getvalue())
    f.write(fac.getvalue())
    f.close()
    
    print 'Applied offset: %.9f, %.9f' % offset
    print 'EPSG %d location: %.9f, %.9f' % (TEPSG,lt,lg)

if __name__ == "__main__":
    main(sys.argv[1:])
