<?php
// if button upload is pressed
if (isset($_POST['upload']))
{
	// if user have entered a file
	if(isset($_FILES['file']))
	{
		// get file path
		$upload_root = "upload/";
		$file = basename($_FILES['file']['name']);
		$target_path = $upload_root.$file;
			
		// limit file size = 10 MB
		// does not always work in PHP
		if($_FILES['file']['size']<10485760)
		{
		
			// only .xml files are allowed
			if(validFile($file))
			{
				// move temp file to upload folder	
				if(move_uploaded_file($_FILES['file']['tmp_name'],$target_path))
				{
					//	create a name for output file
					$outfileName = substr($file,0,strlen($file)-4)."-".time().".".'obj';
					
					// RUN PYTHON code
					// first get path info					
                    $path = dirname($_SERVER['SCRIPT_FILENAME']);
                    
                    // get input file and output file
					$infile = "$path/upload/$file";
					$outfile = "$path/upload/$outfileName";
					
					// RUN main from python script with given arguments
					$url = "CityGML2OBJ.py?INFILE=$infile&OUTFILE=$outfile&INFILE_DB=$file&OUTFILE_DB=$outfileName";
					echo "<meta http-equiv=\"refresh\" content=\"0;url=$url\">"; // execute $url command
						
				}
				else
				{
					template_msg("Something went wrong while uploading");
				}
			}
			else 
			{
				template_msg("You only can upload .xml files");
			}
		}
		else 
		{
			template_msg("file is too big, only files < 10 MB are allowed");
		}
	}
	else 
	{
		template_msg("No file specified");
	}
}

// function used to show msg
function template_msg($msg)
{
	?>
	<table width="100%" border="0">
  <tr>
    <td bgcolor="#E5E5E5"><?php echo $msg;?></td>
  </tr>
</table>
	
	<?php	
}

// Check if file is valid. Only .xml files are allowed
function validFile($file)
{
	return (substr($file,strlen($file)-4))=='.xml' ? true : false;
}
?>
