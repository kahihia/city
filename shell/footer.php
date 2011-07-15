	<footer id="footer">
		<div class="wrapper">
			<p>&copy; Cityfusion 2010.</p>
			<nav>
				<ul>
					<li><a href="">Feedback</a></li>
					<li><a href="">Advertise</a></li>
				</ul>
			</nav>
		</div>
	</footer>

<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js"></script>
<script>!window.jQuery && document.write(unescape('%3Cscript src="js/jquery-1.4.4.min.js"%3E%3C/script%3E'))</script>

<!-- Below is your script file, which has a basic JavaScript design pattern that you can optionally use -->
<!-- Keep this and plugin scripts at the bottom for faster page load; combining and minifying scripts is recommended -->
<script src="js/general.js"></script>

<!-- asynchronous analytics code by Mathias Bynens; change UA-XXXXX-X to your own code; http://mathiasbynens.be/notes/async-analytics-snippet -->
<!-- this can also be placed in the <head> if you want page views to be tracked quicker -->
<script>
$('#city-nav a').bind('click', function() {
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
</script>
</body>
</html>