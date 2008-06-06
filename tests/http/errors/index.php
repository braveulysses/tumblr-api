<?php

if (isset($_GET['code'])) {
    $code = intval($_GET['code']);
} else {
    $code = 400;
}


switch ($code) {
case 400:
    header('HTTP/1.1 400 Bad Request');
    break;
case 401:
    header('HTTP/1.1 401 Unauthorized');
    break;
case 403:
    header('HTTP/1.0 403 Forbidden');
    break;
case 404:
    header('HTTP/1.0 404 Not Found');
    break;
case 410:
    header('HTTP/1.0 410 Gone');
    break;
case 503:
    header('HTTP/1.0 503 Service Unavailable');
    break;
default:
    # Anything unrecognized will return an HTTP 500, like it or not
    header('HTTP/1.0 500 Internal Server Error');
}

echo "HTTP $code";

?>
