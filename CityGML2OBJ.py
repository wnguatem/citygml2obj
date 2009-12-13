# TODO: rotate coordinates by 90 degree clockwise around the X-axis
# TODO: triangulate/quadratize polygons
import sys, os
from lxml import etree
import StringIO

#-- Global variables
OUTFILE = "footprints_extruded.obj"
INFILE = "footprints_extruded.xml"
# Offset to translate the object from global coordinates to 'local' coordinates
# OFFSET = [85430.08,446051.26] #specific for tu-delft campus

GML = "{%s}" % 'http://www.opengis.net/gml'
CGML = "{%s}" % 'http://www.citygml.org/citygml/1/0/0'

def main(argv):
    convert(INFILE, OUTFILE)
    
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
    pointlistF = []
    for t in range(3):
        pointlistF.append([])

    # convert pointlist to floating points
    for i, v in enumerate(pointlist):
        c = v.split()
        pointlistF[0].append(float(c[0]))
        pointlistF[1].append(float(c[1]))
        pointlistF[2].append(float(c[2]))

    # calculate offset
    offset = xyOffset(pointlistF)

    # Generate the vertex-lines in the .obj file. Also translate the points using the OFFSET
    for i in range(len(pointlistF[0])):
        print >>vert, "v %.7f %.7f %.2f" % ( pointlistF[0][i]-offset[0], pointlistF[1][i]-offset[1], pointlistF[2][i] )

    print 'Writing file...'
    # write the file
    f = open(OUTFILE, 'w')
    #f.write("# location in WGS84 (lat,long): 51.9985,4.374211\n") # specific for the tu-delt campus
    f.write(vert.getvalue())
    f.write(fac.getvalue())
    f.close()

if __name__ == "__main__":
    main(sys.argv[1:])
