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
			$uri = '';
			if (isset($page_config['link'])) {
				$uri = $page_config['link'];
			} else {
				$uri = $page;
			}
			if (isset($page_config['nolink'])) {
				$link = $title;
			} else {
				if(preg_match("/^(http:\/\/|\/)", $title))
					$link = "<a href=\"$uri\">$title</a>";
				else
					$link = "<a href=\"/$uri\">$title</a>";
			}

			switch ($page_config['depth']) {
				case 1:
					print "<br /><b>$link</b><br />\n";
					break;
				case 2:
					print "-&nbsp;$link<br />\n";
					break;
				case 3:
					print "&nbsp;&nbsp;&sdot;&nbsp;$link<br />\n";
					break;
				default:
			}

		}
	}
}
?>
