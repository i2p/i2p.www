<?php

function guessIP() {
    return $_SERVER['REMOTE_ADDR'];
}

function routercheck($hostname, $port) {
    $fp = @fsockopen($hostname, $port, $errno, $errstr, 5);
    if ($fp) {
        socket_set_timeout($fp, 10);
        $version = fread($fp, 1);
        if ($version == 'B') {
            return "OKAY looks like we found a router";
        } else {
            return "ERROR invalid service/version";
        }
        fclose($fp);
    } else {
        return "ERROR hostname/port not open";
    }
}

$hostname = guessIP();
$port = '8887';
$msg = '';

if(isset($_REQUEST['hostname']) and isset($_REQUEST['port'])) {
    $hostname = $_REQUEST['hostname'];
    $port = $_REQUEST['port'];
    if (($port>0) && ($port<65536)) {
        $msg = routercheck($hostname, $port);
    } else {
        $msg = "ERROR invalid port range";
    }
}

?>
<html>
<head><title>I2P Router check</title></head>
<body>
<h1>I2P Router check</h1>
<h2><?=$msg?></h2>
<form method="post">
<p>Host/Port: <br>
<input name="hostname" value="<?=$hostname?>" type="text" size="30" maxlength="60">
<input name="port" value="<?=$port?>" type="text" size="6" maxlength="5">
</p>
<input type="submit" value="submit">
<input type="reset" value=" reset">
</form>
</body>
</html>

