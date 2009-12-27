<?php
// change upload_max_filesize in php.ini.
// for example: upload_max_filesize = 10M

// make db connection
$host = "localhost";
$user = "root";
$pass = "1234";
$dbname = "vis3";

$connect = mysql_connect($host,$user,$pass) or die(mysql_error());
mysql_select_db($dbname,$connect) or die(mysql_error());
         	
 ?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
   <head>
      <title>Import 3D Model</title>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">

      <script type="text/javascript" src="http://ecn.dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6.2"></script>

      <script type="text/javascript">
         
         var map = null;
                  
         function GetMap()
         {
            map = new VEMap('myMap');
            map.LoadMap();
            map.SetMapMode(VEMapMode.Mode3D);
         }   

         function AddModel(objfile,lat,lon)
         {            
			
			// center of object
         	var center = new VELatLong(lat,lon);
         	//	model will be rotated 90 degrees 
			var orientation = new VEModelOrientation(0, 90, 0);
			
            var layer = new VEShapeLayer();
            var modelSpec = new VEModelSourceSpecification(VEModelFormat.OBJ,objfile, layer);
            map.Import3DModel(modelSpec, onModelLoad, center, orientation, null);

            // go to model
            map.SetCenterAndZoom(center, 16);
         }

         function onModelLoad(status)
         {
            if (status == VEModelStatusCode.Success)
            {
               alert("The 3D model has been loaded.");
            }
            
            if (status == VEModelStatusCode.InvalidURL)
            {
               alert("The URL given for the model data is invalid.");
            }
            
            if (status == VEModelStatusCode.Failed)
            {
               alert("There was a problem loading the 3D model.");
            }
         }
 
      </script>
   </head>
   <body onload="GetMap();">
    

      <form name="uploader" enctype="multipart/form-data" method="POST" action="">
            <div id='myMap' style="position:relative; width:600px; height:400px;"></div>
            <br />

     <p>
      <input type="file" name="file">
          <input type="submit" name="upload" value="Upload GML file" />
        </p>
     <p>Once you are uploading, please wait untill your object shows up in table below.</p>

      
      
                  <table width="60%" border="0" align="left">
              <tr>
                <td width="10%" bgcolor="#CCCCCC">objID</td>
                <td width="40%" bgcolor="#CCCCCC">number of features</td>
                <td width="50%" bgcolor="#CCCCCC">date</td>
              </tr>
              <?php
              
              // do sql selection and give result
              $sql_select	= "SELECT `objID`,`obj`,`cPointLat`,`cPointLong`,`nof`,`date` from bingModel ORDER BY `objID` DESC";
              $sql			= mysql_query($sql_select);
              // if there is a result
              if(mysql_num_rows($sql)>0)
              {
              	// keep storing data into $row if there is result
              	while($row = mysql_fetch_object($sql))
              	{
              		
              		// url of .obj file
              		$objFile = 'http://'.$_SERVER['HTTP_HOST'].dirname($_SERVER['PHP_SELF']).'/upload/'.$row->obj;
              		
              		// print out result in table
              		echo "              <tr>
                <td bgcolor=\"#E1E1E1\">$row->objID</td>
                <td bgcolor=\"#E1E1E1\">$row->nof</td>
                <td bgcolor=\"#E1E1E1\">$row->date</td>
                <td bgcolor=\"#E1E1E1\"><input id=\"btnAddModel\" type=\"button\" value=\"Add 3D Model\" 
         onClick=\"AddModel('$objFile',$row->cPointLat,$row->cPointLong);\">
</td>
              </tr>";
              
              	}
              }
              // if no results in db
              else 
              {
              	   echo "<tr><td colspan=\"3\" bgcolor=\"#E1E1E1\">No models in database</td></tr>";
              }
              
              ?>
              
            </table>

            <br>

      
      <?php 
      // will be used for uploading file and executing .py script
      include("uploader.php");      
      ?>
      </form>
   </body>
</html>
