$LOAD_PATH.unshift(File.dirname(__FILE__))
#
# Ruby/DBI
#
# Copyright (c) 2001, 2002, 2003 Michael Neumann <mneumann@ntecs.de>
# 
# All rights reserved.
#

require "find"
require "dbi/row"
require "dbi/utils"
require "dbi/sql"
require "dbi/columninfo"
require "date"

module DBI
   VERSION = "0.1.1"
   
   module DBD
      DIR         = "DBD"
      API_VERSION = "0.3"
   end
   
   #  Constants
   
   # Constants for fetch_scroll
   #
   SQL_FETCH_NEXT     = 1
   SQL_FETCH_PRIOR    = 2
   SQL_FETCH_FIRST    = 3
   SQL_FETCH_LAST     = 4
   SQL_FETCH_ABSOLUTE = 5
   SQL_FETCH_RELATIVE = 6
   
   # SQL type constants
   # 
   SQL_CHAR       = 1
   SQL_NUMERIC    = 2
   SQL_DECIMAL    = 3
   SQL_TIME       = 10 # 92 
   SQL_TIMESTAMP  = 11 # 93 
   SQL_VARCHAR    = 12
   
   SQL_LONGVARCHAR   = -1
   SQL_BINARY        = -2
   SQL_VARBINARY     = -3
   SQL_LONGVARBINARY = -4
   SQL_BIGINT        = -5
   SQL_TINYINT       = -6
   SQL_BIT           = -7
   
   SQL_BLOB = -10   # TODO
   SQL_CLOB = -11   # TODO
   SQL_OTHER = 100
   
   SQL_TYPE_NAMES = {
      SQL_BIT               => 'BIT',
      SQL_TINYINT           => 'TINYINT',
      SQL_SMALLINT          => 'SMALLINT',
      SQL_INTEGER           => 'INTEGER',
      SQL_BIGINT            => 'BIGINT',
      SQL_FLOAT             => 'FLOAT',
      SQL_TIMESTAMP         => 'TIMESTAMP',
      SQL_BINARY            => 'BINARY',
      SQL_VARBINARY         => 'VARBINARY',
      SQL_LONGVARBINARY     => 'LONG VARBINARY',
      SQL_BLOB              => 'BLOB',
      SQL_CLOB              => 'CLOB',
      SQL_OTHER             => nil
   }
   
   #  Exceptions (borrowed by Python API 2.0)
   
   # Base class of all other error exceptions.  Use this to catch all DBI
   # errors.
   class Error < RuntimeError
   end
   
   # For important warnings like data truncation, etc.
   class Warning < RuntimeError
   end
   
   # Exception for errors related to the DBI interface rather than the
   # database itself.
   class InterfaceError < Error
   end
   
   # Exception raised if the DBD driver has not specified a mandatory method.
   class NotImplementedError < InterfaceError
   end
   
   # Exception for errors related to the database.
   class DatabaseError < Error
      attr_reader :err, :errstr, :state
      
      def initialize(errstr="", err=nil, state=nil)
         super(errstr)
         @err, @errstr, @state = err, errstr, state
      end
   end
   
   # Exception for errors due to problems with the processed 
   # data such as division by zero, numeric value out of range, etc.
   class DataError < DatabaseError
   end
   
   # Exception for errors related to the database's operation which are not
   # necessarily under the control of the programmer.  This includes such
   # things as unexpected disconnect, datasource name not found, transaction
   # could not be processed, a memory allocation error occured during
   # processing, etc.
   class OperationalError < DatabaseError
   end
   
   # Exception raised when the relational integrity of the database
   # is affected, e.g. a foreign key check fails.
   class IntegrityError < DatabaseError
   end
   
   # Exception raised when the database encounters an internal error, 
   # e.g. the cursor is not valid anymore, the transaction is out of sync.
   class InternalError < DatabaseError
   end
   
   # Exception raised for programming errors, e.g. table not found
   # or already exists, syntax error in SQL statement, wrong number
   # of parameters specified, etc.
   class ProgrammingError < DatabaseError
   end
   
   # Exception raised if e.g. commit() is called for a database which do not
   # support transactions.
   class NotSupportedError < DatabaseError
   end
   
   #  Datatypes
   
   # TODO: do we need Binary?
   # perhaps easier to call #bind_param(1, binary_string, 'type' => SQL_BLOB)
   class Binary
      attr_accessor :data
      def initialize(data)
         @data = data
      end
      
      def to_s
         @data
      end
   end
   
   #  Module functions (of DBI)
   DEFAULT_TRACE_MODE = 2
   DEFAULT_TRACE_OUTPUT = STDERR
   
   # TODO: Is using class variables within a module such a wise idea? - Dan B.
   @@driver_map   = Hash.new 
   @@trace_mode   = DEFAULT_TRACE_MODE
   @@trace_output = DEFAULT_TRACE_OUTPUT
   
   class << self
      
      # Establish a database connection.  This is mostly a facade for the
      # DBD's connect method.
      def connect(driver_url, user=nil, auth=nil, params=nil, &p)
         dr, db_args = _get_full_driver(driver_url)
         dh = dr[0] # driver-handle
         dh.connect(db_args, user, auth, params, &p)
      end
      
      # Load a DBD and returns the DriverHandle object
      def get_driver(driver_url)
         _get_full_driver(driver_url)[0][0]  # return DriverHandle
      end
      
      # Extracts the db_args from driver_url and returns the correspondeing
      # entry of the @@driver_map.
      def _get_full_driver(driver_url)
         db_driver, db_args = parse_url(driver_url)
         db_driver = load_driver(db_driver)
         dr = @@driver_map[db_driver]
         [dr, db_args]
      end
      
      def trace(mode=nil, output=nil)
         @@trace_mode   = mode   || @@trace_mode   || DBI::DEFAULT_TRACE_MODE
         @@trace_output = output || @@trace_output || DBI::DEFAULT_TRACE_OUTPUT
      end
      
      # Returns a list of the currently available drivers on your system in
      # 'dbi:driver:' format.
      def available_drivers
         drivers = []
         path = File.dirname(File.dirname(__FILE__)) + "/" + DBD::DIR
         Find.find(path){ |f|
            if File.file?(f)
               driver = File.basename(f, ".rb")
               drivers.push("dbi:#{driver}:")
            end
         }
         drivers
      end
      
      def data_sources(driver)
         db_driver, = parse_url(driver)
         db_driver = load_driver(db_driver)
         dh = @@driver_map[db_driver][0]
         dh.data_sources
      end
      
      def disconnect_all( driver = nil )
         if driver.nil?
            @@driver_map.each {|k,v| v[0].disconnect_all}
         else
            db_driver, = parse_url(driver)
            @@driver_map[db_driver][0].disconnect_all
         end
      end
      
      
      private
      
      ##
      # extended by John Gorman <jgorman@webbysoft.com> for
      # case insensitive DBD names
      # 
      def load_driver(driver_name)
         if @@driver_map[driver_name].nil?
            
            dc = driver_name.downcase
            
            # caseless look for drivers already loaded
            found = @@driver_map.keys.find {|key| key.downcase == dc}
            return found if found
            
            if $SAFE >= 1
               # case-sensitive in safe mode
               require "#{DBD::DIR}/#{driver_name}/#{driver_name}"
            else
               # try a quick load and then a caseless scan
               begin
                  require "#{DBD::DIR}/#{driver_name}/#{driver_name}"
               rescue LoadError
                  $LOAD_PATH.each do |dir|
                     path = "#{dir}/#{DBD::DIR}"
                     next unless FileTest.directory?(path)
                     found = Dir.entries(path).find {|e| e.downcase == dc}
                     next unless found

                     require "#{DBD::DIR}/#{found}/#{found}"
                     break
                  end
               end
            end
            
            found ||= driver_name
            
            # On a filesystem that is not case-sensitive (e.g., HFS+ on Mac OS X),
            # the initial require attempt that loads the driver may succeed even
            # though the lettercase of driver_name doesn't match the actual
            # filename. If that happens, const_get will fail and it become
            # necessary to look though the list of constants and look for a
            # caseless match.  The result of this match provides the constant
            # with the proper lettercase -- which can be used to generate the
            # driver handle.
            
            dr = nil
            begin
               dr = DBI::DBD.const_get(found.intern)
            rescue NameError
               # caseless look for constants to find actual constant
               found = found.downcase
               found = DBI::DBD.constants.find { |e| e.downcase == found }
               dr = DBI::DBD.const_get(found.intern) unless found.nil?
            end
            
            # If dr is nil at this point, it means the underlying driver
            # failed to load.  This usually means it's not installed, but
            # can fail for other reasons.
            if dr.nil?
               err = "Unable to load driver '#{driver_name}'"
               raise DBI::InterfaceError, err
            end
            
            dbd_dr = dr::Driver.new
            drh = DBI::DriverHandle.new(dbd_dr)
            drh.trace(@@trace_mode, @@trace_output)
            @@driver_map[found] = [drh, dbd_dr]
            return found
         else
            return driver_name
         end
      rescue LoadError, NameError
         if $SAFE >= 1
            raise InterfaceError, "Could not load driver (#{$!.message}). Note that in SAFE mode >= 1, driver URLs have to be case sensitive!"
         else
            raise InterfaceError, "Could not load driver (#{$!.message})"
         end
      end
      
      # Splits a DBI URL into two components - the database driver name
      # and the datasource (along with any options, if any) and returns
      # a two element array, e.g. 'dbi:foo:bar' would return ['foo','bar'].
      #
      # A regular expression is used instead of a simple split to validate
      # the proper format for the URL.  If it isn't correct, an Interface
      # error is raised.
      def parse_url(driver_url)
         if driver_url =~ /^(DBI|dbi):([^:]+)(:(.*))?$/ 
            [$2, $4]
         else
            raise InterfaceError, "Invalid Data Source Name"
         end
      end
      
   end # self
   
   
   
   #----------------------------------------------------
   #  Dispatch classes
   #----------------------------------------------------
   
   
   ##
   # Dispatch classes (Handle, DriverHandle, DatabaseHandle and StatementHandle)
   #
   
   class Handle
      attr_reader :trace_mode, :trace_output
      attr_reader :handle 
      
      def initialize(handle)
         @handle = handle
         @trace_mode = @trace_output = nil
      end
      
      def trace(mode=nil, output=nil)
         @trace_mode   = mode   || @trace_mode   || DBI::DEFAULT_TRACE_MODE
         @trace_output = output || @trace_output || DBI::DEFAULT_TRACE_OUTPUT
      end
      
      
      ##
      # call a driver specific function
      #
      def func(function, *values)
         if @handle.respond_to?("__" + function.to_s) then
            @handle.send("__" + function.to_s, *values)  
         else
            raise InterfaceError, "Driver specific function <#{function}> not available."
         end
      rescue ArgumentError
         raise InterfaceError, "Wrong # of arguments for driver specific function"
      end
      
      # error functions?
   end
   
   class DriverHandle < Handle
      
      def connect(db_args, user, auth, params)
         
         user = @handle.default_user[0] if user.nil?
         auth = @handle.default_user[1] if auth.nil?
         
         # TODO: what if only one of them is nil?
         #if user.nil? and auth.nil? then
         #  user, auth = @handle.default_user
         #end
         
         params ||= {}
         new_params = @handle.default_attributes
         params.each {|k,v| new_params[k] = v} 
         
         
         db = @handle.connect(db_args, user, auth, new_params)
         dbh = DatabaseHandle.new(db)
         dbh.trace(@trace_mode, @trace_output)
         
         if block_given?
            begin
               yield dbh
            ensure  
               dbh.disconnect if dbh.connected?
            end  
         else
            return dbh
         end
      end
      
      def data_sources
         @handle.data_sources
      end
      
      def disconnect_all
         @handle.disconnect_all
      end
   end
   
   class DatabaseHandle < Handle
      
      include DBI::Utils::ConvParam
      
      def connected?
         not @handle.nil?
      end
      
      def disconnect
         raise InterfaceError, "Database connection was already closed!" if @handle.nil?
         @handle.disconnect
         @handle = nil
      end
      
      def prepare(stmt)
         raise InterfaceError, "Database connection was already closed!" if @handle.nil?
         sth = StatementHandle.new(@handle.prepare(stmt), false)
         sth.trace(@trace_mode, @trace_output)
         
         if block_given?
            begin
               yield sth
            ensure
               sth.finish unless sth.finished?
            end
         else
            return sth
         end 
      end
      
      def execute(stmt, *bindvars)
         raise InterfaceError, "Database connection was already closed!" if @handle.nil?
         sth = StatementHandle.new(@handle.execute(stmt, *conv_param(*bindvars)), true, false)
         sth.trace(@trace_mode, @trace_output)
         
         if block_given?
            begin
               yield sth
            ensure
               sth.finish unless sth.finished?
            end
         else
            return sth
         end 
      end
      
      def do(stmt, *bindvars)
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.do(stmt, *conv_param(*bindvars))
         end
         
         def select_one(stmt, *bindvars)
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            row = nil
            execute(stmt, *bindvars) do |sth|
               row = sth.fetch 
            end
            row
         end
         
         def select_all(stmt, *bindvars, &p)
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            rows = nil
            execute(stmt, *bindvars) do |sth|
               if block_given?
                  sth.each(&p)
               else
                  rows = sth.fetch_all 
               end
            end
            return rows
         end
         
         def tables
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.tables
         end
         
         def columns( table )
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.columns( table ).collect {|col| ColumnInfo.new(col) }
         end
         
         def ping
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.ping
         end
         
         def quote(value)
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.quote(value)
         end
         
         def commit
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.commit
         end
         
         def rollback
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle.rollback
         end
         
         def transaction
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            raise InterfaceError, "No block given" unless block_given?
            
            commit
            begin
               yield self
               commit
            rescue Exception
               rollback
               raise
            end
         end
         
         
         def [] (attr)
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle[attr]
         end
         
         def []= (attr, val)
            raise InterfaceError, "Database connection was already closed!" if @handle.nil?
            @handle[attr] = val
         end
         
      end
