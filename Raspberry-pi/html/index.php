<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$pagetitle = "Solar System v 1.0";

$servername = "localhost";
$username = "xx";
$password = "yy";
$dbname = "solardata";

$fan = 1;
$fan_temp = 0;
$inverter_relay = 1;

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$sql = "SELECT setting, value from settings";
$result = $conn->query($sql);

while($row = $result->fetch_assoc()) {
	if ($row["setting"] == 'fan'){
		$fan = intval($row["value"]);
	}
	elseif ($row["setting"] == 'fan_temp'){
		$fan_temp = intval($row["value"]);
	}
	elseif ($row["setting"] == 'inverter_relay'){
		$inverter_relay = intval($row["value"]);
	}
}

$conn->close();
//echo $fan . " - " . $fan_temp . " - " . $inverter_relay ;
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title><?php echo $pagetitle ?></title>
    <!-- Bootstrap -->
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
	<link href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css" rel="stylesheet">
	<link rel="icon" href="sun.png">
	<!-- Google Charts -->
	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
	
	<script src="/fusioncharts-suite-xt/js/fusioncharts.js"></script>
    <script src="/fusioncharts-suite-xt/js/fusioncharts.charts.js"></script>
    <script src="/fusioncharts-suite-xt/js/themes/fusioncharts.theme.zune.js"></script>
	
  </head>
  <body>
 <script type="text/javascript"> 
	var graph_width = 300;
 
	google.charts.load('current', {'packages':['gauge', 'line', 'corechart']});

	google.charts.setOnLoadCallback(draw_pv_voltage_chart);
	google.charts.setOnLoadCallback(draw_pv_amp_chart);
	google.charts.setOnLoadCallback(draw_pv_watt_chart);
	google.charts.setOnLoadCallback(draw_batt_voltage_chart);
	//google.charts.setOnLoadCallback(draw_batt_amp_chart);
	//google.charts.setOnLoadCallback(draw_batt_watt_chart);
	google.charts.setOnLoadCallback(draw_batt_percent_chart);
	google.charts.setOnLoadCallback(draw_batt_load_watts);
	google.charts.setOnLoadCallback(draw_batt_load_current);	
	google.charts.setOnLoadCallback(draw_rbpi_temp_chart);
	//google.charts.setOnLoadCallback(draw_inverter_amp_chart);
	google.charts.setOnLoadCallback(draw_batteryTemp_chart);

      function draw_pv_voltage_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Voltage', 0]
        ]);

        var options = {
          width: graph_width,
          yellowFrom:0, yellowTo: 12,
          greenFrom:12, greenTo: 20,
		  redFrom: 20, redTo: 25,
		  min: 0,
		  max:25,
          minorTicks: 25
		  ,series: {
                animation: {
                    duration: 2000
                }
            }
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_pv_voltage_chart'));

        chart.draw(data, options);

        //Update data
    function get_PV_voltage_Data () {
        $.ajax({
            //url: 'realtime_pv_volt.php',
			url: 'realtime_mqtt_data.php?itm=solarVoltage',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_PV_voltage_Data, 5000);
            }
        });
    }
    get_PV_voltage_Data();
      }
	  
	  
	  function draw_pv_amp_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Amps', 0]
        ]);
/* width: 800, height: 240,*/
        var options = {
          width: graph_width,
          greenFrom:0, greenTo: 20,
		  yellowFrom:20, yellowTo: 30,
		  redFrom: 30, redTo: 40,
		  min: 0,
		  max: 40,
          minorTicks: 10
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_pv_amp_chart'));

        chart.draw(data, options);

        //Update data
    function get_PV_amp_Data () {
        $.ajax({
            //url: 'realtime_pv_amp.php',
			url: 'realtime_mqtt_data.php?itm=solarCurrent',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_PV_amp_Data, 5000);
            }
        });
    }
    get_PV_amp_Data();
      }
	  
	   
	  function draw_pv_watt_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Watts', 0]
        ]);

        var options = {
          width: graph_width,         
		  min: 0,
		  max: 600,
          minorTicks: 5
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_pv_watt_chart'));

        chart.draw(data, options);

        //Update data
    function get_PV_watt_Data () {
        $.ajax({
            //url: 'realtime_pv_watts.php',
			url: 'realtime_mqtt_data.php?itm=solarWatts',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_PV_watt_Data, 5000);
            }
        });
    }
    get_PV_watt_Data();
      }

