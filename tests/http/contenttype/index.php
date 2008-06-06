<?php

if (isset($_GET['type'])) {
    $t = $_GET['type'];
} else {
    $t = 'textxml';
}

switch ($t) {
    case 'applicationxml':
        $type = 'application/xml';
        break;
    case 'applicationxhtmlxml':
        $type = 'application/xhtml+xml';
        break;
    case 'texthtml':
        $type = 'text/html';
        break;
    case 'textxml':
        $type = 'text/xml';
        break;
    default:
        $type = 'text/plain';
}

header("Content-Type: $type; charset=utf-8");
readfile("demo.xml");

?>
