<!doctype html>

<!-- Paul Irish's technique for targeting IE, modified to only target IE6, applied to the html element instead of body -->
<!--[if lt IE 7 ]><html lang="en" class="no-js ie6"><![endif]-->
<!--[if (gt IE 6)|!(IE)]><!--><html lang="en" class="no-js"><!--<![endif]-->

<head>
	<meta charset="utf-8">

	<title></title>
	<meta name="description" content="">
	<meta name="author" content="">

	<link rel="stylesheet" href="style.css?v=1.0">
	<script src="js/modernizr-1.6.min.js"></script>
</head>
<body>
	<div class="wrapper">
	
		<header id="header">
			<hgroup>
				<h1><a href="/">Cityfusion</a></h1>
				<h2>The community at your fingertips</h2>
			</hgroup>
	
			<nav id="main-nav">
				<ul>
					<li><a href="">Browse Events</a></li>
					<li><a href="post-event.php" class="post current">Post an Event</a></li>
				</ul>
			</nav>
	
			<nav id="user-nav">
				<ul>
					<li><a href="login.php">Sign In</a></li>
					<li><a href="register.php">Register</a></li>
				</ul>
			</nav>
	
			<nav id="city-nav">
				<a href="">Saskatoon <span class="downtick"></span></a>
			</nav>
	</header>
	
	<aside id="city-widget">
		<p>Cityfusion is currently only available in Saskatoon, Canada.</p>
		<p><span class="white">Want your city to be next?</span><br><a href="/feedback">Let us know.</a></p>
	</aside>
	
	<nav id="date-nav">
		<ul>
			<li><a href="" class="current">Today</a></li>
			<li><a href="">Tomorrow</a></li>
			<li><a href="">This weekend</a></li>
			<li><a href="">This week</a></li>
			<li><a href="">Next week</a></li>			
			<li><a href="" class="jump">Jump to date</a></li>
		</ul>
	</nav>