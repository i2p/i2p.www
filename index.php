<?php
include('menu.php');

define('MENU_FILE','menu.ini');
define('PAGE_DIR','pages/');
define('PAGE_EXT','.html');

/* Filter out everything except alphanumerical characters and underscores */
function form_dirty($data) {
    return preg_match('/[^[:alnum:]_]/',$data);
}

$page = '';
if(isset($_REQUEST['page'])) {
    $page = urldecode($_REQUEST['page']);
} else {
    $page = 'home';
}

if(!form_dirty($page) and is_readable(PAGE_DIR.$page.PAGE_EXT)) {
    $site_structure = parse_ini_file(MENU_FILE, true);
    $pagetitle = getpagetitle($page);
    include(PAGE_DIR.'header'.PAGE_EXT);
    include(PAGE_DIR.$page.PAGE_EXT);
    include(PAGE_DIR.'footer'.PAGE_EXT);
} else {                                                                                            
    header("HTTP/1.0 404 Not Found");
    print "<h1>Error: Page not found</h1>\n";
    print "<a href=\"javascript:history.back(1)\">Go back</a>";
}

?>
