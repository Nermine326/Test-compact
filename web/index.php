<html>
<style>
body {text-align:center;color:#fff;}
a {color:#fff;}
</style>
<body bgcolor=black color=#fff>
<?php
	function getSQLDomains() {
		$sql = "SELECT * FROM `DNScache`";
		return querySQLArray($sql);
	}
	function getSQLDomain($domain) {
		$sql = "SELECT * FROM `DNScache` WHERE `domain` = '".$domain."';";
		$res = querySQL($sql);
		if($res['banned'] == 1) {
			return '127.0.0.1';
		}else{
			return $res['ip'];
		}
	}
	function countSQLDomain($domain) {
		$sql = "SELECT count(*) FROM `DNScache` WHERE `domain` = '".$domain."';";
		$res = querySQL($sql);
		return $res['count(*)'];
	}
	function setSQLDomain($domain, $ip) {
		querySQL("INSERT INTO `DNScache` (`domain` ,`ip` ,`banned`) VALUES ('".$domain."', '".$ip."', '0');");
	}
	function getSQLBlacklist() {
		return querySQLArray("SELECT * FROM `blacklist`;");
	}
	function setSQLBlacklist($domain) {
		return querySQLArray("INSERT INTO `blacklist` (`domain`) VALUES ('".$domain."');");
	}
	function deleteSQLBlacklist($domain) {
		querySQLArray("DELETE FROM `blacklist` WHERE `domain` = '".$domain."';");
	}
	function querySQL($sql) {
		$query = mysql_query($sql);
		if (!$query) die('Requête invalide : ' . mysql_error() );
		if($row = mysql_fetch_assoc($query)) {
			return $row;
		}else{
			return null;
		}
	}
	function simpleQuerySQL($sql) {
		$query = mysql_query($sql);
		if (!$query) die('Requête invalide : ' . mysql_error() );
	}
	function querySQLArray($sql) {
		$res = array();
		$query = mysql_query($sql);
		if (!$query) die('Requête invalide : ' . mysql_error() );
		while ($row = mysql_fetch_assoc($query)) {
			$res[] = $row;
		}
		return $res;
	}
	
	$db = mysql_connect('127.0.0.1', 'root2', '');
	if (!$db) die('Connexion impossible : ' . mysql_error());
	mysql_select_db('DNSdata', $db); 
	
	if(isset($_GET['domain']) && isset($_GET['banned'])) {
		$sql = "UPDATE `DNScache` SET `banned` = ".(($_GET['banned']==1)?1:0)." WHERE `domain` = '".$_GET['domain']."' LIMIT 1;";
		simpleQuerySQL($sql);
	}
	echo "<table border=1 align=center>";
	$i = 0;
	foreach(getSQLDomains() as $d) {
		$style = 'style="background-color:'.(($d['banned']==1)?'red':'green').'"';
		echo '<tr><td '.$style.'><a name="dns'.$i.'"/>'.$d['domain']."</td><td ".$style.">".$d['ip']."</td><td ".$style.">".$d['banned']."</td><td ".$style."><a href=\"?banned=".(($d['banned']==1)?0:1)."&domain=".$d["domain"]."#dns".$i."\">".(($d['banned']==1)?"debloquer":"bloquer")."</a></td></tr>";
		$i++;
	}
	echo "</table>";
	
	mysql_close($db);
?>
</body>
</html>