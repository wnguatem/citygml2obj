<?php
         	

         	
		    $file = "http://files.ylan.nl/footprints_extruded.obj";
         	
         	$data = file($file);
         	         	
         	$latlong = substr($data[1],1);
         	
         	$data = explode(',',$latlong);
         	$lat = $data[0];
         	$long = $data[1];

         	
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

         function AddModel(type)
         {
            
			
			var center = new VELatLong(<?php echo $lat.",".$long;?>);
			var orientation = new VEModelOrientation(0, 90, 0);
			
			document.getElementById('textfield').value = center


            var layer = new VEShapeLayer();
            var modelSpec = new VEModelSourceSpecification(VEModelFormat.OBJ, document.getElementById('txtSource').value, layer);
            map.Import3DModel(modelSpec, onModelLoad, center, orientation, null);

            // go to model
            map.SetCenterAndZoom(center, 16);
         }

         function onModelLoad(model, status)
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

      <form id="form1" name="form1" method="post" action="">
            <div id='myMap' style="position:relative; width:600px; height:400px;"></div>
      <p>
        <input id="txtSource" type="text" value="http://files.ylan.nl/footprints_extruded.obj" name="txtSource">
        <input id="btnAddModel" type="button" value="Load 3D Model" 
         onclick="AddModel();" name="btnAddModel">
      </p>
			center point:<br>
          <input type="text" name="textfield" id="textfield" />

      </form>
      <p>&nbsp;</p>
   </body>
</html>
