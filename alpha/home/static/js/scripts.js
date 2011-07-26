$('tr.hasactions').bind('hover', function() {
    $('#city-nav a, #city-widget').toggleClass('active');
    return false;
});

$('html').click(function() {
    if($('#city-widget').hasClass('active') == true)
    {
	$('#city-nav a, #city-widget').toggleClass('active');
    }
});
$('#city-widget').click(function(event){
    event.stopPropagation();
});

var _gaq = [['_setAccount', 'UA-XXXXX-X'], ['_trackPageview']];
(function(d, t) {
    var g = d.createElement(t),
    s = d.getElementsByTagName(t)[0];
    g.async = true;
    g.src = ('https:' == location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    s.parentNode.insertBefore(g, s);
})(document, 'script');