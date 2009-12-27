#General modules:
import sys, os
import StringIO

#lxml for parsing gml:
from lxml import etree

#OGR for performing crs transformation
from osgeo import ogr

#server modules:
if __name__ != "__main__":
    import _mysql
    import datetime
    from mod_python import util

#-- Global variables

# It will be assumed the gml-model is in SEPSG. TEPSG should be the epsg code from bing.
SEPSG, TEPSG = 28992,4326

# some namespaces for the gml parsing
GML = "{%s}" % 'http://www.opengis.net/gml'
CGML = "{%s}" % 'http://www.citygml.org/citygml/1/0/0'

def main(INFILE,OUTFILE):
    """
    Performs conversion, adds the model to DB, and redirects the user back to the main page. This function is called when executing this script from the command line, using the first argument as INFILE, and the second argument as OUTFILE
    Input:
    - req: mod_python specific (something with the current http Request)
    - INFILE: the location of the cityGML file
    - OUTFILE: where to put the .obj file
    Output:
    - some info on the shell
    - .obj file
    """
    data = convert(INFILE, OUTFILE)

    cPointLat,cPointLong,nof = data
    
def index(req,INFILE,OUTFILE,INFILE_DB,OUTFILE_DB):
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

    util.redirect(req, '3d_bing_maps_viewer.php')

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

    def checkBottomFace(data):
        """ Check if current face is bottom face, data contains [x,y,z]"""

        bottomFace = True
        
        for p in data:
            if p[2]!=0:
                bottomFace = False

        return bottomFace

    def getArea(polygon):
        """ Get area of a polygon, polygon list looks like [[x1,y1,z1],[x2,y2,z2]] """
        # soruce for calculation method: http://en.wikipedia.org/wiki/Centroid

        Asum = 0
        for p in range(0,len(polygon)):
            if p==len(polygon)-1:
                # go back again to first point
                Asum += (polygon[p][0]*polygon[0][1])-(polygon[0][0]*polygon[p][1])
            else:
                Asum += (polygon[p][0]*polygon[p+1][1])-(polygon[p+1][0]*polygon[p][1])

        return 0.5*Asum

    def getCentroid(Area,polygon):
        """ returns centroid of polygon in x,y coordinates"""
        # soruce for calculation method: http://en.wikipedia.org/wiki/Centroid

        Sum = 0
        for p in range(0,len(polygon)):
            if p==len(polygon)-1:
                # go back again to first point
                Sum += (polygon[p][0]+polygon[0][0])*(polygon[p][0]*polygon[0][1]-polygon[0][0]*polygon[p][1])
            else:
                Sum += (polygon[p][0]+polygon[p+1][0])*(polygon[p][0]*polygon[p+1][1]-polygon[p+1][0]*polygon[p][1])

        Cx = (1/(6*Area))*Sum

        Sum = 0
        for p in range(0,len(polygon)):
            if p==len(polygon)-1:
                # go back again to first point
                Sum += (polygon[p][1]+polygon[0][1])*(polygon[p][0]*polygon[0][1]-polygon[0][0]*polygon[p][1])
            else:
                Sum += (polygon[p][1]+polygon[p+1][1])*(polygon[p][0]*polygon[p+1][1]-polygon[p+1][0]*polygon[p][1])
        
        Cy = (1/(6*Area))*Sum
        
        return (Cx,Cy)

    def getFinalCentroid(bottomFaces,nof):
        """Calculate centroid of all bottomfaces together, bottomfaces contains the bottom polygons of each ciyObjectMember.
nof is the number of features you have"""

        sumCx = 0
        sumCy = 0        
        
        # get sum of centroids in x and y direction
        for i in range(0,len(bottomFaces)):
                        
            currentCentroid = getCentroid(getArea(bottomFaces[i][1]),bottomFaces[i][1])
            sumCx += currentCentroid[0]
            sumCy += currentCentroid[1]

        FinalCx = sumCx/nof
        FinalCy = sumCy/nof

        return FinalCx,FinalCy
            

    # parse the infile
    print 'Reading file...'
    tree = etree.parse(infile)
    # for storing vertices:
    vert = StringIO.StringIO()
    # for storing faces:
    fac = StringIO.StringIO()

    pointlist = []
    count = 0
    bottomFaces = []
    
    # loop through the ciyObjectMember elements, for all faces put the points in a set (so that they are not duplicated). Then extend the pointlist with that set. This gives every unique point an index
    for cOM in tree.iter(CGML+"cityObjectMember"):
        count += 1
        s = set([])

        # for each cOM bottom face needs to found
        # so initial value will be false
        foundBottomFace = False
               
        pointlist += list(s)
        # with pointlist we can generate the face-lines in the .obj file:
        for lR in cOM.iter(GML+"LinearRing"):
            print >>fac, "f",
            for pos in range(len(lR)-1):
                print >>fac, pointlist.index(lR[pos].text)+1,
            print >>fac

            # needed to calculate centroid
            posData = []

            for pos in lR:
                s.update([pos.text])

                # get points of bottom face
                x,y,z = pos.text.split()

                posData.append([float(x)]+[float(y)]+[float(z)])

            # keep face?
            if checkBottomFace(posData) and not foundBottomFace:
                # if bottom face store cOmID and x,y,z values
                bottomFaces.append([count,posData])
                # if bottom face of cOM has been found, then switch trigger to True
                # this is done to increase the efficiency.
                # It is assumed there is only 1 bottom face for each cOM
                foundBottomFace = True

    print 'translating points...'

    # calculate offset
    offset = getFinalCentroid(bottomFaces,count)

    # Generate the vertex-lines in the .obj file. Also translate the points using the OFFSET
    for p in pointlist:
        c = p.split()
        print >>vert, "v %.7f %.7f %.2f" % ( float(c[0])-offset[0], float(c[1])-offset[1], float(c[2]) )

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
    
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
