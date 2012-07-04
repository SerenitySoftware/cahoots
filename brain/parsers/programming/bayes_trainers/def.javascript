
// return an associative array for file named  fileName
function parseYamlFile(fileName){
    var fs// :FileSystemObject
        =new ActiveXObject("Scripting.FileSystemObject");
    var src =fs.OpenTextFile(fileName);
    var result=parseYamlStream(src);
    src.Close();
    return result;
}

function parseYamlString(s){
    var lines=s.split(/\r?\n|\r/ig);
    var ah=new ArrayHandler()
    var parser=new YamlParser(ah);
    for(var i in lines){
        parser.add(lines[i]);
    }
    parser.end();
    return ah.result;
}

// return an associative array for src
// src should suppoth the following methods
//    AtEndOfStream - retutns true if there is no lines in stream
//    ReadLine - returns the next readed line
function parseYamlStream(src){
    var ah=new ArrayHandler()
    var parser=new YamlParser(ah);
    while(!src.AtEndOfStream){
        var s=src.ReadLine();
        //if(/�����������/i.test(s))
        //   debugger;
        parser.add(s);
    }
    parser.end();
    return ah.result;
} //parseYamlFile

// ----------------------------------------------------------------------


// ---------------------------------------------------------------------

function ArrayHandler(){
    this.wasIndent=false;
    this.result=[];
    this.state={cur:this.result};
    this.targets=[];
    this.processPair=ArrayHandler_processPair;
    this.processIndent=ArrayHandler_processIndent;
    this.processUnindent=ArrayHandler_processUnindent;
    this.processEntry=ArrayHandler_processEntry;
}

function ArrayHandler_processPair(p,n,v){
    //WScript.Echo("P:"+n+":"+v);
    this.state.cur[n]=v;
    this.state.lastN=n;
    this.wasIndent=false;
}
function ArrayHandler_processIndent(p){
    //WScript.Echo("I");
    this.state.cur[this.state.lastN]=[]
    this.targets.push(this.state);
    this.state={cur:this.state.cur[this.state.lastN]};
    this.wasIndent=true;
}
function ArrayHandler_processUnindent(p){
    //WScript.Echo("U");
    this.state=this.targets.pop();
    if(this.state.isCollection)
        this.state=this.targets.pop();
    this.wasIndent=false;
}
function ArrayHandler_processEntry(p){
    //WScript.Echo("E");
    var n=[];
    if(!this.wasIndent)
        this.state=this.targets.pop();
    this.state.isCollection=true;
    this.state.cur.push(n);
    this.targets.push(this.state);
    this.state={cur:n};
    this.wasIndent=false;
}


//-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
function testParse(){
    var yp=new YamlParser();
    yp.onPair=function(p,n,v){WScript.Echo(n+">>"+v);}
    yp.onEntry=function(p){WScript.Echo("entry");}
    yp.onIndent=function(p){WScript.Echo("indent");}
    yp.onUnindent=function(p){WScript.Echo("unindent");}
    yp.add("test:it");
    yp.add("  - test2 : it2 ");
    yp.add("        test3 : it2 ");
    yp.add("    test4:it2 ");
    yp.add("test4:it2 ");
    yp.end();
}
function YamlParser(handler){
    this.lineTpl=/^((\s*)(\-\s+)?)(\S[^:]*):(.*)$/i;
    this.commentTpl=/^\s+#/ig;
    this.add=YamlParser_add;
    this.end=YamlParser_end;
    this.processIndents=YamlParser_processIndents;
    this.getTopIndent=YamlParser_getTopIndent;
    this.handler=handler;
    this.onIndent=null;
    this.onPair=null;
    this.onUnindent=null;
    this.onEntry=null;
    this.curIndent=0;
    this.indents=[0];
}
function YamlParser_getTopIndent(){
    return this.indents[this.indents.length-1];
} //YamlParser_getTopIndent
function YamlParser_processIndents(indent){
    if(indent>this.getTopIndent()){
        call(this.onIndent, this);
        if(this.handler!=null) this.handler.processIndent(this);
        this.indents.push(indent);
    }else{
        while(indent<this.getTopIndent()){
            call(this.onUnindent, this);
            if(this.handler!=null) this.handler.processUnindent(this);
            this.indents.pop();
        }
    }
} //YamlParser_processIndents
function YamlParser_add(s){
    // var indents //:Array
    if(this.commentTpl.test(s))
        return;
    var r=this.lineTpl.exec(s);
    if(r!=null){
        var spaces=r[1].replace(/\t/ig, "    ");
        var curIndent=spaces.length;
        this.processIndents(curIndent);
        var curName=r[4];
        var curValue=r[5];
        if(r[3].length!=0){
            call(this.onEntry, this);
            if(this.handler!=null) this.handler.processEntry(this);
        };
        call(this.onPair, this, trim(curName), trim(curValue))
        if(this.handler!=null) this.handler.processPair(this, trim(curName), trim(curValue));
    }
} //YamlParser_add
function YamlParser_end(){
    this.processIndents(0);
} //YamlParser_end
function call(f, a1, a2, a3, a4, a5){
    if(f!=null) f(a1, a2, a3, a4, a5);
} //call
function trim(s){
    return s.replace(/((^\s+)|(\s+$))/ig,"")
} //trim

function warning(s){
    WScript.Echo("��������������: "+s);
}
function startOfMonth(date){
    // var date //:Date
    return new Date(date.getYear(), date.getMonth(), 1);
}

//requestVars start

/*
 * @author      Jesse Berman
 * @copyright   2008-01-31
 * @version     1.0
 * @license     http://www.gnu.org/copyleft/lesser.html
*/


/*
 * Portions by Dieter Raber <dieter@dieterraber.net>
 * copyright   2004-12-27
*/


/* pwa.js: a drop-in JavaScript utility that displays galleries from picasaweb.google.com in your website */

/* NOTE: This version hides all the link-backs to Picasa */

/* This JavaScript file, when called from a webpage, will load all the thumbnail images of all the galleries
   in a user's Picasa Web Albums account into an HTML table that's 4 rows wide.  Clicking on any of the
   galleries will display thumbnails of all the photos in that gallery, and clicking on any of those thumbnails
   will display the photo.  

   To call this file from your own webpage, use the following syntax:

       <script type="text/javascript">username='YourPicasawebUsername'; photosize='800'; columns='4';</script>
       <script type="text/javascript" src="http://www.yoursite.com/pwa.js"></script>

   Make sure you change YourPicasawebUsername to your actual Picasaweb username.  For more information about
   Picasa, check out picasaweb.google.com.  Also, www.yoursite.com should point to your actual site name, and
   the location of the pwa.js file.  The script looks for the images back.jpg, next.jpg, and home.jpg, in the
   same directory as pwa.js, to create the navigation arrows.  Please make sure those exist!  I'm providing
   samples in the SourceForce repository, but feel free to substitute your own.

   Note: "Photosize" is the size of the image to be displayed when viewing single images.  I like 800.  :-)
   Note: "columns" is the number of columns of photos to be displayed on your site in the gallery and album views.
   You may omit either of these values; if you do, the default settings are 800 for photosize and 4 for columns.

*/



function readGet(){var _GET = new Array();var uriStr  = window.location.href.replace(/&amp;/g, '&');var paraArr, paraSplit;if(uriStr.indexOf('?') > -1){var uriArr  = uriStr.split('?');var paraStr = uriArr[1];}else{return _GET;}if(paraStr.indexOf('&') > -1){paraArr = paraStr.split('&');}else{paraArr = new Array(paraStr);}for(var i = 0; i < paraArr.length; i++){paraArr[i] = paraArr[i].indexOf('=') > -1 ? paraArr[i] : paraArr[i] + '=';paraSplit  = paraArr[i].split('=');_GET[paraSplit[0]] = decodeURI(paraSplit[1].replace(/\+/g, ' '));}return _GET;}var _GET = readGet();
//requestVars end

function resize(which, max) {
// not used anymore! was scaling photos after they were loaded. using browser-native inline scaling instead,
// until google fixes their image size request to work with any imgmax, rather than just 800 :-(
  var elem = document.getElementById(which);
  if (elem == undefined || elem == null) return false;
  if (max == undefined) max = 658;
  if (elem.width > elem.height) {
    if (elem.width > max) elem.width = max;
  } else {
    if (elem.height > max) elem.height = max;
  }
}

//$Update: May 10, 2007$

function $(a){document.write(a);}
var photosize;
if(!photosize){photosize = 800;}

var columns;
if(!columns || isNaN(columns) || columns < 1) {columns = 4;}


