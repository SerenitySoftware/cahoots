// This file will handle packaged requests for database insert requests
package com.launch.gateway {
    import mx.controls.Alert;
    
    public class DBInsert {
        
        // This is the gateway Request function on the parentApplication
        private var gatewayRequest : Function;
        
        
        public var table : String = new String();           /** "pages" **/
        // "id" will hold the field name of the PK for the table in question.  If this is set, it will return the table name.
        public var id : String = new String();              /** "page_id" **/
        
        public var fields : Array = new Array();            /** ["title","name","date"] **/
        public var values : Array = new Array();            /** ["My title","My name","My Date"] **/

        // Because these data transmissions are asynchronous, we must specify a "results" function to pass the returned array of results into.
        public var responseFunction : Function = null;
        
        
        // The gateway request function MUST be passed in.
        public function DBInsert(gatewayRequestFunction:Function) : void {
            this.gatewayRequest = gatewayRequestFunction;
        }
        
        
        // This will be called to execute the select statement
        public function queryDB() : void {
            
            // This will be the array of parameters for our database request;
            var arrParams : Array = new Array();
            
            // We have to make sure a table is set and if not, alert the user that they didn't set a table
            if ( this.table.length > 0 ) arrParams[0] = this.table;
            else {
                Alert.show("You must specify a table to select data from.");
                this.clearQuery();
                return;
            }
            
            // Making sure that there is data specified
            if ( this.fields.length > 0 && this.fields.length == this.values.length ) arrParams[1] = new Array(this.fields, this.values);
            else {
                Alert.show("You must specify fields and values to insert and the number of fields and values must be equal.");
                this.clearQuery();
                return;
            }
            
            // table PK's field name.
            if ( this.id.length > 0 ) arrParams[2] = this.id;
            
            
            // Sending off the database select request.
            this.gatewayRequest("dbInsert", arrParams, this.responseFunction);
            
            // Clearing the query so the object can be instantly re-used
            this.clearQuery();
            
        }
        
        
        // This function clears the query so the object can be re-used if someone wants to.
        // Called every time a query is sent or can be called anytime someone wants.
        public function clearQuery() : void {
            
            this.table = new String();
            this.id = new String();
            
            this.fields = new Array();
            this.values = new Array();
            
            this.responseFunction = null;
            
        }
        
        
    } 
    
}