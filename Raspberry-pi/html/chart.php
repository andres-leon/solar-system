<?php
/*
Use Fusecharts free trial. I only use this for my personal use. http://www.fusioncharts.com
*/
error_reporting(E_ALL);
ini_set('display_errors', 1);
/* Include the `../src/fusioncharts.php` file that contains functions to embed the charts.*/

include("fusioncharts.php");

/* The following 4 code lines contains the database connection information. Alternatively, you can move these code lines to a separate file and include the file here. You can also modify this code based on your database connection.   */

$hostdb = "localhost";  // MySQl host
$userdb = "xxx";  // MySQL username
$passdb = "yyy";  // MySQL password
$namedb = "solardata";  // MySQL database name

// Establish a connection to the database
$dbhandle = new mysqli($hostdb, $userdb, $passdb, $namedb);

/*Render an error message, to avoid abrupt failure, if the database connection parameters are incorrect */
if ($dbhandle->connect_error) {
  exit("There was an error with your connection: ".$dbhandle->connect_error);
}
?>
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Solar System Historical Data</title>
		<!--
        <script src="http://static.fusioncharts.com/code/latest/fusioncharts.js"></script>
        <script src="http://static.fusioncharts.com/code/latest/fusioncharts.charts.js"></script>
        <script src="http://static.fusioncharts.com/code/latest/themes/fusioncharts.theme.zune.js"></script>
		-->
		<script src="js/fusioncharts.js"></script>
        <script src="js/fusioncharts.charts.js"></script>
        <script src="js/themes/fusioncharts.theme.zune.js"></script>
		<link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
		<link href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css" rel="stylesheet">
    </head>

    <body>

<?php
//Defaults
$historyselect = "pvoutput";
$historyselecttime = 0.5;
$charttype = "zoomlinedy";
$pYAxisMaxValue = 0;
$pYAxisMinValue = 0;
$sYAxisMaxValue = 0;
$sYAxisMinValue = 0;
$YAxisMaxValue = 0;
$YAxisMinValue = 0;

if ( isset($_POST['historyselect']) ) {
	$historyselect = $_POST['historyselect'];	
}
if ( isset($_POST['historyselecttime']) ) {
	$historyselecttime = $_POST['historyselecttime'];	
}

//$strQuery = "SELECT datetimestamp,PV_array_power, pv_array_current  FROM stats_with_new_battery_charge_percentage WHERE datetimestamp >= now() - INTERVAL 2 DAY";

switch ($historyselect) {
	case "pvoutput":
		$strQuery = "SELECT datetimestamp as valx, PV_array_power as py, PV_array_current as sy FROM stats_with_new_battery_charge_percentage WHERE datetimestamp >= now() - ";
		$pyAxisName = "Watts";
		$syAxisName = "Current (A)";
		$caption = "PV Output (Watts and Amps)";
		$dataseries1name = "PV Watts";
		$dataseries2name = "PV Amperes";
		$charttype = "zoomlinedy";
		$pYAxisMaxValue = 300;
		$pYAxisMinValue = -50;
		$sYAxisMaxValue = 45;
		$sYAxisMinValue = -10;		
		break;
		
	case "batteryvolt":
		$strQuery = "SELECT datetimestamp as valx, battery_voltage as py, pv_array_voltage as sy FROM stats_with_new_battery_charge_percentage WHERE datetimestamp >= now() - ";
		$pyAxisName = "Volts";
		$syAxisName = "Volts";
		$caption = "Battery and Panel Voltage";
		$dataseries1name = "Battery Volts";
		$dataseries2name = "PV Volts";
		$charttype = "zoomline";
		$YAxisMaxValue = 15;
		$YAxisMinValue = 10;
		break;
		
	case "temps":
		$strQuery = "SELECT datetimestamp as valx, RBP_CPU_temperature as py, Battery_Sensor_temperature as sy FROM stats_with_new_battery_charge_percentage WHERE datetimestamp >= now() - ";
		$pyAxisName = "F";
		$syAxisName = "F";
		$caption = "Temperatures";
		$dataseries1name = "RBPi Temp";
		$dataseries2name = "Battery Temp";
		$charttype = "zoomline";
		$YAxisMaxValue = 190;
		$YAxisMinValue = 35;
		break;
	
	case "wattspermin":
		$strQuery = "SELECT dayhourmin as valx, watts as py FROM PV_watt_average_dayhourmin WHERE dayhourmin >= now() - ";
		$pyAxisName = "F";
		$syAxisName = "F";
		$caption = "Average PV Watts per minute";
		$dataseries1name = "Watts";
		$charttype = "zoomline";
		$YAxisMaxValue = 400;
		$YAxisMinValue = 0;
		break;

}

if ($historyselecttime == "0.5") {
	$strQuery .=  " INTERVAL 12 HOUR";
}
else {
	$strQuery .=  " INTERVAL " . $historyselecttime . " DAY";
}

$caption .= " (" . $historyselecttime . " Days)";

//echo $strQuery;