//Global variables
var photolist = new Array(); //this is used globally to store the entire list of photos in a given album, rather than pass the list around in a URL (which was getting rediculously long as a result)
var album_name = ""; //this is used globally to store the album name, so we don't have to pass it around in the URL anymore either.
var my_numpics = ""; //this is used globally to store the number of items in a particular album, so we don't have to pass it around in the URL anymore either.
var prev = ""; //used in the navigation arrows when viewing a single item
var next = "";//used in the navigation arrows when viewing a single item



function picasaweb(j){ //returns the list of all albums for the user
 $("<div style='margin-left:3px'>Gallery Home</div><!--<div style='text-align:right; margin-right:5px; margin-top:-14px'><a target=PICASA class='standard' href='http://picasaweb.google.com/"+username+"/'>View this gallery in Picasa</a></div>--><br>");
 $("<table border=0><tr>");

 for(i=0;i<j.feed.entry.length;i++){

 // for each of the albums in the feed, grab its album cover thumbnail and the link to that album,
 // then display them in a table with 4 columns (along with the album title)

  //This was the old way of grabbing the photos; since Google updated the feed, the media entry is better. :-)
  //
  //var img_begin = j.feed.entry[i].summary.$t.indexOf('src="')+5;
  //var img_end = j.feed.entry[i].summary.$t.indexOf('?imgmax');
  //var img_base = j.feed.entry[i].summary.$t.slice(img_begin, img_end);

  var img_base = j.feed.entry[i].media$group.media$content[0].url;

  var id_begin = j.feed.entry[i].id.$t.indexOf('albumid/')+8;
  var id_end = j.feed.entry[i].id.$t.indexOf('?');
  var id_base = j.feed.entry[i].id.$t.slice(id_begin, id_end);

  $("<td valign=top><a class='standard' href='?albumid="+id_base+"'><img src='"+img_base+"?imgmax=160&crop=1' class='pwimages' /></a>");
  $("<br><table border=0><tr><td></td></tr></table><center><a class='standard' href='?albumid="+id_base+"'>"+ j.feed.entry[i].title.$t +"</a></center></td>");
  if (i % columns == columns-1) {
    $("</tr><tr><td><br></td></tr> <tr><td></td></tr> <tr>");
  }
 }
 $("</tr></table>");
 
}





function getphotolist(j){

// This function is called just before displaying an item; it returns info about the item's current state within its parent
// album, such as the name of the album it's in, the index of the photo in that album, and the IDs of the previous and next
// photos in that album (so we can link to them using navigation arrows).  This way we don't have to pass state information
// around in the URL, which was resulting in hellishly long URLs (sometimes causing "URI too long" errors on some servers).

// Get the number of pictures in the album.  Added 7/18/2007.
 my_numpics = j.feed.openSearch$totalResults.$t;

// Also get the name of the album, so we don't have to pass that around either.  Added 7/18/2007.
 album_name = j.feed.title.$t;

 for(i=0;i<j.feed.entry.length;i++){
  // get the list of all photos referenced in the album and display;
  // also stored in an array (photoids) for navigation in the photo view (passed via the URL)
  var id_begin = j.feed.entry[i].id.$t.indexOf('photoid/')+8;
  var id_end = j.feed.entry[i].id.$t.indexOf('?');
  var id_base = j.feed.entry[i].id.$t.slice(id_begin, id_end);
  photolist[i]=id_base;

  // now get previous and next photos relative to the photo we're currently viewing
  if (i>0)
  {
    var prev_begin = j.feed.entry[i-1].id.$t.indexOf('photoid/')+8;
    var prev_end = j.feed.entry[i-1].id.$t.indexOf('?');
    prev = j.feed.entry[i-1].id.$t.slice(id_begin, id_end);
  }
  if (i<j.feed.entry.length-1)
  {
    var next_begin = j.feed.entry[i+1].id.$t.indexOf('photoid/')+8;
    var next_end = j.feed.entry[i+1].id.$t.indexOf('?');
    next = j.feed.entry[i+1].id.$t.slice(id_begin, id_end);
  }

 }
}




