<?php
include('menu.php');

define(PAGE_DIR,'pages/');
define(PAGE_EXT,'.html');

/* Filter out everything except alphanumerical characters and underscores */
function form_filter($data) {
    return preg_replace('/[^[:alnum:]_]/','',$data);
}

$page = '';
if(isset($_REQUEST['page'])) {
    $page = form_filter(urldecode($_REQUEST['page']));
} else {
    $page = 'home';
}

$pagetitle = getpagetitle($page);

if(is_readable(PAGE_DIR.$page.PAGE_EXT)) {
    include(PAGE_DIR.'header'.PAGE_EXT);
    include(PAGE_DIR.$page.PAGE_EXT);
    include(PAGE_DIR.'footer'.PAGE_EXT);
} else {                                                                                            
    header("HTTP/1.0 404 Not Found");
    include(PAGE_DIR.'header'.PAGE_EXT);
    print "<h1>Error: Page \"$page\" not found</h1>";
    include(PAGE_DIR.'footer'.PAGE_EXT);
}

?>
