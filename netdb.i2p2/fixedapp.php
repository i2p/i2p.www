 <?php
# Reseed script
#

define('DATABASE', '/var/www/reseed.db');
define('NUM_ROUTERS', 50);
define('NETDB_DIR', '/home/i2p/.i2p/netDb');
define('DEBUG', false);

/*
-------------------------------------
Add following to .htaccess:
Options +FollowSymlinks
RewriteEngine On
RewriteRule ^(.*\.dat)$ /index.php?file=$1 [L]
RewriteCond %{REQUEST_FILENAME} !index.php
RewriteCond %{REQUEST_FILENAME} !robots.txt

-------------------------------------

Do not touch if you don't know what you're doing.
*/

# Database handle
class ReseedDatabase extends SQLite3
{
    protected $db;
    protected $createStatement1 = 'create table client (ip string, whn int)';
    protected $createStatement2 = 'create table entry (whn int, wht string)';

    public function __construct($file, $flags = SQLITE3_OPEN_READONLY)
    {
        parent::__construct($file, $flags);
    $this->busyTimeout(10000);
        // this only has to happen once, no sense calling it on every request
        //$this->_create();
    }

    public function insertEntry($time, $entry)
    {
        $results = $this->exec(sprintf('insert into entry (whn,wht) values (%d,"%s")', $time, $entry));
        if ($results == true) return true;
        return false;
    }

    public function insertClient($time, $host)
    {
        $results = $this->exec(sprintf('insert into client (ip,whn) values ("%s",%d)', $host, $time));
        if ($results == true) return true;
        return false;
    }

    public function getEntries($time)
    {
        $results = $this->query(sprintf('select * from entry where whn = "%s"', $time));
        if ($results instanceof SQLite3Result) {
            $t = array();
            while ($j = $results->fetchArray(SQLITE3_ASSOC)) {
                $t[] = $j;
            }
            return $t;
        }
        return false;
    }

    public function getEntriesFromClient($host)
    {
        $results = $this->query(sprintf('select e.wht from entry e, client c where c.whn=e.whn and c.ip = "%s"', $host));
        if ($results instanceof SQLite3Result) {
            $t = array();
            while ($j = $results->fetchArray(SQLITE3_ASSOC)) {
                $t[] = $j['wht'];
            }
            return $t;
        }
        return false;
    }

    public function getClient($host)
    {
        $results = $this->query(sprintf('select * from client where ip = "%s"', $host));
        if ($results instanceof SQLite3Result) return $results->fetchArray();
        return false;
    }

    public function cleanup()
    {
        $this->exec(sprintf('delete from client where whn < %d', (time() - 3600)));
        $this->exec(sprintf('delete from entry where whn < %d', (time() - 7200)));
    }

    private function _create()
    {
        if ($this->query('select * from entry') == false && $this->query('select * from client') == false) {
            $this->exec($this->createStatement1);
            $this->exec($this->createStatement2);
        }
    }

}


$user_agent = $_SERVER['HTTP_USER_AGENT'];
$remote_ip = $_SERVER["REMOTE_ADDR"];

if (true !== DEBUG && !strstr($user_agent, 'Wget/1.11.4')) {
    header('HTTP/1.0 400 Access Denied');
    header('Content-Type: text/plain');
    die("Access denied.");
}

// if they're requesting a file, let's try to send it to them
if (isset($_GET['file'])) {
    // sanitize the input filename
    $file = htmlentities($_GET['file'], ENT_QUOTES, 'UTF-8', false);
    $file = str_replace('..', '', str_replace('/', '', $file));
    $file = realpath(NETDB_DIR . DIRECTORY_SEPARATOR . $file);
    $filename = basename($file);

    // make sure they are requesting a real file
    if (!$file || empty($filename) ||
        NETDB_DIR !== substr($file, 0, strlen(NETDB_DIR)) ||
        preg_match("/^routerInfo-(.+)\=.dat$/", $filename) !== 1 ||
        !file_exists($file) ||
        is_dir($file)
    ) {
        header('HTTP/1.0 404 Not Found');
        header('Content-Type: text/plain');
        die('Not found.');
    }

    $db = new ReseedDatabase(DATABASE, SQLITE3_OPEN_READONLY);
    $res = $db->getEntriesFromClient($remote_ip);
    $db->close();
    unset($db);
    if ($res === false || !in_array($filename, $res)) {
        header('HTTP/1.0 404 Not Found');
        header('Content-Type: text/plain');
        die('Not found.');
    }

    header('Content-Type: application/octet-stream');
    header('Content-Transfer-Encoding: binary');
    header('Content-Length: ' . filesize($file));
    header(sprintf('Content-Disposition: attachment; filename="%s"', $filename));

    ob_clean();
    flush();
    readfile($file);

    die();
}

$page = '<html><head><title>NetDB</title></head><body><ul>%s</ul></body></html>';
$entry = '<li><a href="%s">%s</a></li>';

$db = new ReseedDatabase(DATABASE, SQLITE3_OPEN_READONLY);
if ($db->getClient($remote_ip) === false) {
    $time = time();

    $db->close();
    unset($db);
    $db = new ReseedDatabase(DATABASE, SQLITE3_OPEN_READWRITE);
    $db->insertClient($time, $remote_ip);
    $db->close();
    unset($db);

    # generate new list
    $clientRouterList = array();
    if (is_dir(NETDB_DIR) && is_readable(NETDB_DIR)) {
        $clientRouterList = array_map('basename', glob(NETDB_DIR . DIRECTORY_SEPARATOR . 'routerInfo-*=.dat', GLOB_ERR));
    }

    $db = new ReseedDatabase(DATABASE, SQLITE3_OPEN_READWRITE);
    foreach (array_rand($clientRouterList, NUM_ROUTERS) as $router) {
        $db->insertEntry($time, $clientRouterList[$router]);
    }
} else {
    // run cleanup 50% of requests
    if (rand(0, 100) < 50) {
       $db->close();
       unset($db);
       $db = new ReseedDatabase(DATABASE, SQLITE3_OPEN_READWRITE);
       $db->cleanup();
    }
}

// to release locks
$db->close();
unset($db);
$db = new ReseedDatabase(DATABASE, SQLITE3_OPEN_READONLY);

# use old list based on date in database, i.e. sends the same as before
$clientRouterList = $db->getEntriesFromClient($remote_ip);

$db->close();
unset($db);

header('Content-Type: text/html');
die(sprintf($page, implode('', array_map(function($single) use ($entry) { return sprintf($entry, $single, $single);}, $clientRouterList))));

