<?php
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

$msg = "";
$inverter_new_stat = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
	if ( isset($_POST['fan']) ) {
		$fan = 1;
	}		
	else {
		$fan = 0;
	}
	
	$fan_temp = test_input($_POST["fan_temp"]);

	if ( isset($_POST['inverter_relay']) ) {
		$inverter_new_stat = "c";
		$inverter_relay = 1;
	}		
	else {
		$inverter_new_stat = "o";
		$inverter_relay = 0;
	}
	
	$sql = "UPDATE settings set value = " . $fan . ", datetimeupdated = NOW() WHERE setting = 'fan'; ";
	$sql .= "UPDATE settings set value = " . $fan_temp . ", datetimeupdated = NOW() WHERE setting = 'fan_temp'; ";
	$sql .= "UPDATE settings set value = " . $inverter_relay . ", datetimeupdated = NOW() WHERE setting = 'inverter_relay'; ";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ($conn->connect_error) {
		die($msg = $conn->connect_error);
	} 

	if ($conn->multi_query($sql) === TRUE) {
		//$msg = '<div class="alert alert-success" role="alert">UPDATE SUCCESSFUL___ ' . $sql . '</div>';
		$msg = '<div class="alert alert-success" role="alert">DONE!<br />' . date("Y-m-d H:i:s") . '</div>';
	} else {
		$msg = '<div class="alert alert-danger" role="alert">ERROR! = ' . $conn->error . ' ==> ' . $sql . '</div>';
	}
	$conn->close();
	
	//$msg .= "-=-=-=-=-=-=-=<br />";
	
	//$cmd = 'sudo -u www-data python /var/www/solar/inverter_relay_controller01.py ' . $inverter_new_stat;
	//$msg .= "<br /> cmd: " . $cmd . " == " . exec($cmd);
}

echo $msg;
?>

