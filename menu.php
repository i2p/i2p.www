<?php
function getpagetitle($page) {
	global $site_structure;
	if (isset($site_structure[$page]['title'])) {
		return $site_structure[$page]['title'];
	}
	$title = str_replace ('_', ' ', $page);
	return ucfirst($title);
}

function buildmenu() {
	global $site_structure;
	foreach ($site_structure as $page=>$page_config) {
		if (isset($page_config['depth'])) {
			$title = getpagetitle($page);
			$link = '';
			if (isset($page_config['link'])) {
				$link = $page_config['link'];
			} else {
				$link = $page;
			}
			switch ($page_config['depth']) {
				case 1:
					print "<br /><b><a href=\"$link\">$title</a></b><br />\n";
					break;
				case 2:
					print "-&nbsp;<a href=\"$link\">$title</a><br />\n";
					break;
				case 3:
					print "&nbsp;&nbsp;&sdot;&nbsp;<a href=\"$link\">$title</a><br />\n";
					break;
				default:
			}

		}
	}
}
?>
