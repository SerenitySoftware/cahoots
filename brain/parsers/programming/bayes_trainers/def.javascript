
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


//$Update: January 31, 2008$

/***********************************************************************
 * YAV - Yet Another Validator  v2.0                                   *
 * Copyright (C) 2005-2008                                             *
 * Author: Federico Crivellaro <f.crivellaro@gmail.com>                *
 * WWW: http://yav.sourceforge.net                                     *
 ***********************************************************************/

var yav = {

performCheck: function (formName, strRules, alertType, filterErrorsByName) {

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

/*!
 * jQuery JavaScript Library v1.8.0pre 9a40b1848a77e106d8ff96d40ca01d9b325f63bc
 * http://jquery.com/
 *
 * Copyright (c) 2012 jQuery Foundation and other contributors
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * Includes Sizzle.js
 * http://sizzlejs.com/
 * Copyright 2012, The Dojo Foundation
 * Released under the MIT, BSD, and GPL Licenses.
 *
 * Date: Wed Jul 04 2012 14:11:16 GMT-0700 (PDT)
 */
(function( window, undefined ) {
var
  // Use the correct document accordingly with window argument (sandbox)
  document = window.document,
  location = window.location,
  navigator = window.navigator,

  // Map over jQuery in case of overwrite
  _jQuery = window.jQuery,

  // Map over the $ in case of overwrite
  _$ = window.$,

  // Save a reference to some core methods
  core_push = Array.prototype.push,
  core_slice = Array.prototype.slice,
  core_indexOf = Array.prototype.indexOf,
  core_toString = Object.prototype.toString,
  core_hasOwn = Object.prototype.hasOwnProperty,
  core_trim = String.prototype.trim,

  // Define a local copy of jQuery
  jQuery = function( selector, context ) {
    // The jQuery object is actually just the init constructor 'enhanced'
    return new jQuery.fn.init( selector, context, rootjQuery );
  },

  // A central reference to the root jQuery(document)
  rootjQuery,

  // The deferred used on DOM ready
  readyList,

  // Used for detecting and trimming whitespace
  core_rnotwhite = /\S/,
  core_rspace = /\s+/,

  // IE doesn't match non-breaking spaces with \s
  rtrim = core_rnotwhite.test("\xA0") ? (/^[\s\xA0]+|[\s\xA0]+$/g) : /^\s+|\s+$/g,

  // A simple way to check for HTML strings
  // Prioritize #id over <tag> to avoid XSS via location.hash (#9521)
  rquickExpr = /^(?:[^#<]*(<[\w\W]+>)[^>]*$|#([\w\-]*)$)/,

  // Match a standalone tag
  rsingleTag = /^<(\w+)\s*\/?>(?:<\/\1>)?$/,

  // JSON RegExp
  rvalidchars = /^[\],:{}\s]*$/,
  rvalidbraces = /(?:^|:|,)(?:\s*\[)+/g,
  rvalidescape = /\\(?:["\\\/bfnrt]|u[\da-fA-F]{4})/g,
  rvalidtokens = /"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,

  // Matches dashed string for camelizing
  rmsPrefix = /^-ms-/,
  rdashAlpha = /-([\da-z])/gi,

  // Used by jQuery.camelCase as callback to replace()
  fcamelCase = function( all, letter ) {
    return ( letter + "" ).toUpperCase();
  },

  // The ready event handler and self cleanup method
  DOMContentLoaded = function() {
    if ( document.addEventListener ) {
      document.removeEventListener( "DOMContentLoaded", DOMContentLoaded, false );
    } else {
      // we're here because readyState !== "loading" in oldIE
      // which is good enough for us to call the dom ready!
      document.detachEvent( "onreadystatechange", DOMContentLoaded );
    }
    jQuery.ready();
  },

  // [[Class]] -> type pairs
  class2type = {};

jQuery.fn = jQuery.prototype = {
  constructor: jQuery,
  init: function( selector, context, rootjQuery ) {
    var match, elem, ret, doc;

    // Handle $(""), $(null), $(undefined), $(false)
    if ( !selector ) {
      return this;
    }

    // Handle $(DOMElement)
    if ( selector.nodeType ) {
      this.context = this[0] = selector;
      this.length = 1;
      return this;
    }

    // Handle HTML strings
    if ( typeof selector === "string" ) {
      if ( selector.charAt(0) === "<" && selector.charAt( selector.length - 1 ) === ">" && selector.length >= 3 ) {
        // Assume that strings that start and end with <> are HTML and skip the regex check
        match = [ null, selector, null ];

      } else {
        match = rquickExpr.exec( selector );
      }

      // Match html or make sure no context is specified for #id
      if ( match && (match[1] || !context) ) {

        // HANDLE: $(html) -> $(array)
        if ( match[1] ) {
          context = context instanceof jQuery ? context[0] : context;
          doc = ( context && context.nodeType ? context.ownerDocument || context : document );

          // scripts is true for back-compat
          selector = jQuery.parseHTML( match[1], doc, true );
          if ( rsingleTag.test( match[1] ) && jQuery.isPlainObject( context ) ) {
            this.attr.call( selector, context, true );
          }

          return jQuery.merge( this, selector );

        // HANDLE: $(#id)
        } else {
          elem = document.getElementById( match[2] );

          // Check parentNode to catch when Blackberry 4.6 returns
          // nodes that are no longer in the document #6963
          if ( elem && elem.parentNode ) {
            // Handle the case where IE and Opera return items
            // by name instead of ID
            if ( elem.id !== match[2] ) {
              return rootjQuery.find( selector );
            }

            // Otherwise, we inject the element directly into the jQuery object
            this.length = 1;
            this[0] = elem;
          }

          this.context = document;
          this.selector = selector;
          return this;
        }

      // HANDLE: $(expr, $(...))
      } else if ( !context || context.jquery ) {
        return ( context || rootjQuery ).find( selector );

      // HANDLE: $(expr, context)
      // (which is just equivalent to: $(context).find(expr)
      } else {
        return this.constructor( context ).find( selector );
      }

    // HANDLE: $(function)
    // Shortcut for document ready
    } else if ( jQuery.isFunction( selector ) ) {
      return rootjQuery.ready( selector );
    }

    if ( selector.selector !== undefined ) {
      this.selector = selector.selector;
      this.context = selector.context;
    }

    return jQuery.makeArray( selector, this );
  },

  // Start with an empty selector
  selector: "",

  // The current version of jQuery being used
  jquery: "1.8.0pre 9a40b1848a77e106d8ff96d40ca01d9b325f63bc",

  // The default length of a jQuery object is 0
  length: 0,

  // The number of elements contained in the matched element set
  size: function() {
    return this.length;
  },

  toArray: function() {
    return core_slice.call( this );
  },

  // Get the Nth element in the matched element set OR
  // Get the whole matched element set as a clean array
  get: function( num ) {
    return num == null ?

      // Return a 'clean' array
      this.toArray() :

      // Return just the object
      ( num < 0 ? this[ this.length + num ] : this[ num ] );
  },

  // Take an array of elements and push it onto the stack
  // (returning the new matched element set)
  pushStack: function( elems, name, selector ) {
    // Build a new jQuery matched element set
    var ret = this.constructor();

    if ( jQuery.isArray( elems ) ) {
      core_push.apply( ret, elems );

    } else {
      jQuery.merge( ret, elems );
    }

    // Add the old object onto the stack (as a reference)
    ret.prevObject = this;

    ret.context = this.context;

    if ( name === "find" ) {
      ret.selector = this.selector + ( this.selector ? " " : "" ) + selector;
    } else if ( name ) {
      ret.selector = this.selector + "." + name + "(" + selector + ")";
    }

    // Return the newly-formed element set
    return ret;
  },

  // Execute a callback for every element in the matched set.
  // (You can seed the arguments with an array of args, but this is
  // only used internally.)
  each: function( callback, args ) {
    return jQuery.each( this, callback, args );
  },

  ready: function( fn ) {
    // Add the callback
    jQuery.ready.promise().done( fn );

    return this;
  },

  eq: function( i ) {
    i = +i;
    return i === -1 ?
      this.slice( i ) :
      this.slice( i, i + 1 );
  },

  first: function() {
    return this.eq( 0 );
  },

  last: function() {
    return this.eq( -1 );
  },

  slice: function() {
    return this.pushStack( core_slice.apply( this, arguments ),
      "slice", core_slice.call(arguments).join(",") );
  },

  map: function( callback ) {
    return this.pushStack( jQuery.map(this, function( elem, i ) {
      return callback.call( elem, i, elem );
    }));
  },

  end: function() {
    return this.prevObject || this.constructor(null);
  },

  // For internal use only.
  // Behaves like an Array's method, not like a jQuery method.
  push: core_push,
  sort: [].sort,
  splice: [].splice
};

// Give the init function the jQuery prototype for later instantiation
jQuery.fn.init.prototype = jQuery.fn;

jQuery.extend = jQuery.fn.extend = function() {
  var options, name, src, copy, copyIsArray, clone,
    target = arguments[0] || {},
    i = 1,
    length = arguments.length,
    deep = false;

  // Handle a deep copy situation
  if ( typeof target === "boolean" ) {
    deep = target;
    target = arguments[1] || {};
    // skip the boolean and the target
    i = 2;
  }

  // Handle case when target is a string or something (possible in deep copy)
  if ( typeof target !== "object" && !jQuery.isFunction(target) ) {
    target = {};
  }

  // extend jQuery itself if only one argument is passed
  if ( length === i ) {
    target = this;
    --i;
  }

  for ( ; i < length; i++ ) {
    // Only deal with non-null/undefined values
    if ( (options = arguments[ i ]) != null ) {
      // Extend the base object
      for ( name in options ) {
        src = target[ name ];
        copy = options[ name ];

        // Prevent never-ending loop
        if ( target === copy ) {
          continue;
        }

        // Recurse if we're merging plain objects or arrays
        if ( deep && copy && ( jQuery.isPlainObject(copy) || (copyIsArray = jQuery.isArray(copy)) ) ) {
          if ( copyIsArray ) {
            copyIsArray = false;
            clone = src && jQuery.isArray(src) ? src : [];

          } else {
            clone = src && jQuery.isPlainObject(src) ? src : {};
          }

          // Never move original objects, clone them
          target[ name ] = jQuery.extend( deep, clone, copy );

        // Don't bring in undefined values
        } else if ( copy !== undefined ) {
          target[ name ] = copy;
        }
      }
    }
  }

  // Return the modified object
  return target;
};

jQuery.extend({
  noConflict: function( deep ) {
    if ( window.$ === jQuery ) {
      window.$ = _$;
    }

    if ( deep && window.jQuery === jQuery ) {
      window.jQuery = _jQuery;
    }

    return jQuery;
  },

  // Is the DOM ready to be used? Set to true once it occurs.
  isReady: false,

  // A counter to track how many items to wait for before
  // the ready event fires. See #6781
  readyWait: 1,

  // Hold (or release) the ready event
  holdReady: function( hold ) {
    if ( hold ) {
      jQuery.readyWait++;
    } else {
      jQuery.ready( true );
    }
  },

  // Handle when the DOM is ready
  ready: function( wait ) {

    // Abort if there are pending holds or we're already ready
    if ( wait === true ? --jQuery.readyWait : jQuery.isReady ) {
      return;
    }

    // Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).
    if ( !document.body ) {
      return setTimeout( jQuery.ready, 1 );
    }

    // Remember that the DOM is ready
    jQuery.isReady = true;

    // If a normal DOM Ready event fired, decrement, and wait if need be
    if ( wait !== true && --jQuery.readyWait > 0 ) {
      return;
    }

    // If there are functions bound, to execute
    readyList.resolveWith( document, [ jQuery ] );

    // Trigger any bound ready events
    if ( jQuery.fn.trigger ) {
      jQuery( document ).trigger("ready").off("ready");
    }
  },

  // See test/unit/core.js for details concerning isFunction.
  // Since version 1.3, DOM methods and functions like alert
  // aren't supported. They return false on IE (#2968).
  isFunction: function( obj ) {
    return jQuery.type(obj) === "function";
  },

  isArray: Array.isArray || function( obj ) {
    return jQuery.type(obj) === "array";
  },

  isWindow: function( obj ) {
    return obj != null && obj == obj.window;
  },

  isNumeric: function( obj ) {
    return !isNaN( parseFloat(obj) ) && isFinite( obj );
  },

  type: function( obj ) {
    return obj == null ?
      String( obj ) :
      class2type[ core_toString.call(obj) ] || "object";
  },

  isPlainObject: function( obj ) {
    // Must be an Object.
    // Because of IE, we also have to check the presence of the constructor property.
    // Make sure that DOM nodes and window objects don't pass through, as well
    if ( !obj || jQuery.type(obj) !== "object" || obj.nodeType || jQuery.isWindow( obj ) ) {
      return false;
    }

    try {
      // Not own constructor property must be Object
      if ( obj.constructor &&
        !core_hasOwn.call(obj, "constructor") &&
        !core_hasOwn.call(obj.constructor.prototype, "isPrototypeOf") ) {
        return false;
      }
    } catch ( e ) {
      // IE8,9 Will throw exceptions on certain host objects #9897
      return false;
    }

    // Own properties are enumerated firstly, so to speed up,
    // if last one is own, then all properties are own.

    var key;
    for ( key in obj ) {}

    return key === undefined || core_hasOwn.call( obj, key );
  },

  isEmptyObject: function( obj ) {
    for ( var name in obj ) {
      return false;
    }
    return true;
  },

  error: function( msg ) {
    throw new Error( msg );
  },

  // data: string of html
  // context (optional): If specified, the fragment will be created in this context, defaults to document
  // scripts (optional): If true, will include scripts passed in the html string
  parseHTML: function( data, context, scripts ) {
    var parsed;
    if ( !data || typeof data !== "string" ) {
      return null;
    }
    if ( typeof context === "boolean" ) {
      scripts = context;
      context = 0;
    }
    context = context || document;

    // Single tag
    if ( (parsed = rsingleTag.exec( data )) ) {
      return [ context.createElement( parsed[1] ) ];
    }

    parsed = jQuery.buildFragment( [ data ], context, scripts ? null : [] );
    return jQuery.merge( [],
      (parsed.cacheable ? jQuery.clone( parsed.fragment ) : parsed.fragment).childNodes );
  },

  parseJSON: function( data ) {
    if ( !data || typeof data !== "string") {
      return null;
    }

    // Make sure leading/trailing whitespace is removed (IE can't handle it)
    data = jQuery.trim( data );

    // Attempt to parse using the native JSON parser first
    if ( window.JSON && window.JSON.parse ) {
      return window.JSON.parse( data );
    }

    // Make sure the incoming data is actual JSON
    // Logic borrowed from http://json.org/json2.js
    if ( rvalidchars.test( data.replace( rvalidescape, "@" )
      .replace( rvalidtokens, "]" )
      .replace( rvalidbraces, "")) ) {

      return ( new Function( "return " + data ) )();

    }
    jQuery.error( "Invalid JSON: " + data );
  },

  // Cross-browser xml parsing
  parseXML: function( data ) {
    var xml, tmp;
    if ( !data || typeof data !== "string" ) {
      return null;
    }
    try {
      if ( window.DOMParser ) { // Standard
        tmp = new DOMParser();
        xml = tmp.parseFromString( data , "text/xml" );
      } else { // IE
        xml = new ActiveXObject( "Microsoft.XMLDOM" );
        xml.async = "false";
        xml.loadXML( data );
      }
    } catch( e ) {
      xml = undefined;
    }
    if ( !xml || !xml.documentElement || xml.getElementsByTagName( "parsererror" ).length ) {
      jQuery.error( "Invalid XML: " + data );
    }
    return xml;
  },

  noop: function() {},

  // Evaluates a script in a global context
  // Workarounds based on findings by Jim Driscoll
  // http://weblogs.java.net/blog/driscoll/archive/2009/09/08/eval-javascript-global-context
  globalEval: function( data ) {
    if ( data && core_rnotwhite.test( data ) ) {
      // We use execScript on Internet Explorer
      // We use an anonymous function so that context is window
      // rather than jQuery in Firefox
      ( window.execScript || function( data ) {
        window[ "eval" ].call( window, data );
      } )( data );
    }
  },

  // Convert dashed to camelCase; used by the css and data modules
  // Microsoft forgot to hump their vendor prefix (#9572)
  camelCase: function( string ) {
    return string.replace( rmsPrefix, "ms-" ).replace( rdashAlpha, fcamelCase );
  },

  nodeName: function( elem, name ) {
    return elem.nodeName && elem.nodeName.toUpperCase() === name.toUpperCase();
  },

  // args is for internal usage only
  each: function( object, callback, args ) {
    var name, i = 0,
      length = object.length,
      isObj = length === undefined || jQuery.isFunction( object );

    if ( args ) {
      if ( isObj ) {
        for ( name in object ) {
          if ( callback.apply( object[ name ], args ) === false ) {
            break;
          }
        }
      } else {
        for ( ; i < length; ) {
          if ( callback.apply( object[ i++ ], args ) === false ) {
            break;
          }
        }
      }

    // A special, fast, case for the most common use of each
    } else {
      if ( isObj ) {
        for ( name in object ) {
          if ( callback.call( object[ name ], name, object[ name ] ) === false ) {
            break;
          }
        }
      } else {
        for ( ; i < length; ) {
          if ( callback.call( object[ i ], i, object[ i++ ] ) === false ) {
            break;
          }
        }
      }
    }

    return object;
  },

  // Use native String.trim function wherever possible
  trim: core_trim ?
    function( text ) {
      return text == null ?
        "" :
        core_trim.call( text );
    } :

    // Otherwise use our own trimming functionality
    function( text ) {
      return text == null ?
        "" :
        text.toString().replace( rtrim, "" );
    },

  // results is for internal usage only
  makeArray: function( array, results ) {
    var ret = results || [];

    if ( array != null ) {
      // The window, strings (and functions) also have 'length'
      // Tweaked logic slightly to handle Blackberry 4.7 RegExp issues #6930
      var type = jQuery.type( array );

      if ( array.length == null || type === "string" || type === "function" || type === "regexp" || jQuery.isWindow( array ) ) {
        core_push.call( ret, array );
      } else {
        jQuery.merge( ret, array );
      }
    }

    return ret;
  },

  inArray: function( elem, array, i ) {
    var len;

    if ( array ) {
      if ( core_indexOf ) {
        return core_indexOf.call( array, elem, i );
      }

      len = array.length;
      i = i ? i < 0 ? Math.max( 0, len + i ) : i : 0;

      for ( ; i < len; i++ ) {
        // Skip accessing in sparse arrays
        if ( i in array && array[ i ] === elem ) {
          return i;
        }
      }
    }

    return -1;
  },

  merge: function( first, second ) {
    var i = first.length,
      j = 0;

    if ( typeof second.length === "number" ) {
      for ( var l = second.length; j < l; j++ ) {
        first[ i++ ] = second[ j ];
      }

    } else {
      while ( second[j] !== undefined ) {
        first[ i++ ] = second[ j++ ];
      }
    }

    first.length = i;

    return first;
  },

  grep: function( elems, callback, inv ) {
    var ret = [], retVal;
    inv = !!inv;

    // Go through the array, only saving the items
    // that pass the validator function
    for ( var i = 0, length = elems.length; i < length; i++ ) {
      retVal = !!callback( elems[ i ], i );
      if ( inv !== retVal ) {
        ret.push( elems[ i ] );
      }
    }

    return ret;
  },

  // arg is for internal usage only
  map: function( elems, callback, arg ) {
    var value, key, ret = [],
      i = 0,
      length = elems.length,
      // jquery objects are treated as arrays
      isArray = elems instanceof jQuery || length !== undefined && typeof length === "number" && ( ( length > 0 && elems[ 0 ] && elems[ length -1 ] ) || length === 0 || jQuery.isArray( elems ) ) ;

    // Go through the array, translating each of the items to their
    if ( isArray ) {
      for ( ; i < length; i++ ) {
        value = callback( elems[ i ], i, arg );

        if ( value != null ) {
          ret[ ret.length ] = value;
        }
      }

    // Go through every key on the object,
    } else {
      for ( key in elems ) {
        value = callback( elems[ key ], key, arg );

        if ( value != null ) {
          ret[ ret.length ] = value;
        }
      }
    }

    // Flatten any nested arrays
    return ret.concat.apply( [], ret );
  },

  // A global GUID counter for objects
  guid: 1,

  // Bind a function to a context, optionally partially applying any
  // arguments.
  proxy: function( fn, context ) {
    if ( typeof context === "string" ) {
      var tmp = fn[ context ];
      context = fn;
      fn = tmp;
    }

    // Quick check to determine if target is callable, in the spec
    // this throws a TypeError, but we will just return undefined.
    if ( !jQuery.isFunction( fn ) ) {
      return undefined;
    }

    // Simulated bind
    var args = core_slice.call( arguments, 2 ),
      proxy = function() {
        return fn.apply( context, args.concat( core_slice.call( arguments ) ) );
      };

    // Set the guid of unique handler to the same of original handler, so it can be removed
    proxy.guid = fn.guid = fn.guid || proxy.guid || jQuery.guid++;

    return proxy;
  },

  // Multifunctional method to get and set values of a collection
  // The value/s can optionally be executed if it's a function
  access: function( elems, fn, key, value, chainable, emptyGet, pass ) {
    var exec,
      bulk = key == null,
      i = 0,
      length = elems.length;

    // Sets many values
    if ( key && typeof key === "object" ) {
      for ( i in key ) {
        jQuery.access( elems, fn, i, key[i], 1, emptyGet, value );
      }
      chainable = 1;

    // Sets one value
    } else if ( value !== undefined ) {
      // Optionally, function values get executed if exec is true
      exec = pass === undefined && jQuery.isFunction( value );

      if ( bulk ) {
        // Bulk operations only iterate when executing function values
        if ( exec ) {
          exec = fn;
          fn = function( elem, key, value ) {
            return exec.call( jQuery( elem ), value );
          };

        // Otherwise they run against the entire set
        } else {
          fn.call( elems, value );
          fn = null;
        }
      }

      if ( fn ) {
        for (; i < length; i++ ) {
          fn( elems[i], key, exec ? value.call( elems[i], i, fn( elems[i], key ) ) : value, pass );
        }
      }

      chainable = 1;
    }

    return chainable ?
      elems :

      // Gets
      bulk ?
        fn.call( elems ) :
        length ? fn( elems[0], key ) : emptyGet;
  },

  now: function() {
    return ( new Date() ).getTime();
  }
});