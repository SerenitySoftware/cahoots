
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