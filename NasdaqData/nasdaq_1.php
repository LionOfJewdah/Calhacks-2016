<?php
// define the SOAP client using the url for the service
$client = new soapclient('http://ws.nasdaqdod.com/v1/NASDAQAnalytics.asmx?WSDL');

// create an array of parameters
$param = array(
               "Symbols" => "NDAQ, GOOG",
               "StartDateTime" => "11/11/2016 09:30:00.000",
               "EndDateTime" => "11/11/2016 10:30:00.000",
               //  "StartDateTime" => "11/11/2009 09:30:00.000",
               //  "EndDateTime" => "11/11/2009 10:30:00.000",
               "MarketCenters" => "Q, B");

// add authentication info
$xignite_header = new SoapHeader('http://www.xignite.com/services/',
     "Header", array("Token_" => "25D26255F6924F31BD86503A4253BEA0"));
$client->__setSoapHeaders(array($xignite_header));

// call the service, passing the parameters and the name of the operation
$result = $client->GetAverageMarketSpread($param);
// assess the results
if (is_soap_fault($result)) {
     echo '<h2>Fault</h2><pre>';
     print_r($result);
     echo '</pre>';
} else {
     echo '<h2>Result</h2><pre>';
     print_r($result);
     echo '</pre>';
}
// print the SOAP request
echo '<h2>Request</h2><pre>' . htmlspecialchars($client->__getLastRequest(), ENT_QUOTES) . '</pre>';
// print the SOAP request Headers
echo '<h2>Request Headers</h2><pre>' . htmlspecialchars($client->__getLastRequestHeaders(), ENT_QUOTES) . '</pre>';
// print the SOAP response
echo '<h2>Response</h2><pre>' . htmlspecialchars($client->__getLastResponse(), ENT_QUOTES) . '</pre>';
?>