function albums(j){  //returns all photos in a specific album

 //get the number of photos in the album
 var np = j.feed.openSearch$totalResults.$t;
 var item_plural = "s";
 if (np == "1") { item_plural = ""; }

 var album_begin = j.feed.entry[0].summary.$t.indexOf('href="')+6;
 var album_end = j.feed.entry[0].summary.$t.indexOf('/photo#');
 var album_link = j.feed.entry[0].summary.$t.slice(album_begin, album_end);
 var photoids = new Array();

 $("<div style='margin-left:3px'><a class='standard' href='" + window.location.protocol + "//" + window.location.hostname+window.location.pathname+"'>Gallery Home</a> &gt; "+ j.feed.title.$t +"&nbsp;&nbsp;["+np+" item"+item_plural+"]</div><!--<div style='text-align:right; margin-right:5px; margin-top:-14px'><a target=PICASA class='standard' href='"+album_link+"'>View this album in Picasa</a></div>--><br>");
 $("<table border=0><tr>");

 for(i=0;i<j.feed.entry.length;i++){

  //var img_begin = j.feed.entry[i].summary.$t.indexOf('src="')+5;
  //var img_end = j.feed.entry[i].summary.$t.indexOf('?imgmax');
  //var img_base = j.feed.entry[i].summary.$t.slice(img_begin, img_end);

  var img_base = j.feed.entry[i].media$group.media$content[0].url;

  var id_begin = j.feed.entry[i].id.$t.indexOf('photoid/')+8;
  var id_end = j.feed.entry[i].id.$t.indexOf('?');
  var id_base = j.feed.entry[i].id.$t.slice(id_begin, id_end);
  photoids[i]=id_base;
  

  // display the thumbnail (in a table) and make the link to the photo page, including the gallery name so it can be displayed.
  // (apparently the gallery name isn't in the photo feed from the Picasa API, so we need to pass it as an argument in the URL) - removed the gallery name 7/18/2007
  var link_url = "?albumid="+_GET['albumid']+"&photoid="+id_base; //+"&photoids="+photoids;
  // disable the navigation entirely for really long URLs so we don't hit against the URL length limit.
  // note: this is probably not necessary now that we're no longer passing the photoarray inside the URL. 7/17/2007
  // Not a bad idea to leave it in, though, in case something goes seriously wrong and we need to revert to that method.
  if (link_url.length > 2048) { link_url = link_url.slice(0, link_url.indexOf('&photoids=')+10)+id_base; }
  $("<td valign=top><a href='"+link_url+"'><img src='"+img_base+"?imgmax=160&crop=1' class='pwimages' /></a>");
  //$("<p><center><SPAN STYLE='font-size: 9px'>"+j.feed.entry[i].media$group.media$description.$t+"</span></center>");
  $("</td>");

  if (i % columns == columns-1) {
    $("</tr><tr><td><br></td></tr><tr>");
  }
 }
 $("</tr></table>");

}
function photo(j){//returns exactly one photo


 var album_begin = j.entry.summary.$t.indexOf('href="')+6;
 var album_end = j.entry.summary.$t.indexOf('/photo#');
 var album_link = j.entry.summary.$t.slice(album_begin, album_end);

 var img_title = j.entry.title.$t;

 //get the dimensions of the photo we're grabbing; if it's smaller than our max width, there's no need to scale it up.
 var img_width = j.entry.media$group.media$content[0].width;
 var img_height = j.entry.media$group.media$content[0].height;


 var img_base = j.entry.media$group.media$content[0].url;


 // is this a video? If so, we will display that in the breadcrumbs below.
 var is_video = 0;
 if (j.entry.media$group.media$content.length > 1)
 {
   //$('This is a '+j.entry.media$group.media$content[1].medium+'.<br>');
   if (j.entry.media$group.media$content[1].medium == "video")
   {
       is_video = 1;
   }
 }

 
 var photo_begin = j.entry.summary.$t.indexOf('href="')+6;
 var photo_end = j.entry.summary.$t.indexOf('"><img');
 var photo_link = j.entry.summary.$t.slice(photo_begin, photo_end);
 var photo_id = _GET['photoid'];

 //album name is now taken from the global variable instead. 7/18/2007
 //
 //var album_name_begin = j.entry.summary.$t.indexOf(username)+username.length+1;
 //var album_name_end = j.entry.summary.$t.indexOf('/photo#');
 //var album_name = j.entry.summary.$t.slice(album_name_begin, album_name_end);

 var album_id = _GET['albumid'];
 var my_next = next;
 var my_prev = prev;
 var photo_array = photolist;
 //var my_numpics = _GET['np'];
 //instead, we now get this through the global variable my_numpics. 7/18/2007

 //$("photo ids: "+_GET['photoids']+".<br><br>");
 //$("photolist: "+photo_array+".<br><br>");

 //var my_galleryname = _GET['galleryname'];
 //var my_fixed_galleryname = my_galleryname.slice(1, my_galleryname.length-1);
 var my_galleryname = album_name;
 var my_fixed_galleryname = album_name;
 var album_base_path = window.location.protocol + "//" + window.location.hostname+window.location.pathname +"?albumid="+ _GET['albumid'];

 // Get the filename for display in the breadcrumbs
 var LastSlash = 0;
 var img_filename = img_title;
 for(i=0;i<img_base.length-1;i++){
  if (img_base.charAt(i)=="/")
  {
      LastSlash = i;
  }
 }
 if (LastSlash != 0)
 {
     img_filename = img_base.slice(LastSlash+1, img_base.length);
 }
 // replace some commonly-used URL characters like %20
 img_filename = img_filename.replace("%20"," ");
 img_filename = img_filename.replace("%22","\"");
 img_filename = img_filename.replace("%27","\'");


//find preceding two and following two pictures in the array; used for the navigation arrows.
//the arrows are already linked to the previous and next pics, which were passed in with the URL.
//however, we need the ones that are two behind and two ahead so that we can pass that info along when we link to another photo.
//
//NOTE: as of 7/16/2007, the photo array is taken from global photolist (loaded in the getphotolist function) rather than from the URL.
//This has eliminated the need for really long URLs, which were hitting up against the URL length limit in some extreme cases.
for(i=0;i<photo_array.length;i++){
 if (photo_array[i]==photo_id)
 {
     var p1 = photo_array[i-1]; //ID of the picture one behind this one; if null, we're at the beginning of the album
     var current_index = i + 1; //this is the count of the current photo
     var n1 = photo_array[i+1]; //ID of the picture one ahead of this one; if null, we're at the end of the album
 }
}
//these will be passed along if we move to the next or previous photo - removed the gallery name 7/18/2007
//var prev = album_base_path + "&photoid=" + p1 + "&np=" + my_numpics + "&galleryname=" + my_galleryname.replace("'","%27") + "&prev="+p2+ "&next="+photo_id; //+"&photoids="+photo_array;
//var next = album_base_path + "&photoid=" + n1 + "&np=" + my_numpics + "&galleryname=" + my_galleryname.replace("'","%27") + "&prev="+photo_id+ "&next="+n2; //+"&photoids="+photo_array;
var prev = album_base_path + "&photoid=" + p1; //+"&photoids="+photo_array;
var next = album_base_path + "&photoid=" + n1; //+"&photoids="+photo_array;


//Display the breadcrumbs
var my_item_plural = "";
if (my_numpics != 1)
{
    my_item_plural = "s";
}
var item_label = "picture";
var item_label_caps = "Picture";
if (is_video == 1) //if it's a video, don't say it's a picture, say it's an "item" instead
{
    item_label = "item";
    item_label_caps = "Item";
}
//if (photo_array.length == 1) { var current_index_text = "Total of " + my_numpics + " " + item_label + my_item_plural; } else { var current_index_text = item_label_caps + " " + current_index + " of " + my_numpics; }
var current_index_text = item_label_caps + " " + current_index + " of " + my_numpics;
if (is_video == 1) { current_index_text = current_index_text + "&nbsp;&nbsp;[VIDEO]"; }  //show in the breadcrumbs that the item is a video
$("<div style='margin-left:3px'><a class='standard' href='"+ window.location.protocol + "//" + window.location.hostname+window.location.pathname+"'>Gallery Home</a> &gt; <a class='standard' href='" + album_base_path + "'>" + my_fixed_galleryname + "</a> &gt; <!--" + img_filename + "-->" + current_index_text + "</div><!--<div style='text-align:right; margin-right:3px; margin-top:-14px'><a target=PICASA class='standard' href='"+photo_link+"'>View this image in Picasa</a></div>--><br>");


if (p1 == null) //we're at the first picture in the album; going back takes us to the album index
  { var prev = album_base_path }

if (n1 == null) //we're at the last picture in the album; going forward takes us to the album index
  { var next = album_base_path }

 //the navigation panel: back, home, and next.
 $("<center><table border=0><tr valign=top>");
 if (photo_array.length > 1) { $("<td><a class='standard' href='"+prev+"'><img border=0 alt='Previous item' src='prev.jpg'></a> </td><td></td>"); }
 $("<td> <a class='standard' href='"+album_base_path+"'><img border=0 alt='Back to album index' src='home.jpg'></a> </td>");
 if (photo_array.length > 1) { $("<td></td><td> <a class='standard' href='"+next+"'><img border=0 alt='Next item' src='next.jpg'></a></td>"); }
 $("</tr></table></center><br>");

 var max_width = 658; //max width for our photos
 var display_width = max_width;
 if (img_width < display_width)
   { display_width = img_width; } //don't scale up photos that are narrower than our max width; disable this to set all photos to max width

 //at long last, display the image and its description. photos larger than max_width are scaled down; smaller ones are left alone
 $("<center><!--<a border=0 target=PICASA href='"+photo_link+"'>--><img id='picture' width="+display_width+" src='"+img_base+"?imgmax="+photosize+"' class='pwimages' /><!--</a>--></center>");
 $("<br><center><div style='margin-left:2px'>"+j.entry.media$group.media$description.$t+"</div></center></p>");


 //now we will trap left and right arrow keys so we can scroll through the photos with a single keypress ;-) JMB 7/5/2007
 $('<script language="Javascript"> function testKeyCode( evt, intKeyCode ) { if ( window.createPopup ) return evt.keyCode == intKeyCode; else return evt.which == intKeyCode; } document.onkeydown = function ( evt ) { if ( evt == null ) evt = event; if ( testKeyCode( evt, 37 ) ) { window.location = "' + prev + '"; return false; } if ( testKeyCode( evt, 39 ) ) { window.location = "' + next + '"; return false; } } </script>');


 // an attempt at resampling the photo, rather than relying on the browser's internal resize function. doesn't work, unfortunately.
 //
 //$("<?php $filename='"+img_base+"?imgmax="+photosize+"'; $width = 658; $height = 1600; list($width_orig, $height_orig) = getimagesize($filename); ");
 //$("$ratio_orig = $width_orig/$height_orig; if ($width/$height > $ratio_orig) { $width = $height*$ratio_orig; } else { $height = $width/$ratio_orig; } ");
 //$("$image_p = imagecreatetruecolor($width, $height); $image = imagecreatefromjpeg($filename); ");
 //$("imagecopyresampled($image_p, $image, 0, 0, 0, 0, $width, $height, $width_orig, $height_orig); imagejpeg($image_p, null, 100); ?>");

}

if(_GET['photoid']&&_GET['albumid']){
 $('<script type="text/javascript" src="http://picasaweb.google.com/data/feed/base/user/'+username+'/albumid/'+_GET['albumid']+'?category=photo&alt=json&callback=getphotolist"></script>');//get the list of photos in the album and put it in the global "photolist" array so we can properly display the navigation arrows; this eliminates the need for really long URLs :-) 7/16/2007
 $('<script type="text/javascript" src="http://picasaweb.google.com/data/entry/base/user/'+username+'/albumid/'+_GET['albumid']+'/photoid/'+_GET['photoid']+'?alt=json&callback=photo"></script>');//photo
}else if(_GET['albumid']&&!_GET['photoid']){
 $('<script type="text/javascript" src="http://picasaweb.google.com/data/feed/base/user/'+username+'/albumid/'+_GET['albumid']+'?category=photo&alt=json&callback=albums"></script>');//albums
}else{
 $('<script type="text/javascript" src="http://picasaweb.google.com/data/feed/base/user/'+username+'?category=album&alt=json&callback=picasaweb&access=public"></script>');//picasaweb
}


//$Update: January 31, 2008$

/***********************************************************************
 * YAV - Yet Another Validator  v2.0                                   *
 * Copyright (C) 2005-2008                                             *
 * Author: Federico Crivellaro <f.crivellaro@gmail.com>                *
 * WWW: http://yav.sourceforge.net                                     *
 ***********************************************************************/

