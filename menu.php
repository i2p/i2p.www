<?php
// TODO: improve this, like include the navigation hierarchy into it

// dictionary for looking up the page title, if there is no match
// the first character of the page is capitalized
$pagetitles = array('home' => 'News',
	      	'about' => 'About I2P',
		'getinvolved' => 'Get involved',
		'halloffame' => 'Hall of Fame',
		'myi2p' => 'MyI2P',
		'minwww' => 'MinWWW',
		'i2ptunnel' => 'I2PTunnel',
		'i2ptunnel_services' => 'Setting up services',
		'i2ptunnel_tuning' => 'Tuning',
		'i2ptunnel_lan' => 'LAN setup',
		'jvm' => 'JVM',
		'api' => 'API',
		'sam' => 'SAM',
		'i2cp' => 'I2CP',
		'how' => 'How does it work?',
		'how_intro' => 'Intro',
		'how_threatmodel' => 'Threat model',
		'how_tunnelrouting' => 'Tunnel routing',
		'how_garlicrouting' => 'Garlic routing',
		'how_networkdatabase' => 'Network database',
		'how_peerselection' => 'Peer selection',
		'how_cryptography' => 'Cryptography',
		'how_elgamalaes' => 'ElGamal/AES+SessionTag',
		'how_networkcomparisons' => 'Network comparisons',
		'faq' => 'FAQ',
		'cvs' => 'CVS');

function getpagetitle($page) {
	global $pagetitles;
	if (isset($pagetitles[$page])) {
		return $pagetitles[$page];
	}
	$title = str_replace ('_', ' ', $page);
	return ucfirst($title);
}
?>
