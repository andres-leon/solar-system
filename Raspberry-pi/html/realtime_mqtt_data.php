<?php
if (isset($_GET['itm']))
{
	$itm = $_GET['itm'];
	$cmd = 'sudo -u www-data python /var/www/solar/realtime_mqtt_data.py ' . $itm ;
	echo exec($cmd);		
}
?>