var yav = {

//------------------------------------------------------------ PUBLIC FUNCTIONS
undef: undefined,
isFocusSet: undefined,
internalRules: undefined,
f: undefined,
formEvt: undefined,
fieldsEvt: new Array(),
rulesEvt: new Array(),
helpEvt: new Array(),
mask: new Array(),
onOKEvt: new Array(),
onErrorEvt: new Array(),
preValidationEvt: new Array(),
filterByName: null,

performCheck: function (formName, strRules, alertType, filterErrorsByName) {
    yav.filterByName = (filterErrorsByName) ? filterErrorsByName: null;
    for(var j=0; j<yav.preValidationEvt.length; j++) {
        if (yav.filterByName==yav.preValidationEvt[j].name) {
            var preValidationResult = eval(yav.preValidationEvt[j].fn);
            yav.preValidationEvt[j].executedWithSuccess = preValidationResult;
            if (!preValidationResult) {
                return preValidationResult;
            }
            break;
        }
    }
    yav.isFocusSet = false;
    var rules = yav.makeRules(strRules);
    yav.internalRules = yav.makeRules(strRules);
    yav.f = document.forms[formName];
    if( !yav.f ) {
        yav.debug('DEBUG: could not find form object ' + formName);
        return null;
    }
    var errors = new Array();
    var ix = 0;
    if (rules.length) {
        for(var i=0; i<rules.length; i++) {
            var aRule = rules[i];
            if (aRule!=null) {
                yav.highlight(yav.getField(yav.f, aRule.el), yav_config.inputclassnormal);
            }
        }
    } else {
        if (rules!=null) {
            yav.highlight(yav.getField(yav.f, rules.el), yav_config.inputclassnormal);
        }
    }
    if (rules.length) {
        for(var i=0; i<rules.length; i++) {
            var aRule = rules[i];
            var anErr = null;
            if (aRule==null) {
                //do nothing
            } else if (aRule.ruleType=='pre-condition' || aRule.ruleType=='post-condition' || aRule.ruleType=='andor-operator') {
                //do nothing
            } else if (aRule.ruleName=='implies') {
                pre  = aRule.el;
                post = aRule.comparisonValue;
                var oldClassName = yav.getField(yav.f, rules[pre].el).className;
                if ( yav.filterByName!=null ) {
                    if (rules[pre].el==yav.filterByName || rules[post].el==yav.filterByName) {
                        yav.clearInlineSpans(rules[pre].el, rules[post].el);
                    }
                }
                if ( yav.checkRule(yav.f, rules[pre])==null && yav.checkRule(yav.f, rules[post])!=null ) {
                    anErr = yav.deleteInline(aRule.alertMsg) + '__inline__'+rules[post].el;
                } else if ( yav.checkRule(yav.f, rules[pre])!=null ) {
                    yav.getField(yav.f, rules[pre].el).className = oldClassName;
                }
            } else if (aRule.ruleName=='date_lt' || aRule.ruleName=='date_le') {
                if ( yav.filterByName!=null ) {
                    if (aRule.comparisonValue && aRule.comparisonValue.indexOf('$'+yav.filterByName)==0) {
                        yav.clearInlineSpans(aRule.el, yav.filterByName);
                    }
                }
                anErr = yav.checkRule(yav.f, aRule);
            } else {
                anErr = yav.checkRule(yav.f, aRule);
            }
            if ( anErr!=null ) {
                if (yav.filterByName && yav.filterByName!=null) {
                    if (aRule.ruleName=='implies') {
                        if (rules[pre].el==yav.filterByName || rules[post].el==yav.filterByName) {
                            yav.clearInlineSpans(rules[pre].el, rules[post].el);
                        }
                        aRule = rules[aRule.comparisonValue];
                    }
                    //todo
                    if (aRule.ruleName=='or') {
                        var tmp = aRule.comparisonValue.split('-');
                        for(var t=0; t<tmp.length; t++) {
                            yav.clearInlineSpans(rules[tmp[t]].el);
                        }
                        if (rules[aRule.el].el==yav.filterByName) {
                            yav.clearInlineSpans(rules[aRule.el].el);
                        }
                        aRule = rules[aRule.el];
                    }
                    //
                    if (aRule.el==yav.filterByName || (aRule.comparisonValue && aRule.comparisonValue.indexOf('$'+yav.filterByName)==0)) {
                        for(var z=0; z<rules.length; z++) {
                            if (rules[z].ruleName=='implies' && rules[rules[z].el].el==aRule.el) {
                                yav.clearInlineSpans(rules[rules[z].comparisonValue].el);
                            }
                        }
                        errors[ix] = anErr;
                        ix++;
                        break;              
                    }
                } else {
                    errors[ix] = anErr;
                    ix++;
                }
            }
        }//for
    } else {
        var myRule = rules;
        err = yav.checkRule(yav.f, myRule);
        if ( err!=null ) {
            if (yav.filterByName && yav.filterByName != null) {
                if (myRule.el == yav.filterByName) {
                    errors[0] = err;
                }
            } else {
                errors[0] = err;
            }
        }
    }
    var retval = yav.displayAlert(errors, alertType);
    yav.filterByName = null;
    return retval;
},

checkKeyPress: function (ev, obj, strRules) {
    var keyCode = null;
    keyCode = (typeof(ev.which))!='undefined' ? ev.which : window.event.keyCode;
    var rules = yav.makeRules(strRules);
    var keyAllowed = true;
    if (rules.length) {
        for(var i=0; i<rules.length; i++) {
            var aRule = rules[i];
            if (aRule.ruleName=='keypress' && aRule.el==obj.name) {
                keyAllowed = yav.isKeyAllowed(keyCode, aRule.comparisonValue);
                break;
            }
        }
    } else {
        var aRule = rules;
        if (aRule.ruleName=='keypress' && aRule.el==obj.name) {
            keyAllowed = yav.isKeyAllowed(keyCode, aRule.comparisonValue);
        }
    }
    if (!keyAllowed) {
        if ( typeof(ev.which)=='undefined' ) {
            window.event.keyCode=0;
        } else {
            ev.preventDefault();
            ev.stopPropagation();
            ev.returnValue=false;
        }
    }
    return keyAllowed;
},

init: function (formName, strRules) {
    yav.addMask('alphabetic', null, null, yav_config.alphabetic_regex);
    yav.addMask('alphanumeric', null, null, yav_config.alphanumeric_regex);
    yav.addMask('alnumhyphen', null, null, yav_config.alnumhyphen_regex);
    yav.addMask('alnumhyphenat', null, null, yav_config.alnumhyphenat_regex);
    yav.addMask('alphaspace', null, null, yav_config.alphaspace_regex);
    yav.formEvt = formName;
    yav.rulesEvt = strRules;
    if (strRules.length) {
        for(var i=0; i<strRules.length; i++) {
            var aRule = yav.splitRule(strRules[i]);
            var elm = yav.getField(document.forms[formName], aRule.el);
            if (elm && aRule.ruleName=='mask') {
                yav.addEvent(elm, 'keypress', yav.maskEvt.bindAsEventListener(elm));
            } else if (elm && !yav.inArray(yav.fieldsEvt, aRule.el) ) {
                var eventAdded = false;
                for(var j=0; j<yav.onOKEvt.length; j++) {
                    if (elm.name==yav.onOKEvt[j].name) {
                        yav.addEvent(elm, yav.onOKEvt[j].evType, 
                            function(){
                                if (yav.performEvt(this.name)) {
                                    yav.performOnOKEvt(this.name);
                                } else {
                                    for(var k=0; k<yav.preValidationEvt.length; k++) {
                                        if (this.name==yav.preValidationEvt[k].name) {
                                            if (yav.preValidationEvt[k].executedWithSuccess==false) {
                                                yav.preValidationEvt[k].executedWithSuccess = null;
                                                return;
                                            }
                                            yav.preValidationEvt[k].executedWithSuccess = null;
                                            break;
                                        }
                                    }
                                    yav.performOnErrorEvt(this.name);
                                }
                            } );
                        eventAdded = true;
                        break;
                    }
                }
                if (!eventAdded) {
                    for(var j=0; j<yav.onErrorEvt.length; j++) {
                        if (elm.name==yav.onErrorEvt[j].name) {
                            yav.addEvent(elm, yav.onErrorEvt[j].evType, 
                                function(){
                                    if (!yav.performEvt(this.name)) {
                                        for(var k=0; k<yav.preValidationEvt.length; k++) {
                                            if (this.name==yav.preValidationEvt[k].name) {
                                                if (yav.preValidationEvt[k].executedWithSuccess==false) {
                                                    yav.preValidationEvt[k].executedWithSuccess = null;
                                                    return;
                                                }
                                                yav.preValidationEvt[k].executedWithSuccess = null;
                                                break;
                                            }
                                        }
                                        yav.performOnErrorEvt(this.name);
                                    }
                                } );
                            eventAdded = true;
                            break;
                        }
                    }
                }
                yav.fieldsEvt.push(aRule.el);
                if (!eventAdded) {
                    yav.addEvent(elm, 'blur', 
                      function(){
                        yav.performEvt(this.name);
                      });
                }
            }
        }
    } else {
        var rule = yav.splitRule(strRules);
        var elm = yav.getField(document.forms[formName], rule.el);
        if (elm && rule.ruleName=='mask') {
            yav.addEvent(elm, 'keypress', yav.maskEvt.bindAsEventListener(elm));
        } else if (elm) {
            var eventAdded = false;
            for(var j=0; i<yav.onOKEvt.length; j++) {
                if (elm.name==yav.onOKEvt[i].name) {
                    yav.addEvent(elm, yav.onOKEvt[j].evType, 
                        function(){
                            if (yav.performEvt(this.name)) {
                                yav.performOnOKEvt(this.name);
                            }
                        } );
                    eventAdded = true;
                    break;
                }
            }
            for(var j=0; j<yav.onErrorEvt.length; j++) {
                if (elm.name==yav.onErrorEvt[j].name) {
                    yav.addEvent(elm, yav.onErrorEvt[j].evType, 
                        function(){
                            if (!yav.performEvt(this.name)) {
                                for(var k=0; k<yav.preValidationEvt.length; k++) {
                                    if (this.name==yav.preValidationEvt[k].name) {
                                        if (yav.preValidationEvt[k].executedWithSuccess==false) {
                                            yav.preValidationEvt[k].executedWithSuccess = null;
                                            return;
                                        }
                                        yav.preValidationEvt[k].executedWithSuccess = null;
                                        break;
                                    }
                                }
                                yav.performOnErrorEvt(this.name);
                            }
                        } );
                    eventAdded = true;
                    break;
                }
            }
            if (!eventAdded) {
                yav.addEvent(elm, 'blur', 
                  function(){
                    yav.performEvt(this.name);
                  });
            }
        }
    }
    if (yav.helpEvt.length>0) {
        for(var i=0; i<yav.helpEvt.length; i++) {
            var elm = yav.getField(document.forms[formName], yav.helpEvt[i].name);
            if ( elm ) {
                if ( elm.focus ) {
                    yav.addEvent(elm, 'focus', 
                      function(){
                        yav.showHelpEvt(this.name);
                      });
                } else {
                    yav.addEvent(elm, 'click', 
                      function(){
                        yav.showHelpEvt(this.name);
                      });
                }
                if ( !yav.inArray(yav.fieldsEvt, yav.helpEvt[i].name) ) {
                    yav.addEvent(elm, 'blur', 
                      function(){
                        yav.cleanInline(this.name);
                      });
                }
            }
        }
    }
},

displayMsg: function(name, msg, clazz) {
    var elm = yav.get(yav_config.errorsdiv+'_'+name);
    if (elm) {
        elm.innerHTML = msg;
        elm.className = clazz;
        elm.style.display = '';
    } else {
        elm = yav.get(yav_config.errorsdiv);
        if (elm) {
            elm.innerHTML = msg;
            elm.className = clazz;
            elm.style.display = '';
        } else {
            alert(msg);
        }
    }
},

cleanInline: function(name) {
    yav.get(yav_config.errorsdiv+'_'+name).innerHTML = '';
    yav.get(yav_config.errorsdiv+'_'+name).className = '';
    yav.get(yav_config.errorsdiv+'_'+name).style.display = 'none';
},

addHelp: function (name, helpMsg) {
    var elem = new Object();
    elem.name = name;
    elem.help = helpMsg;
    yav.helpEvt.push(elem);
},

addMask: function (name, format, charsAllowed, regex) {
    var elem = new Object();
    elem.name = name;
    elem.format = format;
    elem.charsAllowed = charsAllowed;
    elem.regex = regex ? regex : null;
    yav.mask.push(elem);
},

postValidation_OnOK: function(name, evType, fn){
    var elem = new Object();
    elem.name = name;
    elem.evType = evType;
    elem.fn = fn;
    yav.onOKEvt.push(elem);
},

postValidation_OnError: function(name, evType, fn){
    var elem = new Object();
    elem.name = name;
    elem.evType = evType;
    elem.fn = fn;
    yav.onErrorEvt.push(elem);
},

preValidation: function(fn, name){
    var elem = new Object();
    elem.name = (name && name!=null)? name : null;
    elem.fn = fn;
    elem.executedWithSuccess = null;
    yav.preValidationEvt.push(elem);
},

//------------------------------------------------------------ PRIVATE FUNCTIONS

inArray: function(arr, value) {
    var found = false;
    for (var i=0;i<arr.length;i++) {
        if (arr[i]==value) {
            found = true;
            break;
        }
    }
    return found;
},

performEvt: function(name) {
    var elm = yav.get(yav_config.errorsdiv);
    if (elm) {
        elm.innerHTML = '';
        elm.className = '';
        elm.style.display = 'none';
    }
    return yav.performCheck(yav.formEvt, yav.rulesEvt, 'inline', name); 
},

performOnOKEvt: function(name) {
    for(var j=0; j<yav.onOKEvt.length; j++) {
        if (name==yav.onOKEvt[j].name) {
            eval(yav.onOKEvt[j].fn);
            break;
        }
    }
},

performOnErrorEvt: function(name) {
    for(var j=0; j<yav.onErrorEvt.length; j++) {
        if (name==yav.onErrorEvt[j].name) {
            eval(yav.onErrorEvt[j].fn);
            break;
        }
    }
},

showHelpEvt: function(name) {
    for(var i=0; i<yav.helpEvt.length; i++) {
        if (yav.helpEvt[i].name==name) {
            yav.get(yav_config.errorsdiv+'_'+name).innerHTML = yav.helpEvt[i].help;
            yav.get(yav_config.errorsdiv+'_'+name).className = yav_config.innerhelp;
            yav.get(yav_config.errorsdiv+'_'+name).style.display = '';
            break;
        }
    }
},

maskEvt: function(ev) {
    var mask = null;
    var myRule = null;
    for(var i=0; i<yav.rulesEvt.length; i++) {
        var aRule = yav.splitRule(yav.rulesEvt[i]);
        var elm = yav.getField(document.forms[yav.formEvt], aRule.el);
        if (elm && aRule.ruleName=='mask' && elm.name==this.name) {
            for(var j=0; j<yav.mask.length; j++) {
                if ( yav.mask[j].name==aRule.comparisonValue ) {
                    mask = yav.mask[j];
                    break;
                }
            }
            myRule = aRule;
            break;
        }
    }
    var key  = (typeof(ev.which))!='undefined' ? ev.which : window.event.keyCode;
    var ch      = String.fromCharCode(key);
    var str     = this.value + ch;
    var pos     = str.length;
    if (key==8 || key==0) { 
        return true;
    }
    var keyAllowed = false;
    if (mask==null) {
        if ( yav.isKeyAllowed(key, myRule.comparisonValue) ) {
            keyAllowed = true;
        } else {
            if ( typeof(ev.which)=='undefined' ) {
                window.event.keyCode=0;
            } else {
                ev.preventDefault();
                ev.stopPropagation();
                ev.returnValue=false;
            }
        }
        return keyAllowed;
    } else if ( mask.format==null ) {
        reg = new RegExp(mask.regex);
        if ( reg.test(ch) ) {
            keyAllowed = true;
        } else {
            if ( typeof(ev.which)=='undefined' ) {
                window.event.keyCode=0;
            } else {
                ev.preventDefault();
                ev.stopPropagation();
                ev.returnValue=false;
            }
        }
        return keyAllowed;
    } else if ( yav.isKeyAllowed(key, mask.charsAllowed) && pos <= mask.format.length ) {
        if ( mask.format.charAt(pos - 1) != ' ' ) {
            str = this.value + mask.format.charAt(pos - 1) + ch;
        }
        this.value = str;
        keyAllowed = true;
    }
    if ( typeof(ev.which)=='undefined' ) {
        window.event.keyCode=0;
    } else {
        ev.preventDefault();
        ev.stopPropagation();
        ev.returnValue=false;
    }
    return keyAllowed;
},

displayAlert: function (messages, alertType) {
    var retval =null;
    yav.clearAllInlineSpans();
    if (alertType=='classic') {
        retval = yav.displayClassic(messages);
    } else if (alertType=='innerHtml') {
        retval = yav.displayInnerHtml(messages);
    }else if (alertType=='inline') {
        retval = yav.displayInline(messages);
    }else if (alertType=='jsVar') {
        retval = yav.displayJsVar(messages);
    } else {
        yav.debug('DEBUG: alert type ' + alertType + ' not supported');
    }
    return retval;
},

displayClassic: function (messages) {
    var str = '';
    if ( messages!=null && messages.length>0 ) {
        if (yav.strTrim(yav_config.HEADER_MSG).length > 0) {
            str += yav_config.HEADER_MSG + '\n\n';
        }
        for (var i=0; i<messages.length; i++) {
            str += ' ' + yav.deleteInline(messages[i]) + '\n';
        }
        if (yav.strTrim(yav_config.FOOTER_MSG).length > 0) {
            str += '\n' + yav_config.FOOTER_MSG;
        }
        alert(str);
        return false;
    } else {
        return true;
    }
},

displayInnerHtml: function (messages) {
    if ( messages!=null && messages.length>0 ) {
        var str = '';
        if (yav.strTrim(yav_config.HEADER_MSG).length > 0) {
            str += yav_config.HEADER_MSG;
        }
        str += '<ul>';
        for (var i=0; i<messages.length; i++) {
            str += '<li>'+yav.deleteInline(messages[i])+'</li>';
        }
        str += '</ul>';
        if (yav.strTrim(yav_config.FOOTER_MSG).length > 0) {
            str += yav_config.FOOTER_MSG;
        }
        yav.get(yav_config.errorsdiv).innerHTML = str;
        yav.get(yav_config.errorsdiv).className = yav_config.innererror;
        yav.get(yav_config.errorsdiv).style.display = 'block';
        return false;
    } else {
        yav.get(yav_config.errorsdiv).innerHTML = '';
        yav.get(yav_config.errorsdiv).className = '';
        yav.get(yav_config.errorsdiv).style.display = 'none';
        return true;
    }
},

displayInline: function (messages) {
    if ( messages!=null && messages.length>0 ) {
        var genericErrors = new Array();
        var genericErrIndex = 0;
        for (var i=0; i<messages.length; i++) {
            var elName = messages[i].substring(messages[i].indexOf('__inline__')+10);
            if ( yav.get(yav_config.errorsdiv+'_'+elName) ) {
                yav.get(yav_config.errorsdiv+'_'+elName).innerHTML = yav.deleteInline(messages[i]);
                yav.get(yav_config.errorsdiv+'_'+elName).className = yav_config.innererror;
                yav.get(yav_config.errorsdiv+'_'+elName).style.display = '';
            } else {
                genericErrors[genericErrIndex] = messages[i];
                genericErrIndex++;
            }
        }
        if (genericErrIndex>0) {
            yav.displayInnerHtml(genericErrors);
        }
        return false;
    } else {
        return true;
    }
},

clearAllInlineSpans: function () {
    var allDivs = document.getElementsByTagName("span");
    for (var j=0; j<allDivs.length; j++) {
        var idName = allDivs[j].id;
        if ( idName.indexOf(yav_config.errorsdiv+'_')==0 ) {
            if (yav.filterByName!=null) {
                if ( idName==yav_config.errorsdiv+'_'+yav.filterByName ) {
                    yav.get(idName).innerHTML = '';
                    yav.get(idName).className = '';
                    yav.get(idName).style.display = 'none';
                }
            } else {
                yav.get(idName).innerHTML = '';
                yav.get(idName).className = '';
                yav.get(idName).style.display = 'none';
            }
        }
    }
},

clearInlineSpans: function () {
    var allDivs = document.getElementsByTagName("span");
    for (var j=0; j<allDivs.length; j++) {
        var idName = allDivs[j].id;
        if ( idName.indexOf(yav_config.errorsdiv+'_')==0 ) {
            for (var k=0; k<arguments.length; k++) {
                if ( idName==yav_config.errorsdiv+'_'+arguments[k] ) {
                    yav.get(idName).innerHTML = '';
                    yav.get(idName).className = '';
                    yav.get(idName).style.display = 'none';
                }
            }
        }
    }
},

displayJsVar: function (messages) {
    yav.get(yav_config.errorsdiv).className = '';
    yav.get(yav_config.errorsdiv).style.display = 'none';
    if ( messages!=null && messages.length>0 ) {
        for (var i=0; i<messages.length; i++) {
            messages[i] = yav.deleteInline(messages[i]);
        }
        var str = '';
        str += '<script>var jsErrors;</script>';
        yav.get(yav_config.errorsdiv).innerHTML = str;
        jsErrors = messages;
        return false;
    } else {
        yav.get(yav_config.errorsdiv).innerHTML = '<script>var jsErrors;</script>';
        return true;
    }
},

rule: function (el, ruleName, comparisonValue, alertMsg, ruleType) {
    var checkArguments = arguments.length>=4 && arguments[0]!=null && arguments[1]!=null;
    if ( !checkArguments ) {
        return false;
    }
    tmp = el.split(':');
    nameDisplayed = '';
    if (tmp.length == 2) {
        nameDisplayed = tmp[1];
        el = tmp[0];
    }
    this.el = el;
    this.nameDisplayed = nameDisplayed;
    this.ruleName = ruleName;
    this.comparisonValue = comparisonValue;
    this.ruleType = ruleType;
    if (alertMsg==yav.undef || alertMsg==null) {
        this.alertMsg = yav.getDefaultMessage(el, nameDisplayed, ruleName, comparisonValue)+'__inline__'+this.el;
    } else {
        this.alertMsg = alertMsg+'__inline__'+this.el;
    }
},

checkRule: function (f, myRule) {
    retVal = null;
    if (myRule != null) {
        if (myRule.ruleName=='custom') {
            var customFunction = null;
            if (myRule.comparisonValue!=null) {
                customFunction = ' retVal = ' + myRule.comparisonValue;
            } else { // deprecated, maintained for back compatibility
                customFunction = ' retVal = ' + myRule.el;
            }
            retVal = eval(customFunction);
            if (myRule.comparisonValue!=null && retVal!=this.undef && retVal!=null) {
                retVal += '__inline__'+myRule.el;
            }
            if (retVal!=null && myRule.comparisonValue!=null) {
                yav.highlight(yav.getField(yav.f, myRule.el), yav_config.inputclasserror);
            }
        } else if (myRule.ruleName=='and') {
            var op_1 = myRule.el;
            var op_next = myRule.comparisonValue;
            if ( yav.checkRule(f, yav.internalRules[op_1])!=null ) {
                retVal = myRule.alertMsg;
                if (myRule.ruleType=='pre-condition' || myRule.ruleType=='andor-operator') {
                    //yav.highlight(yav.getField(f, yav.internalRules[op_1].el), yav_config.inputclasserror);
                }
            } else {
                var op_k = op_next.split('-');
                for(var k=0; k<op_k.length; k++) {
                    if ( yav.checkRule(f, yav.internalRules[op_k[k]])!=null ) {
                        retVal = myRule.alertMsg;
                        if (myRule.ruleType=='pre-condition' || myRule.ruleType=='andor-operator') {
                            //yav.highlight(yav.getField(f, yav.internalRules[op_k[k]].el), yav_config.inputclasserror);
                        }
                        break;
                    }
                }
            }
        } else if (myRule.ruleName=='or') {
            var op_1 = myRule.el;
            var op_next = myRule.comparisonValue;
            var success = false;
            if ( yav.checkRule(f, yav.internalRules[op_1])==null ) {
                success = true;
            } else {
                if (myRule.ruleType=='pre-condition' || myRule.ruleType=='andor-operator') {
                    //yav.highlight(yav.getField(f, yav.internalRules[op_1].el), yav_config.inputclasserror);
                }
                var op_k = op_next.split('-');
                for(var k=0; k<op_k.length; k++) {
                    if ( yav.checkRule(f, yav.internalRules[op_k[k]])==null ) {
                        success = true;
                        break;
                    } else {
                        if (myRule.ruleType=='pre-condition' || myRule.ruleType=='andor-operator') {
                            //yav.highlight(yav.getField(f, yav.internalRules[op_k[k]].el), yav_config.inputclasserror);
                        }
                    }
                }
            }
            if (success) {
                yav.highlight(yav.getField(f, yav.internalRules[op_1].el), yav_config.inputclassnormal);
                var op_k = op_next.split('-');
                for(var k=0; k<op_k.length; k++) {
                    yav.highlight(yav.getField(f, yav.internalRules[op_k[k]].el), yav_config.inputclassnormal);
                }
            } else {
                retVal = myRule.alertMsg;
            }
        } else {
            el = yav.getField(f, myRule.el);
            if (el == null) {
                yav.debug('DEBUG: could not find element ' + myRule.el);
                return null;
            }
            var err = null;
            if(el.type) {
                if(el.type=='hidden'||el.type=='text'||el.type=='password'||el.type=='textarea') {
                    err = yav.checkText(el, myRule);
                } else if(el.type=='checkbox') {
                    err = yav.checkCheckbox(el, myRule);
                } else if(el.type=='select-one') {
                    err = yav.checkSelOne(el, myRule);
                } else if(el.type=='select-multiple') {
                    err = yav.checkSelMul(el, myRule);
                } else if(el.type=='radio') {
                    err = yav.checkRadio(el, myRule);
                } else {
                    yav.debug('DEBUG: type '+ el.type +' not supported');
                }
            } else {
                err = yav.checkRadio(el, myRule);
            }
            retVal = err;
        }
    }
    return retVal;
},

checkRadio: function (el, myRule) {
    var err = null;
    if (myRule.ruleName=='required') {
        var radios = el;
        var found=false;
        if (isNaN(radios.length) && radios.checked) {
            found=true;
        } else {
            for(var j=0; j < radios.length; j++) {
                if(radios[j].checked) {
                    found=true;
                    break;
                }
            }
        }
        if( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='equal') {
        var radios = el;
        var found=false;
        if (isNaN(radios.length) && radios.checked) {
            if (radios.value==myRule.comparisonValue) {
                found=true;
            }
        } else {
            for(var j=0; j < radios.length; j++) {
                if(radios[j].checked) {
                    if (radios[j].value==myRule.comparisonValue) {
                        found=true;
                        break;
                    }
                }
            }
        }
        if( !found ) {
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='notequal') {
        var radios = el;
        var found=false;
        if (isNaN(radios.length) && radios.checked) {
            if (radios.value!=myRule.comparisonValue) {
                found=true;
            }
        } else {
            for(var j=0; j < radios.length; j++) {
                if(radios[j].checked) {
                    if (radios[j].value!=myRule.comparisonValue) {
                        found=true;
                        break;
                    }
                }
            }
        }
        if( !found ) {
            err = myRule.alertMsg;
        }
    } else {
        yav.debug('DEBUG: rule ' + myRule.ruleName + ' not supported for radio');
    }
    return err;
},

checkText: function (el, myRule) {
    err = null;
    if (yav_config.trimenabled) {
        el.value = yav.strTrim(el.value);
    }
    if (myRule.ruleName=='required') {
        if ( el.value==null || el.value=='' ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='equal') {
        err = yav.checkEqual(el, myRule);
    } else if (myRule.ruleName=='notequal') {
        err = yav.checkNotEqual(el, myRule);
    } else if (myRule.ruleName=='numeric') {
        reg = new RegExp("^[0-9]*$");
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='alphabetic') {
        reg = new RegExp(yav_config.alphabetic_regex);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='alphanumeric') {
        reg = new RegExp(yav_config.alphanumeric_regex);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='alnumhyphen') {
        reg = new RegExp(yav_config.alnumhyphen_regex);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='alnumhyphenat') {
        reg = new RegExp(yav_config.alnumhyphenat_regex);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='alphaspace') {
        reg = new RegExp(yav_config.alphaspace_regex);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='email') {
        reg = new RegExp(yav_config.email_regex);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='maxlength') {
        if ( isNaN(myRule.comparisonValue) ) {
            yav.debug('DEBUG: comparisonValue for rule ' + myRule.ruleName + ' not a number');
        }else if ( el.value.length > myRule.comparisonValue ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='minlength') {
        if ( isNaN(myRule.comparisonValue) ) {
            yav.debug('DEBUG: comparisonValue for rule ' + myRule.ruleName + ' not a number');
        } else if ( el.value.length < myRule.comparisonValue ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='numrange') {
        reg = new RegExp("^[-+]{0,1}[0-9]*[.]{0,1}[0-9]*$");
        if ( !reg.test(yav.unformatNumber(el.value)) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        } else {
            regRange = new RegExp("^[0-9]+-[0-9]+$"); 
            if ( !regRange.test(myRule.comparisonValue) ) {
                yav.debug('DEBUG: comparisonValue for rule ' + myRule.ruleName + ' not in format number1-number2');
            } else {
                rangeVal = myRule.comparisonValue.split('-');
                if (eval(yav.unformatNumber(el.value))<eval(rangeVal[0]) || eval(yav.unformatNumber(el.value))>eval(rangeVal[1])) {
                    yav.highlight(el, yav_config.inputclasserror); 
                    err = myRule.alertMsg;
                }
            }
        }
    } else if (myRule.ruleName=='regexp') {
        reg = new RegExp(myRule.comparisonValue);
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else if (myRule.ruleName=='integer') {
        err = yav.checkInteger(el, myRule);
    } else if (myRule.ruleName=='double') {
        err = yav.checkDouble(el, myRule);
    } else if (myRule.ruleName=='date') {
        err = yav.checkDate(el, myRule);
    } else if (myRule.ruleName=='date_lt') {
        err = yav.checkDateLessThan(el, myRule, false);
    } else if (myRule.ruleName=='date_le') {
        err = yav.checkDateLessThan(el, myRule, true);
    } else if (myRule.ruleName=='keypress') {
        // do nothing
    } else if (myRule.ruleName=='empty') {
        if ( el.value!=null && el.value!='' ) {
            yav.highlight(el, yav_config.inputclasserror);
            err = myRule.alertMsg;
        }
    } else {
        yav.debug('DEBUG: rule ' + myRule.ruleName + ' not supported for ' + el.type);
    }
    return err;
},

checkInteger: function (el, myRule) {
    reg = new RegExp("^[-+]{0,1}[0-9]*$");
    if ( !reg.test(el.value) ) {
        yav.highlight(el, yav_config.inputclasserror);
        return myRule.alertMsg;
    }
},

checkDouble: function (el, myRule) {
    var sep = yav_config.DECIMAL_SEP;
    reg = new RegExp("^[-+]{0,1}[0-9]*[" + sep + "]{0,1}[0-9]*$");
    if ( !reg.test(el.value) ) {
        yav.highlight(el, yav_config.inputclasserror);
        return myRule.alertMsg;
    }
},

checkDate: function (el, myRule) {
    error = null;
    if (el.value!='') {
        var dateFormat = yav_config.DATE_FORMAT;
        ddReg = new RegExp("dd");
        MMReg = new RegExp("MM");
        yyyyReg = new RegExp("yyyy");
        if ( !ddReg.test(dateFormat) || !MMReg.test(dateFormat) || !yyyyReg.test(dateFormat)  ) {
            yav.debug('DEBUG: locale format ' + dateFormat + ' not supported');
        } else {
            ddStart = dateFormat.indexOf('dd');
            MMStart = dateFormat.indexOf('MM');
            yyyyStart = dateFormat.indexOf('yyyy');
        }
        strReg = dateFormat.replace('dd','[0-9]{2}').replace('MM','[0-9]{2}').replace('yyyy','[0-9]{4}');
        reg = new RegExp("^" + strReg + "$");
        if ( !reg.test(el.value) ) {
            yav.highlight(el, yav_config.inputclasserror);
            error = myRule.alertMsg;
        } else {
            dd   = el.value.substring(ddStart, ddStart+2);
            MM   = el.value.substring(MMStart, MMStart+2);
            yyyy = el.value.substring(yyyyStart, yyyyStart+4);
            if ( !yav.checkddMMyyyy(dd, MM, yyyy) ) {
                yav.highlight(el, yav_config.inputclasserror);
                error = myRule.alertMsg;
            }
        }
    }
    return error;
},

checkDateLessThan: function (el, myRule, isEqualAllowed) {
    error = null;
    var isDate = yav.checkDate(el, myRule)==null ? true : false;
    if ( isDate && el.value!='' ) {
        var dateFormat = yav_config.DATE_FORMAT;
        ddStart = dateFormat.indexOf('dd');
        MMStart = dateFormat.indexOf('MM');
        yyyyStart = dateFormat.indexOf('yyyy');
        dd   = el.value.substring(ddStart, ddStart+2);
        MM   = el.value.substring(MMStart, MMStart+2);
        yyyy = el.value.substring(yyyyStart, yyyyStart+4);
        myDate = "" + yyyy + MM + dd;
        strReg = dateFormat.replace('dd','[0-9]{2}').replace('MM','[0-9]{2}').replace('yyyy','[0-9]{4}');
        reg = new RegExp("^" + strReg + "$");
        var isMeta = myRule.comparisonValue.indexOf('$')==0 
            ? true
            : false;
        var comparisonDate = '';
        if (isMeta) {
            toSplit = myRule.comparisonValue.substr(1);
            tmp = toSplit.split(':');
            if (tmp.length == 2) {
                comparisonDate = yav.getField(yav.f, tmp[0]).value;
            } else {
                comparisonDate = yav.getField(yav.f, myRule.comparisonValue.substr(1)).value;
            }
        } else {
            comparisonDate = myRule.comparisonValue;
        }
        if ( !reg.test(comparisonDate) ) {
            yav.highlight(el, yav_config.inputclasserror);
            error = myRule.alertMsg;
        } else {
            cdd   = comparisonDate.substring(ddStart, ddStart+2);
            cMM   = comparisonDate.substring(MMStart, MMStart+2);
            cyyyy = comparisonDate.substring(yyyyStart, yyyyStart+4);
            cDate = "" + cyyyy + cMM + cdd;
            if (isEqualAllowed) {
                if ( !yav.checkddMMyyyy(cdd, cMM, cyyyy) || myDate>cDate ) {
                    yav.highlight(el, yav_config.inputclasserror);
                    error = myRule.alertMsg;
                }
            } else {
                if ( !yav.checkddMMyyyy(cdd, cMM, cyyyy) || myDate>=cDate ) {
                    yav.highlight(el, yav_config.inputclasserror);
                    error = myRule.alertMsg;
                }
            }
        }
    } else {
        if ( el.value!='' ) {
            yav.highlight(el, yav_config.inputclasserror);
            error = myRule.alertMsg;
        }
    }
    return error;
},

checkEqual: function (el, myRule) {
    error = null;
    var isMeta = myRule.comparisonValue.indexOf('$')==0 
        ? true
        : false;
    var comparisonVal = '';
    if (isMeta) {
        toSplit = myRule.comparisonValue.substr(1);
        tmp = toSplit.split(':');
        if (tmp.length == 2) {
            comparisonVal = yav.getField(yav.f, tmp[0]).value;
        } else {
            comparisonVal = yav.getField(yav.f, myRule.comparisonValue.substr(1)).value;
        }
    } else {
        comparisonVal = myRule.comparisonValue;
    }
    if ( el.value!=comparisonVal ) {
        yav.highlight(el, yav_config.inputclasserror);
        error = myRule.alertMsg;
    }
    return error;
},

checkNotEqual: function (el, myRule) {
    error = null;
    var isMeta = myRule.comparisonValue.indexOf('$')==0 
        ? true
        : false;
    var comparisonVal = '';
    if (isMeta) {
        toSplit = myRule.comparisonValue.substr(1);
        tmp = toSplit.split(':');
        if (tmp.length == 2) {
            comparisonVal = yav.getField(yav.f, tmp[0]).value;
        } else {
            comparisonVal = yav.getField(yav.f, myRule.comparisonValue.substr(1)).value;
        }
    } else {
        comparisonVal = myRule.comparisonValue;
    }
    if ( el.value==comparisonVal ) {
        yav.highlight(el, yav_config.inputclasserror);
        error = myRule.alertMsg;
    }
    return error;
},

checkddMMyyyy: function (dd, MM, yyyy) {
    retVal = true;
    if (    (dd<1) || (dd>31) || (MM<1) || (MM>12) ||
            (dd==31 && (MM==2 || MM==4 || MM==6 || MM==9 || MM==11) ) ||
            (dd >29 && MM==2) ||
            (dd==29 && (MM==2) && ((yyyy%4 > 0) || (yyyy%4==0 && yyyy%100==0 && yyyy%400>0 )) )) {
       retVal = false;
    }
    return retVal;
},

checkCheckbox: function (el, myRule) {
    if (myRule.ruleName=='required') {
        if ( !el.checked ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else if (myRule.ruleName=='equal') {
        if ( !el.checked || el.value!=myRule.comparisonValue ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else if (myRule.ruleName=='notequal') {
        if ( el.checked && el.value==myRule.comparisonValue ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else {
        yav.debug('DEBUG: rule ' + myRule.ruleName + ' not supported for ' + el.type);
    }
},

checkSelOne: function (el, myRule) {
    if (myRule.ruleName=='required') {
        var found = false;
        var inx = el.selectedIndex;
        if(inx>=0 && el.options[inx].value) {
            found = true;
        }
        if ( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else if (myRule.ruleName=='equal') {
        var found = false;
        var inx = el.selectedIndex;
        if(inx>=0 && el.options[inx].value==myRule.comparisonValue) {
            found = true;
        }
        if ( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else if (myRule.ruleName=='notequal') {
        var found = false;
        var inx = el.selectedIndex;
        if(inx>=0 && el.options[inx].value!=myRule.comparisonValue) {
            found = true;
        }
        if ( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else {
        yav.debug('DEBUG: rule ' + myRule.ruleName + ' not supported for ' + el.type);
    }
},

checkSelMul: function (el, myRule) {
    if (myRule.ruleName=='required') {
        var found = false;
        opts = el.options;
        for(var i=0; i<opts.length; i++) {
            if(opts[i].selected && opts[i].value) {
                found = true;
                break;
            }
        }
        if ( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else if (myRule.ruleName=='equal') {
        var found = false;
        opts = el.options;
        for(var i=0; i<opts.length; i++) {
            if(opts[i].selected && opts[i].value==myRule.comparisonValue) {
                found = true;
                break;
            }
        }
        if ( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else if (myRule.ruleName=='notequal') {
        var found = false;
        opts = el.options;
        for(var i=0; i<opts.length; i++) {
            if(opts[i].selected && opts[i].value!=myRule.comparisonValue) {
                found = true;
                break;
            }
        }
        if ( !found ) {
            yav.highlight(el, yav_config.inputclasserror);
            return myRule.alertMsg;
        }
    } else {
        yav.debug('DEBUG: rule ' + myRule.ruleName + ' not supported for ' + el.type);
    }
},

debug: function (msg) {
   if (yav_config.debugmode) {
        alert(msg);
   }
},

strTrim: function (str) {
    return str.replace(/^\s+/,'').replace(/\s+$/,'');
},

makeRules: function (strRules) {
    var rules=new Array();
    if (strRules.length) {
        for(var i=0; i<strRules.length; i++) {
            rules[i] = yav.splitRule(strRules[i]);
        }
    } else {
        rules[0] = yav.splitRule(strRules);
    }
    return rules;
},

splitRule: function (strRule) {
    var retval = null;
    if (strRule!=yav.undef) {
        params = strRule.split(yav_config.RULE_SEP);
        switch (params.length) {
            case 2:
                retval = new yav.rule(params[0], params[1], null, null, null);
                break;
            case 3:
                if (yav.threeParamRule(params[1])) {
                    retval = new yav.rule(params[0], params[1], params[2], null, null);
                } else if (params[2]=='pre-condition' || params[2]=='post-condition' || params[2]=='andor-operator') {
                    retval = new yav.rule(params[0], params[1], null, 'foo', params[2]);
                } else {
                    retval = new yav.rule(params[0], params[1], null, params[2], null);
                }
                break;
            case 4:
                if (yav.threeParamRule(params[1]) && (params[3]=='pre-condition' || params[3]=='post-condition' || params[3]=='andor-operator')) {
                    retval = new yav.rule(params[0], params[1], params[2], 'foo', params[3]);
                } else {
                    retval = new yav.rule(params[0], params[1], params[2], params[3], null);
                }
                break;
            default:
                yav.debug('DEBUG: wrong definition of rule');
        }
    }
    return retval;
},

threeParamRule: function (ruleName) {
    return (ruleName=='equal' || ruleName=='notequal' || ruleName=='minlength' || ruleName=='maxlength' || ruleName=='date_lt' || ruleName=='date_le' || ruleName=='implies' || ruleName=='regexp' || ruleName=='numrange' || ruleName=='keypress' || ruleName=='and' || ruleName=='or' || ruleName=='custom' || ruleName=='mask')
        ? true
        : false;
},

highlight: function (el, clazz) {
    if (yav.rulesEvt.length>0 && clazz==yav_config.inputclasserror) {
        return;
    }
    if (!yav.isFocusSet && clazz==yav_config.inputclasserror) {
        if (  (!el.type) && (el.length>0) && (el.item(0).type=='radio') ) {
            el.item(0).focus();
        } else {
            el.focus();   
        }
        yav.isFocusSet = true;
    }
    if (el!=yav.undef && yav_config.inputhighlight) {
        if ( yav_config.multipleclassname ) {
            yav.highlightMultipleClassName(el, clazz);
        } else {
            el.className = clazz;
        }        
    }
},

highlightMultipleClassName: function (el, clazz) {
    re = new RegExp("(^|\\s)("+yav_config.inputclassnormal+"|"+yav_config.inputclasserror+")($|\\s)");
    el.className = yav.strTrim (
    ( (typeof el.className != "undefined")
        ? el.className.replace(re, "")
        : ""
    ) + " " + clazz );
}

}//end namespace 'yav'