/* **************** */

      function draw_batt_voltage_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Voltage', 0]
        ]);

        var options = {
          width: graph_width,
		  redFrom: 0, redTo: 11.00,
          yellowFrom:11.00, yellowTo: 12.20,
          greenFrom:12.20, greenTo: 20.00,
		  min: 0.0,
		  max:20.0,
          minorTicks: 20
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_batt_voltage_chart'));

        chart.draw(data, options);

        //Update data
    function get_batt_voltage_Data () {
        $.ajax({
            //url: 'realtime_batt_volt.php',
			url: 'realtime_mqtt_data.php?itm=batteryVoltage',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batt_voltage_Data, 5000);
            }
        });
    }
    get_batt_voltage_Data();
      }
	  
	  
	  function draw_batt_amp_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Amps', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:0, greenTo: 20,
		  yellowFrom:20, yellowTo: 30,
		  redFrom: 30, redTo: 40,
		  min: 0,
		  max: 40,
          minorTicks: 10
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_batt_amp_chart'));

        chart.draw(data, options);

        //Update data
    function get_batt_amp_Data () {
        $.ajax({
            //url: 'realtime_batt_amp.php',
			url: 'realtime_mqtt_data.php?itm=batteryCurrent',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batt_amp_Data, 5000);
            }
        });
    }
    get_batt_amp_Data();
      }
	  
	   
	  function draw_batt_watt_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Watts', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:0, greenTo: 20,
		  yellowFrom:20, yellowTo: 30,
		  redFrom: 30, redTo: 40,
		  min: 0,
		  max: 40,
          minorTicks: 10
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_batt_watt_chart'));

        chart.draw(data, options);

        //Update data
    function get_batt_watt_Data () {
        $.ajax({
            //url: 'realtime_batt_watts.php',
			url: 'realtime_mqtt_data.php?itm=batteryWatts',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batt_watt_Data, 5000);
            }
        });
    }
    get_batt_watt_Data();
      }
	  
	   
	  function draw_batt_percent_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Chrg. %', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:70, greenTo: 100,
		  yellowFrom:60, yellowTo: 70,
		  redFrom: 0, redTo: 60,
		  min: 0,
		  max: 100,
          minorTicks: 10
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_batt_percent_chart'));

        chart.draw(data, options);

        //Update data
    function get_batt_percent_Data () {
        $.ajax({
            //url: 'realtime_batt_percent2.php',
			url: 'realtime_mqtt_data.php?itm=batteryChargePercentNew',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batt_percent_Data, 5000);
            }
        });
    }
    get_batt_percent_Data();
      }
	  
	  function draw_batt_load_current() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Load Curr.', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:-15, greenTo: 20,
		  yellowFrom:20, yellowTo: 35,
		  redFrom: 35, redTo: 50,
		  min: -15,
		  max: 50,
          minorTicks: 5
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_batt_load_current'));

        chart.draw(data, options);

        //Update data
    function get_batt_load_current_Data () {
        $.ajax({
            //url: 'realtime_batt_temp.php',
			url: 'realtime_mqtt_data.php?itm=Load_current',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batt_load_current_Data, 5000);
            }
        });
    }
    get_batt_load_current_Data();
      }
	  
	  function draw_batt_load_watts() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Load Watts', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:-25, greenTo: 25,
		  yellowFrom:25, yellowTo: 35,
		  redFrom: 35, redTo: 50,
		  min: -25,
		  max: 50,
          minorTicks: 5
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_batt_load_watts'));

        chart.draw(data, options);

        //Update data
    function get_batt_temp_Data () {
        $.ajax({
            //url: 'realtime_batt_temp.php',
			url: 'realtime_mqtt_data.php?itm=loadWatts',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batt_temp_Data, 5000);
            }
        });
    }
    get_batt_temp_Data();
      }
	  
/* **************** */	  

	  function draw_rbpi_temp_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['CPU Temp.', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:35, greenTo: 140,
		  yellowFrom:140, yellowTo: 165,
		  redFrom: 165, redTo: 180,
		  min: 35,
		  max: 180,
          minorTicks: 10
        };

        var chart = new google.visualization.Gauge(document.getElementById('draw_rbpi_temp_chart'));

        chart.draw(data, options);

        //Update data
    function get_rbpi_temp_Data () {
        $.ajax({
            //url: 'realtime_rbpi_temp.php',
			url: 'realtime_mqtt_data.php?itm=cputemp',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_rbpi_temp_Data, 5000);
            }
        });
    }
    get_rbpi_temp_Data();
      }

