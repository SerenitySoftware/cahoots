//Get window height
function getInsideWindowHeight( )
{
    if (window.innerHeight)
        return window.innerHeight;

    if (document.compatMode && document.compatMode.indexOf("CSS1") >= 0)
        return document.body.parentElement.clientHeight;

    if (document.body && document.body.clientHeight)
        return document.body.clientHeight;

    return 0;
}

//Get window width
function getInsideWindowWidth( )
{
    if (window.innerWidth)
        return window.innerWidth;

    if (document.compatMode && document.compatMode.indexOf("CSS1") >= 0)
        return document.body.parentElement.clientWidth;

    if (document.body && document.body.clientWidth)
        return document.body.clientWidth;

    return 0;
}

//resize lines to fit page
function resize()
{
    var i;
    
    i = document.getElementById("vline");
    if (i) i.height = (getInsideWindowHeight() - 100);

    i = document.getElementById("hline1");
    if (i) i.width = getInsideWindowWidth();

    i = document.getElementById("hline2");
    if (i) i.width = getInsideWindowWidth();
}

//perform login
function login(params)
{
    var width   = 600;
    var height  = 250;
    var left    = (screen.availWidth - width)/2;
    var top     = (screen.availHeight - height)/2;
    var options = "width=" + width + ",height=" + height +
                  ",directories=no,status=no,scrollbars=no,menubar=no,resizable=no" +
                  ",left=" + left + ",top=" + top + ",screenX=" + left + ",screenY=" + top;

    //display initialize window
    var w = window.open('Initialize.asp' + params,'', options);
    w.focus();
    return;
}

//validate
function validForm()
{
    document.frmLogin.submit();
}

//capture key press
var ns4 = (window.navigator.appName != "Microsoft Internet Explorer");
if (ns4) document.captureEvents(Event.KEYDOWN);
document.onkeydown = checkKey;

//check pressed key
function checkKey(e)
{
    var k = (ns4) ? e.keyCode : window.event.keyCode;
    if (k == 13) validForm();
    return;
}