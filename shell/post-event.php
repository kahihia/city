<? include 'header.php'; ?>


<div id="main">
  <section class="body noborder">
    
    <h1>Post Event</h1>
    
    <form>
      
      <ul>
	<li class="label"><label for="name">Event Name</label></li><li><input id="name" type="text" class="text wide"></li><li id="name-info"></li>
	<li class="label"><label for="location">Location</label></li><li><input id="location" type="text" class="text wide"></li><li id="location-info"></li>
	<li class="label"><label for="start">When</label></li><li><input id="start" type="text" class="text wide date">
	  <select name="time">
	    <option>12:00am</option>
	  </select>
	  <a href="" class="addevent">+ Add end time</a></li>
	<li id="when-info"></li>
	<li class="label"></li><li><input id="end" type="text" class="text wide date">
	  <select name="time">
	    <option>12:00am</option>
	  </select>
	  <a href="" class="addevent">- Remove end time</a></li>
	<li class="label">
	  <label for="description">Description</label>
	  <span class="description">Optional</span>
	</li><li><textarea id="description" class="wide" rows=5></textarea></li><li id="description-info"></li>
	<li class="label">Tags</li>
	<li>
	  <ul>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li class="last"><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li class="last"><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li><input type="checkbox" id="remember"><label for="remember">Remember me</label></li>
	    <li class="other"><input type="checkbox" id="other"><label for="other">Other <span class="small">(Specify)</span></label><input type="text" id="othertext" class="othertext"></li>
	  </ul>	
	</li>
	<li class="label"><label for="image">Image</label></li><li><input id="image" type="file" class="file"></li><li id="image-info"></li>
	<li class="label"></li><li><input type="submit" class="submit button" value="Post Event"></li>
      </ul>
    </form>


  </section><!-- .body -->
</div> <!-- #main -->
</div> <!-- .wrapper -->

<? include 'footer.php'; ?>
