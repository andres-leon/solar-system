<?php
/*
updates the database with commands from the web interface token_get_all
reboot or shutdown the Raspberry Pi.
*/
$servername = "localhost";
$username = "xx";
$password = "yy";
$dbname = "solardata";

function test_input($data) {
  $data = trim($data);
  $data = stripslashes($data);
  $data = htmlspecialchars($data);
  return $data;
}
/* 
foreach ($_POST as $key => $value){
  echo "{$key} = {$value}\r\n";
}
 */

$msg = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
	if ( isset($_POST['shutorreboot']) ) {
		/*echo "shutorreboot = " . $_POST['shutorreboot'];*/		
		if ( $_POST['shutorreboot'] == "shutdown" ) {
			$sql = "UPDATE settings set value = 1, datetimeupdated = NOW() WHERE setting = 'shutdown'; ";
		}
		elseif ( $_POST['shutorreboot'] == "reboot" ) {
			$sql = "UPDATE settings set value = 1, datetimeupdated = NOW() WHERE setting = 'reboot'; ";
		}
		
		// Create connection
		$conn = new mysqli($servername, $username, $password, $dbname);
		// Check connection
		if ($conn->connect_error) {
			die($msg = $conn->connect_error);
		} 

		if ($conn->multi_query($sql) === TRUE) {
			//$msg = '<div class="alert alert-success" role="alert">UPDATE SUCCESSFUL___ ' . $sql . '</div>';
			$msg = '<div class="alert alert-success" role="alert">Will ' . $_POST['shutorreboot'] . ' in about 1 minute! <br />' . date("Y-m-d H:i:s") . '</div>';
		} else {
			$msg = '<div class="alert alert-danger" role="alert">ERROR! = ' . $conn->error . ' ==> ' . $sql . '</div>';
		}
		$conn->close();	
	}	
}

echo $msg;


?>