/* **************** */
	  function draw_inverter_amp_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Inv. Amps', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:-6, greenTo: 0,
		  yellowFrom:0, yellowTo: 10,
		  redFrom: 10, redTo: 20,
		  min: -6,
		  max: 20,
          minorTicks: 10
        };
 
        var chart = new google.visualization.Gauge(document.getElementById('draw_inverter_amp_chart'));

        chart.draw(data, options);

        //Update data
    function get_inverter_amp_Data () {
        $.ajax({
            url: 'realtime_mqtt_data.php?itm=inverter_current',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_inverter_amp_Data, 2500);
            }
        });
    }
    get_inverter_amp_Data();
      }

/* **************** */

	  function draw_batteryTemp_chart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Batt. Temp.', 0]
        ]);

        var options = {
          width: graph_width,
          greenFrom:35, greenTo: 140,
		  yellowFrom:140, yellowTo: 165,
		  redFrom: 165, redTo: 180,
		  min: 35,
		  max: 180,
          minorTicks: 10
        };
 
        var chart = new google.visualization.Gauge(document.getElementById('draw_batteryTemp_chart'));

        chart.draw(data, options);

        //Update data
    function get_batteryTemp_Data () {
        $.ajax({
            url: 'realtime_mqtt_data.php?itm=batteryTemp',
            success: function (response) {
                data.setValue(0, 1, response);
                chart.draw(data, options);
                setTimeout(get_batteryTemp_Data, 2500);
            }
        });
    }
    get_batteryTemp_Data();
      }

/* **************** */

	  
</script>
  
<div class="container">	
	<div class="row">
			<div class="col-sm-12 text-center">
				<h2><a href="index.php"><?php echo $pagetitle ?></a></h2>
				<p>Status as of <span id="lastupdated"></span></p>
			</div>
		</div>
	
		<div class="panel-group">
			<div class="panel panel-default">
				<div class="panel-heading">
				<h4>Panels</h4>
				</div>
				<div class="panel-body">
					<div class="row">
						<div class="col-sm-4 text-center">
						<!--  height: 240px;  -->
						<!--  style="width: 800px;" -->
							<center>
								<div id="draw_pv_voltage_chart"></div>
							</center>
						</div>
						<div class="col-sm-4 text-center">
							<center>
								<div id="draw_pv_amp_chart"></div>
							</center>
						</div>
						<div class="col-sm-4 text-center">
							<center>
								<div id="draw_pv_watt_chart"></div>
							</center>
						</div>
					</div>
				</div>
			</div>			
			
			<div class="panel panel-default">
				<div class="panel-heading">
				<h4>Batteries</h4>
				</div>
				<div class="panel-body">
					<div class="row">
						<div class="col-sm-3 text-center">
							<center>
								<div id="draw_batt_voltage_chart"></div>
							</center>
						</div>
						<div class="col-sm-3 text-center">
							<center>
								<div id="draw_batt_percent_chart"></div>
							</center>
						</div>
						<div class="col-sm-3 text-center">
							<center>
								<div id="draw_batt_load_current" title="If this number is way off, then run current_sensor_calibrate.py to recalibrate zero point of sensor."></div>
							</center>
						</div>
						<div class="col-sm-3 text-center">
							<center>
								<div id="draw_batt_load_watts" title="If this number is way off, then run current_sensor_calibrate.py to recalibrate zero point of sensor."></div>
							</center>
						</div>
					</div>
				</div>
			</div>
			
		<div class="panel panel-default">
			<div class="panel-heading">
				<h4>Others</h4>
			</div>
			<div class="panel-body">
				<div class="row">
					<div class="col-sm-3 text-center">
						<center>
							<div id="draw_rbpi_temp_chart"></div>
						</center>
					</div>
					<div class="col-sm-3 text-center">
						<center>
							<div id="draw_batteryTemp_chart"></div>
						</center>
					</div>
					<div class="col-sm-3 text-center">
						<form id="form" name="form">
							<div class="row">
								<div class="col-sm-2 text-center"></div>
								<div class="col-sm-8 text-center">
									<div class="checkbox">
										<label>
<?php
if ($fan == 1) {
	echo '<input class="form-control" id="fan" name="fan" type="checkbox" checked data-toggle="toggle" data-size="normal" data-on="FAN ON" data-off="FAN OFF" data-onstyle="success" data-width="220"> ';
	}
else {
	echo '<input class="form-control" id="fan" name="fan" type="checkbox" data-toggle="toggle" data-size="normal" data-on="FAN ON" data-off="FAN OFF" data-onstyle="success" data-width="220"> ';
	}	
?>
										</label>
									</div>
								</div>
								<div class="col-sm-2 text-center"></div>
							</div>
							<div class="row">
								<div class="col-sm-2 text-center"></div>
								<div class="col-sm-8 text-center">
									<div class="checkbox">
										<label>
