<?php
if (isset($_POST['upload']))
{
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
		
			if(validFile($file))
			{
					
				if(move_uploaded_file($_FILES['file']['tmp_name'],$target_path))
				{
					// RUN PYTHON code
					
					template_msg("The file: ".$file." has been uploaded");				
					
					
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

function validFile($file)
{
	return (substr($file,strlen($file)-4))=='.xml' ? true : false;
}
?>