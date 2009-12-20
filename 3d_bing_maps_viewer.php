<?php
// change upload_max_filesize in php.ini.
// for example: upload_max_filesize = 10M
         	

         	
		    $file = "http://files.ylan.nl/footprints_extruded.obj";
         	
         	$data = file($file);
         	         	
         	$latlong = substr($data[1],1);
         	
         	$data = explode(',',$latlong);
         	$lat = $data[0];
         	$long = $data[1];

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

         function AddModel(objfile)
         {            
			
			var center = new VELatLong(<?php echo $lat.",".$long;?>);
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

      
      
                  <table width="60%" border="0" align="left">
              <tr>
                <td width="10%" bgcolor="#CCCCCC">objID</td>
                <td width="40%" bgcolor="#CCCCCC">number of features</td>
                <td width="50%" bgcolor="#CCCCCC">date</td>
              </tr>
              <?php
              
              $sql_select	= "SELECT objID,obj,nof,date from bingmodel";
              $sql			= mysql_query($sql_select);
              if(mysql_num_rows($sql)>0)
              {
              	while($row = mysql_fetch_object($sql))
              	{
              		
              		$objFile = 'http://'.$_SERVER['SERVER_ADDR'].dirname($_SERVER['PHP_SELF']).'/upload/'.$row->obj;
              		
              		echo "              <tr>
                <td bgcolor=\"#E1E1E1\">$row->objID</td>
                <td bgcolor=\"#E1E1E1\">$row->nof</td>
                <td bgcolor=\"#E1E1E1\">$row->date</td>
                <td bgcolor=\"#E1E1E1\"><input id=\"btnAddModel\" type=\"button\" value=\"Load 3D Model\" 
         onClick=\"AddModel('$objFile');\">
</td>
              </tr>";
              
              	}
              }
              else 
              {
              	   echo "<tr><td colspan=\"3\" bgcolor=\"#E1E1E1\">No models in database</td></tr>";
              }
              
              ?>
              
            </table>

            <br>

      
      <?php 
      include("uploader.php");      
      ?>
      </form>
   </body>
</html>