<?php
if ($inverter_relay == 1) {
	echo '<input id="inverter_relay" name="inverter_relay" title="Turn inverter ON or OFF" type="checkbox" checked data-toggle="toggle" data-size="normal" data-on="INVERTER ON" data-off="INVERTER OFF" data-width="220">';
	}
else {
	echo '<input id="inverter_relay" name="inverter_relay" title="Turn inverter ON or OFF" type="checkbox" data-toggle="toggle" data-size="normal" data-on="INVERTER ON" data-off="INVERTER OFF" data-width="220">';
	}	
?>
										</label>
									</div>
								</div>
								<div class="col-sm-2 text-center"></div>
							</div>
							<div class="row">
								<div class="col-sm-2 text-center"></div>
								<div class="col-sm-6 text-center">
								<center>
								<!--<label for="fan_temp" title="Set the temperature at which the fans should star running if enabled.">CPU Tmp Trigger</label>-->
									<select id="fan_temp" name="fan_temp" class="form-control" data-onstyle="success" title="Set the temperature at which the fans should star running if enabled.">
										<?php
										echo $fan_temp;
											for ($x = 90; $x <= 200; $x++) {
												if ($x == $fan_temp)
													echo "<option value='" . $x . "' selected>" . $x . "</option>";
												else
													echo "<option value='" . $x . "'>" . $x . "</option>";	
											} 
										?>
									</select>
								</center>
								</div>
								<div class="col-sm-2 text-center">
									<button type="submit" title="Update fan, inverter and temp threshhold triggers." class="btn btn-primary">UPDATE</button>
								</div>
								<div class="col-sm-2 text-center"></div>
							</div>
							<div class="row">
							</div>
							<div class="row">
								<div class="col-sm-2 text-center"></div>
								<div id="formpostresult" class="col-sm-8 text-center">
								<div class="col-sm-2 text-center"></div>
								</div>
							</div>
						</form>						
					</div>
					<div class="col-sm-3 text-center">
					<div class="row">
						<div class="col-sm-2 text-center"></div>
							<div class="col-sm-8 text-center">
								<!--<form id="shutform" name="shutform" method="post" action="updatedb_shut_reboot.php">-->
								<form id="shutform" name="shutform">
									<p>&nbsp;</p>
									<select id="shutorreboot" name="shutorreboot" class="form-control" data-onstyle="success">
										<option value="reboot">Reboot</option>
										<option value="shutdown">Shutdown</option>
									</select>
									<br />
									<button type="submit" class="btn btn-danger btn-block">EXECUTE</button>
									<p>&nbsp;</p>
									<div id="shutformresult"></div>
								</form>
							</div>
						<div class="col-sm-2 text-center"></div>
					</div>
				</div>
			</div>
		</div>
		
		<div class="panel panel-default">
			<div class="panel-heading">
				<h4>Historical</h4>
			</div>
			<div class="panel-body">
				<div class="row">
					<div class="col-sm-12 text-center">
						<div class="embed-responsive embed-responsive-16by9">
							<iframe class="embed-responsive-item" src="chart.php"></iframe>
						</div>
					</div>
				</div>
			</div>
			
		</div>		
		
	</div> 
	</div> 
	
		
<!--    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script> -->
    <script src="/bootstrap/js/jquery.min.js"></script>
    <script src="/bootstrap/js/bootstrap.min.js"></script>
	<script src="https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js"></script>
	
	
<script type="text/javascript">
var interval = 2500;   //number of mili seconds between each call
/* http://stackoverflow.com/questions/5384708/reload-a-div-with-jquery-timer */
$(document).ready(function () {   
	
    var refreshlastupdated = function() {
        $.ajax({
            url: "realtime_mqtt_data.php?itm=datetimedatacollected",
            cache: false,
            success: function(html) {
                $('#lastupdated').html(html);
				setTimeout(refreshlastupdated, interval);
            }
        });
    };
	refreshlastupdated();
	
	$('#form').submit(function(event) {
		debugger;
		div = $(this);
		event.preventDefault();
		$.ajax({
			type: "POST",
			url: "updatedb.php",
			data: $(this).serialize(),		
			success: function(data){
				div.parent().find('#formpostresult').html(data);
			}					
		});
	});
	
	 $('#shutform').submit(function(event) {
		debugger;
		div = $(this);
		event.preventDefault();
		$.ajax({
			type: "POST",
			url: "updatedb_shut_reboot.php",
			data: $(this).serialize(),		
			success: function(data){
				div.parent().find('#shutformresult').html(data);
			}
		});
	}); 
	
});	

	</script>
	
	
  </body>
</html>

