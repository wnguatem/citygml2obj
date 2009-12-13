# TODO: rotate coordinates by 90 degree clockwise around the X-axis
# TODO: triangulate/quadratize polygons
import sys, os
from lxml import etree
import StringIO

#-- Global variables
OUTFILE = "footprints_extruded.obj"
INFILE = "footprints_extruded.xml"
# Offset to translate the object from global coordinates to 'local' coordinates
OFFSET = [85430.08,446051.26] #specific for tu-delft campus

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

    # parse the infile
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

    # Generate the vertex-lines in the .obj file. Also translate the points using the OFFSET
    for v in pointlist:
        c = v.split()
        print >>vert, "v %.7f %.7f %s" % ( float(c[0])-OFFSET[0], float(c[1])-OFFSET[1], c[2] )

    # write the file
    f = open(OUTFILE, 'w')
    f.write("# location in WGS84 (lat,long): 51.9985,4.374211\n") # specific for the tu-delt campus
    f.write(vert.getvalue())
    f.write(fac.getvalue())
    f.close()

if __name__ == "__main__":
    main(sys.argv[1:])