$result = $dbhandle->query($strQuery) or exit("Error code ({$dbhandle->errno}): {$dbhandle->error}");

  if ($result) {
	
	if ($charttype == "zoomlinedy"){
		$arrData = array(
			"chart" => array(
				"caption"=> $caption,
				"xAxisname"=> "Date time",
				"pyAxisName"=> $pyAxisName,
				"syAxisName"=> $syAxisName,
				"legendItemFontColor"=> "#666666",
				"theme"=> "zune",
				"pYAxisMaxValue" => $pYAxisMaxValue,
				"pYAxisMinValue" => $pYAxisMinValue,
				"sYAxisMaxValue" => $sYAxisMaxValue,
				"sYAxisMinValue" => $sYAxisMinValue,
				"YAxisMaxValue" => $YAxisMaxValue,
				"YAxisMinValue" => $YAxisMinValue 			
				)
		);
	}
	else {
		$arrData = array(
			"chart" => array(
				"caption"=> $caption,
				"xAxisname"=> "Date time",
				"yAxisName"=> $pyAxisName,
				"yAxisName"=> $syAxisName,
				"legendItemFontColor"=> "#666666",
				"theme"=> "zune",
				"YAxisMaxValue" => $YAxisMaxValue,
				"YAxisMinValue" => $YAxisMinValue 			
				)
		);		
	}	
  
          // creating array for categories object

          $categoryArray=array();
          $dataseries1=array();
          $dataseries2=array();

          // pushing category array values
         while($row = mysqli_fetch_array($result)) {
            array_push($categoryArray, array(
				"label" => $row["valx"]
				)
			);
			array_push($dataseries1, array(
				"value" => $row["py"]
				)
			);
			
			if ($historyselect != 'wattspermin') {
				array_push($dataseries2, array(
					"value" => $row["sy"]
					)
				);
			}			

		}

      $arrData["categories"]=array(array("category"=>$categoryArray));
      // creating dataset object      
	   
	  if (!empty($dataseries2)) {
		  $arrData["dataset"] = array(array("seriesName"=> $dataseries1name, "data"=>$dataseries1), 
			array("seriesName"=> $dataseries2name,  "renderAs"=>"line", "data"=>$dataseries2));
	  }
	  else {
		  $arrData["dataset"] = array(array("seriesName"=> $dataseries1name, "data"=>$dataseries1));
	  }
	
	/*$arrData["dataset"] = array(array("seriesName"=> "Generated Watts", "data"=>$dataseries1));*/

      /*JSON Encode the data to retrieve the string containing the JSON representation of the data in the array. */
      $jsonEncodedData = json_encode($arrData);

      // chart object
      $msChart = new FusionCharts($charttype, "chart1" , "1000", "550", "chart-container", "json", $jsonEncodedData);

      // Render the chart
      $msChart->render();

      // closing db connection
      $dbhandle->close();

   }

?>

<div class="container">	
	<div class="row">
		<form name="historyform" id="historyform" method="post">
			<div class="col-sm-4 text-center">				
				<select id="historyselect" name="historyselect" class="form-control" title="">
					<option  <?php if ($historyselect == 'pvoutput') { ?>selected="true" <?php }; ?> value="pvoutput">PV Output (Watts and Amps)</option>
					<option  <?php if ($historyselect == 'wattspermin') { ?>selected="true" <?php }; ?> value="wattspermin">Average PV Watts per minute</option>
					<option <?php if ($historyselect == 'batteryvolt') { ?>selected="true" <?php }; ?> value="batteryvolt">Voltages</option>
					<option <?php if ($historyselect == 'temps') { ?>selected="true" <?php }; ?> value="temps">Temperatures</option>
				</select>
			</div>
			<div class="col-sm-4 text-center">
				<select id="historyselecttime" name="historyselecttime" class="form-control" title="">
					<option <?php if ($historyselecttime == '0.5') { ?>selected="true" <?php }; ?> value="0.5">12 Hours</option>
					<option <?php if ($historyselecttime == '1') { ?>selected="true" <?php }; ?> value="1">1 Day (24 hours)</option>
					<option <?php if ($historyselecttime == '2') { ?>selected="true" <?php }; ?> value="2">2 Days (48 hours)</option>
					<option <?php if ($historyselecttime == '3') { ?>selected="true" <?php }; ?> value="3">3 Days (72 hours)</option>
					<option <?php if ($historyselecttime == '7') { ?>selected="true" <?php }; ?> value="7">7 Days</option>
					<option <?php if ($historyselecttime == '14') { ?>selected="true" <?php }; ?> value="14">2 Weeks</option>
					<option <?php if ($historyselecttime == '30') { ?>selected="true" <?php }; ?> value="30">Last Month</option>
				</select>
			</div>
			<div class="col-sm-4 text-center">
				<button type="submit" class="btn btn-primary btn-block">LOAD CHART</button>
			</div>
		</form>
	</div>
	<div class="row">
			<div class="col-sm-12 text-center">
				<center>
					<div id="chart-container">Chart will render here!</div>
				</center>
		</div>
	</div>
</div>
			<script src="/bootstrap/js/jquery.min.js"></script>
			<script src="/bootstrap/js/bootstrap.min.js"></script>
    </body>

    </html>