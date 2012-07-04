# --------------------------------------------------------------------------
# JFilter.rb -- sample ruby plugin script
# Copyright (C) 2003 Jamis Buck (jgb3@email.byu.edu)
# --------------------------------------------------------------------------

include XChatRuby

class JFilter < XChatRubyPlugin
  
  def initialize
    @jfilter_name = format( "![bc(ltblue)]JFilter![bc]" )

    @config_file = get_info( "xchatdir" ) + "/jfilter.dat"
    @filter_window = "JFilter Window"

    @filters = []
    @active = false

    load_filters

    hook_command( "Filter", XCHAT_PRI_NORM, method( :filter_handler ),
                  "Usage: /filter cmd opts, see /filter help for more info" )

    hook_server( "PRIVMSG", XCHAT_PRI_NORM, method( :filter_text_handler ) )

    jfilter_hook_print( "CTCP Generic to Channel" )
    jfilter_hook_print( "Join" )
    jfilter_hook_print( "Part" )
    jfilter_hook_print( "Part with Reason" )
    jfilter_hook_print( "Quit" )

    @active = true
    puts "#{@jfilter_name} loaded (\"/filter help\" for more info)."
    show_status
  end

  def jfilter_hook_print( name )
    hook_print( name, XCHAT_PRI_NORM, method( :filter_print_handler ), name )
  end

  def load_filters
    if File.exist? @config_file
      File.open( @config_file, "r" ) do |file|
        file.each do |line|
          @filters.push Regexp.new( line.chomp, true )
        end
      end
    end
  end

  def add_filter( filter )
    @filters.push Regexp.new( filter, true )
    File.open( @config_file, "a" ) do |file|
      file.puts filter
    end
  end

  def show_status
    puts_fmt "Filtering is currently ![c(red)]" + ( @active ? "on" : "off" ) + "![c]."
  end

  def activate_filter( words, words_eol, data )
    if @active
      puts "#{@jfilter_name} is already active."
    else
      @active = true
      puts "#{@jfilter_name} has been actived."
    end

    return XCHAT_EAT_ALL
  end

  def deactivate_filter( words, words_eol, data )
    if !@active
      puts "#{@jfilter_name} is not currently active."
    else
      @active = false
      puts "#{@jfilter_name} has been deactivated."
    end

    return XCHAT_EAT_ALL
  end

  def filter_help( words, words_eol, data )
puts <<EOT

#{@jfilter_name} -- a text filtering plugin for XChat2
Available commands:

  /filter on               -- activates the filter
          off              -- deactivates the filter
          add              -- prompts you for a pattern to add to the filter
          addf   <pattern> -- adds the given pattern to the filter
          status           -- whether the filter is active or not
          list             -- lists the active patterns being filtered
          help             -- shows this text
EOT

    return XCHAT_EAT_ALL
  end

  def show_filter_status( words, words_eol, data )
    show_status
    return XCHAT_EAT_ALL
  end

  def enumerate_available_patterns( words, words_eol, data )
    puts

    if @filters.length < 1
      puts "There are no patterns being filtered."
    else
      puts "Patterns being filtered:"
      @filters.each do |filter|
        puts "  >> " + filter.source
      end
    end

    puts

    return XCHAT_EAT_ALL
  end

  def filter_handler( words, words_eol, data )
    if !words[1]
      puts "You must specify a filter action ('/filter help' for more info)"
    else
      case words[1].downcase
        when 'on' then
          return activate_filter( words, words_eol, data )
        when 'off' then
          return deactivate_filter( words, words_eol, data )
        when 'help' then
          return filter_help( words, words_eol, data )
        when 'status' then
          return show_filter_status( words, words_eol, data )
        when 'addf' then
          return add_pattern_to_filter( words, words_eol, data )
        when 'add' then
          return prompt_for_pattern_to_add( words, words_eol, data )
        when 'list' then
          return enumerate_available_patterns( words, words_eol, data )
      end
    end

    return XCHAT_EAT_ALL
  end

  def write_to_filter_window( text )
    command( "query \"#{@filter_window}\"" )
    puts text, @filter_window
  end

  FILTER_COLOR_CYCLE = [ "yellow", "red", "blue", "green" ]

  def append_user_chan_msg_to_window( user, chan, msg )
    user = "<none>" if !user
    chan = "<none>" if !chan
    msg = "<none>" if !msg

    @current_color = 0 if !@current_color

    color = FILTER_COLOR_CYCLE[ @current_color ]
    write_to_filter_window( format( "![c(#{color})]#{user}![o|]#{chan} : #{msg}" ) )

    @current_color = ( @current_color + 1 ) % FILTER_COLOR_CYCLE.length
  end

  def filter_text_handler( words, words_eol, data )
    return XCHAT_EAT_NONE if !@active || @filters.length < 1

    # words[0] -> ':' + user that sent the text
    # words[1] -> PRIVMSG
    # words[2] -> channel
    # words[3] -> ':' + text

    text = words_eol[3][1..-1]

    words[0] =~ /:(.*?)!/
    user = $1

    # if the message is directly to me (ie, channel==my nick) don't ignore it
    return XCHAT_EAT_NONE if words[2] == get_info( "nick" )

    @filters.each do |filter|
      if text =~ filter
        append_user_chan_msg_to_window( user, words[2], text )
        return XCHAT_EAT_ALL
      end
    end

    return XCHAT_EAT_NONE
  end

  def add_pattern_to_filter( words, words_eol, data )
    return XCHAT_EAT_ALL if !words_eol[2]

    pattern = words_eol[2].strip
    return XCHAT_EAT_ALL if pattern.length < 1

    add_filter( pattern )
    return XCHAT_EAT_ALL
  end

  def prompt_for_pattern_to_add( words, words_eol, data )
    command( 'getstr " " "filter addf" "Enter a pattern to filter:"' )
    return XCHAT_EAT_ALL
  end

  def filter_print_handler( words, data )
    return XCHAT_EAT_NONE if !@active

    case ( data || "" ).downcase
      when "join" then
        msg  = "join"
        user = words[0]
        chan = words[1]

      when "part", "part with reason" then
        msg = "part"
        msg << " (#{words[3]})" if data.downcase == "part with reason"
        user = words[0]
        chan = words[1]

      when "quit" then
        msg = "quit (#{words[1]})"
        user = words[0]
        chan = nil

      when "ctcp generic to channel" then
        msg = "CTCP " + words[0]
        user = words[1]
        chan = words[2]

      else
        msg = data
        user = nil
        chan = nil
    end

    append_user_chan_msg_to_window( user, chan, msg )

    return XCHAT_EAT_XCHAT
  end
end

# Manipulation of LDAP control data.
#
# $Id: control.rb,v 1.2 2005/02/28 05:02:25 ianmacd Exp $
#
# Copyright (C) 2004 Ian Macdonald <ian@caliban.org>
#

module LDAP
  class Control

    require 'openssl'

    # Take +vals+, produce an Array of values in ASN.1 format and then
    # convert the Array to DER.
    #
    def Control.encode( *vals )
      encoded_vals = []
     
      vals.each do |val|
        encoded_vals <<
          case val
          when Integer
            OpenSSL::ASN1::Integer( val )
          when String
            OpenSSL::ASN1::OctetString.new( val )
          else
            # What other types may exist?
          end
      end
   
      OpenSSL::ASN1::Sequence.new( encoded_vals ).to_der
    end


    # Take an Array of ASN.1 data and return an Array of decoded values.
    #
    def decode
      values = []

      OpenSSL::ASN1::decode( self.value ).value.each do |val|
    values << val.value
      end

      values
    end

  end
end

class AssertFail < Exception
end

def assert(a, b)
    caller = ""
    begin
    raise "no problem"
    rescue RuntimeError => e
    caller = e.backtrace[1]
    end
    if (b === a) then
    val = b.inspect
    val = "#{val}..." if val.size > 40
    print "ok #{caller}: #{val}\n" if $VERBOSE
    else
    val = a.inspect
    val = "#{val}..." if val.size > 200
    raise AssertFail, val
    end
end

def file_delete(*args)
    for file in args
    next unless File.exist?(file)
    File.delete(file)
    end
end

def fold_line(line)
    buf = ""
    while line
    head = line[0..63]
    buf << (head + "\n")
    line = line[64..-1]
    end
    buf
end

def assert_file(filename, pat)
    f = File.read(filename)
    r = [pat.gsub(/\s+/, "")].pack('H*')

    if (r === f) then
    print "ok <#{filename}>\n" if $VERBOSE
    else
    for i in 0...(f.size)
        next if (f[i] == r[i])
        printf "ofs=%08x file=%02x expected=%02x\n", i, f[i], r[i]
        break
    end
    print "#{filename} is longer than expected\n" if f.size > r.size
    h = f.unpack('H*').first
    File.open("#{filename}.hex", "w") { |fp| fp.write(fold_line(h)) }
    print "hex dump of <#{filename}> is saved to <#{filename}.hex>.\n"
    raise AssertFail
    end
end

def testblock(title)
    begin
    yield
    rescue Exception => e
    print "#{title} failed: #{e.message} (#{e.class.to_s})\n"
    print "| ", e.backtrace[1..-1].join("\n| "), "\n"
    return 1
    else
    print "#{title} ok\n"
    return 0
    end
end

def tainttest(msg)
    begin
    yield
    rescue SecurityError => e
    assert(e.message, msg)
    else
    raise SecurityError, "<#{msg}> doesn't come" if $SAFE > 0
    end
end

=begin

fcgi.rb 0.8.5 - fcgi.so compatible pure-ruby FastCGI library

fastcgi.rb Copyright (C) 2001 Eli Green
fcgi.rb    Copyright (C) 2002-2003 MoonWolf <moonwolf@moonwolf.com>
fcgi.rb    Copyright (C) 2004 Minero Aoki

=end
trap('SIGTERM') { exit }
trap('SIGPIPE','IGNORE') rescue nil

begin
  raise LoadError if defined?(FCGI_PURE_RUBY) && FCGI_PURE_RUBY
  require "fcgi.so"
rescue LoadError
  require 'socket'
  require 'stringio'

  class FCGI

    def self::is_cgi?
      begin
        s = Socket.for_fd($stdin.fileno)
        s.getpeername
        false
      rescue Errno::ENOTCONN
        false
      rescue Errno::ENOTSOCK, Errno::EINVAL
        true
      end
    end

    def self::each(&block)
      f = default_connection()
      Server.new(f).each_request(&block)
    ensure
      f.close if f
    end

    def self::each_request(&block)
      f = default_connection()
      Server.new(f).each_request(&block)
    ensure
      f.close if f
    end

    def self::default_connection
      ::Socket.for_fd($stdin.fileno)
    end



    ProtocolVersion = 1

    # Record types
    FCGI_BEGIN_REQUEST = 1
    FCGI_ABORT_REQUEST = 2
    FCGI_END_REQUEST = 3
    FCGI_PARAMS = 4
    FCGI_STDIN = 5
    FCGI_STDOUT = 6
    FCGI_STDERR = 7
    FCGI_DATA = 8
    FCGI_GET_VALUES = 9
    FCGI_GET_VALUES_RESULT = 10
    FCGI_UNKNOWN_TYPE = 11
    FCGI_MAXTYPE = FCGI_UNKNOWN_TYPE

    FCGI_NULL_REQUEST_ID = 0

    # FCGI_BEGIN_REQUSET.role
    FCGI_RESPONDER = 1
    FCGI_AUTHORIZER = 2
    FCGI_FILTER = 3

    # FCGI_BEGIN_REQUEST.flags
    FCGI_KEEP_CONN = 1

    # FCGI_END_REQUEST.protocolStatus
    FCGI_REQUEST_COMPLETE = 0
    FCGI_CANT_MPX_CONN = 1
    FCGI_OVERLOADED = 2
    FCGI_UNKNOWN_ROLE = 3


    class Server

      def initialize(server)
        @server = server
        @buffers = {}
        @default_parameters = {
          "FCGI_MAX_CONNS" => 1,
          "FCGI_MAX_REQS"  => 1,
          "FCGI_MPX_CONNS" => true
        }
      end

      def each_request(&block)
        graceful = false
        trap("SIGUSR1") { graceful = true }
        while true
          begin
            session(&block)
          rescue Errno::EPIPE, EOFError
            # HTTP request is canceled by the remote user
          end
          exit 0 if graceful
        end
      end
      
      def session
        sock, addr = *@server.accept
        return unless sock
        fsock = FastCGISocket.new(sock)
        req = next_request(fsock)
        yield req
        respond_to req, fsock, FCGI_REQUEST_COMPLETE
      ensure
        sock.close if sock and not sock.closed?
      end

      private

      def next_request(sock)
        while rec = sock.read_record
          if rec.management_record?
            case rec.type
            when FCGI_GET_VALUES
              sock.send_record handle_GET_VALUES(rec)
            else
              sock.send_record UnknownTypeRecord.new(rec.request_id, rec.type)
            end
          else
            case rec.type
            when FCGI_BEGIN_REQUEST
              @buffers[rec.request_id] = RecordBuffer.new(rec)
            when FCGI_ABORT_REQUEST
              raise "got ABORT_REQUEST"   # FIXME
            else
              buf = @buffers[rec.request_id]   or next # inactive request
              buf.push rec
              if buf.ready?
                @buffers.delete rec.request_id
                return buf.new_request
              end
            end
          end
        end
        raise "must not happen: FCGI socket unexpected EOF"
      end

      def handle_GET_VALUES(rec)
        h = {}
        rec.values.each_key do |name|
          h[name] = @default_parameters[name]
        end
        ValuesRecord.new(FCGI_GET_VALUES_RESULT, rec.request_id, h)
      end

      def respond_to(req, sock, status)
        split_data(FCGI_STDOUT, req.id, req.out) do |rec|
          sock.send_record rec
        end
        split_data(FCGI_STDERR, req.id, req.err) do |rec|
          sock.send_record rec
        end if req.err.length > 0
        sock.send_record EndRequestRecord.new(req.id, 0, status)
      end

      DATA_UNIT = 16384

      def split_data(type, id, f)
        unless f.length == 0
          f.rewind
          while s = f.read(DATA_UNIT)
            yield GenericDataRecord.new(type, id, s)
          end
        end
        yield GenericDataRecord.new(type, id, '')
      end

    end


    class FastCGISocket
      def initialize(sock)
        @socket = sock
      end

      def read_record
        header = @socket.read(Record::HEADER_LENGTH) or return nil
        return nil unless header.size == Record::HEADER_LENGTH
        version, type, reqid, clen, padlen, reserved = *Record.parse_header(header)
        Record.class_for(type).parse(reqid, read_record_body(clen, padlen))
      end

      def read_record_body(clen, padlen)
        buf = ''
        while buf.length < clen
          buf << @socket.read([1024, clen - buf.length].min)
        end
        @socket.read padlen if padlen
        buf
      end
      private :read_record_body

      def send_record(rec)
        @socket.write rec.serialize
        @socket.flush
      end
    end


    class RecordBuffer
      def initialize(rec)
        @begin_request = rec
        @envs = []
        @stdins = []
        @datas = []
      end

      def push(rec)
        case rec
        when ParamsRecord
          @envs.push rec
        when StdinDataRecord
          @stdins.push rec
        when DataRecord
          @datas.push rec
        else
          raise "got unknown record: #{rec.class}"
        end
      end

      def ready?
        case @begin_request.role
        when FCGI_RESPONDER
          completed?(@envs) and
          completed?(@stdins)
        when FCGI_AUTHORIZER
          completed?(@envs)
        when FCGI_FILTER
          completed?(@envs) and
          completed?(@stdins) and
          completed?(@datas)
        else
          raise "unknown role: #{@begin_request.role}"
        end
      end

      def completed?(records)
        records.last and records.last.empty?
      end
      private :completed?

      def new_request
        Request.new(@begin_request.request_id, env(), stdin(), nil, nil, data())
      end

      def env
        h = {}
        @envs.each {|rec| h.update rec.values }
        h
      end

      def stdin
        StringIO.new(@stdins.inject('') {|buf, rec| buf << rec.flagment })
      end

      def data
        StringIO.new(@datas.inject('') {|buf, rec| buf << rec.flagment })
      end
    end


    class Request
      def initialize(id, env, stdin, stdout = nil, stderr = nil, data = nil)
        @id = id
        @env = env
        @in = stdin
        @out = stdout || StringIO.new
        @err = stderr || StringIO.new
        @data = data || StringIO.new
      end

      attr_reader :id
      attr_reader :env
      attr_reader :in
      attr_reader :out
      attr_reader :err
      attr_reader :data

      def finish   # for backword compatibility
      end
    end


    class Record
      # uint8_t  protocol_version;
      # uint8_t  record_type;
      # uint16_t request_id;     (big endian)
      # uint16_t content_length; (big endian)
      # uint8_t  padding_length;
      # uint8_t  reserved;
      HEADER_FORMAT = 'CCnnCC'
      HEADER_LENGTH = 8

      def self::parse_header(buf)
        return *buf.unpack(HEADER_FORMAT)
      end

      def self::class_for(type)
        RECORD_CLASS[type]
      end

      def initialize(type, reqid)
        @type = type
        @request_id = reqid
      end

      def version
        ::FCGI::ProtocolVersion
      end

      attr_reader :type
      attr_reader :request_id

      def management_record?
        @request_id == FCGI_NULL_REQUEST_ID
      end

      def serialize
        body = make_body()
        padlen = body.length % 8
        header = make_header(body.length, padlen)
        header + body + "\000" * padlen
      end

      private

      def make_header(clen, padlen)
        [version(), @type, @request_id, clen, padlen, 0].pack(HEADER_FORMAT)
      end
    end

    class BeginRequestRecord < Record
      # uint16_t role; (big endian)
      # uint8_t  flags;
      # uint8_t  reserved[5];
      BODY_FORMAT = 'nCC5'

      def BeginRequestRecord.parse(id, body)
        role, flags, *reserved = *body.unpack(BODY_FORMAT)
        new(id, role, flags)
      end

      def initialize(id, role, flags)
        super FCGI_BEGIN_REQUEST, id
        @role = role
        @flags = flags
      end

      attr_reader :role
      attr_reader :flags
      
      def make_body
        [@role, @flags, 0, 0, 0, 0, 0].pack(BODY_FORMAT)
      end
    end

    class AbortRequestRecord < Record
      def AbortRequestRecord.parse(id, body)
        new(id)
      end

      def initialize(id)
        super FCGI_ABORT_REQUEST, id
      end
    end

    class EndRequestRecord < Record
      # uint32_t appStatus; (big endian)
      # uint8_t  protocolStatus;
      # uint8_t  reserved[3];
      BODY_FORMAT = 'NCC3'

      def self::parse(id, body)
        appstatus, protostatus, *reserved = *body.unpack(BODY_FORMAT)
        new(id, appstatus, protostatus)
      end

      def initialize(id, appstatus, protostatus)
        super FCGI_END_REQUEST, id
        @application_status = appstatus
        @protocol_status = protostatus
      end

      attr_reader :application_status
      attr_reader :protocol_status

      private

      def make_body
        [@application_status, @protocol_status, 0, 0, 0].pack(BODY_FORMAT)
      end
    end

    class UnknownTypeRecord < Record
      # uint8_t type;
      # uint8_t reserved[7];
      BODY_FORMAT = 'CC7'

      def self::parse(id, body)
        type, *reserved = *body.unpack(BODY_FORMAT)
        new(id, type)
      end

      def initialize(id, t)
        super FCGI_UNKNOWN_TYPE, id
        @unknown_type = t
      end

      attr_reader :unknown_type

      private

      def make_body
        [@unknown_type, 0, 0, 0, 0, 0, 0, 0].pack(BODY_FORMAT)
      end
    end

    class ValuesRecord < Record
      def self::parse(id, body)
        new(id, parse_values(body))
      end

      def self::parse_values(buf)
        result = {}
        until buf.empty?
          name, value = *read_pair(buf)
          result[name] = value
        end
        result
      end
      
      def self::read_pair(buf)
        nlen = read_length(buf)
        vlen = read_length(buf)
        return buf.slice!(0, nlen), buf.slice!(0, vlen)
      end
      
      def self::read_length(buf)
        if buf[0] >> 7 == 0
        then buf.slice!(0,1)[0]
        else buf.slice!(0,4).unpack('N')[0] & ((1<<31) - 1)
        end
      end

      def initialize(type, id, values)
        super type, id
        @values = values
      end

      attr_reader :values

      private

      def make_body
        buf = ''
        @values.each do |name, value|
          buf << serialize_length(name.length)
          buf << serialize_length(value.length)
          buf << name
          buf << value
        end
        buf
      end

      def serialize_length(len)
        if len < 0x80
        then len.chr
        else [len | (1<<31)].pack('N')
        end
      end
    end

    class GetValuesRecord < ValuesRecord
      def initialize(id, values)
        super FCGI_GET_VALUES, id, values
      end
    end

    class ParamsRecord < ValuesRecord
      def initialize(id, values)
        super FCGI_PARAMS, id, values
      end

      def empty?
        @values.empty?
      end
    end

    class GenericDataRecord < Record
      def self::parse(id, body)
        new(id, body)
      end

      def initialize(type, id, flagment)
        super type, id
        @flagment = flagment
      end

      attr_reader :flagment

      def empty?
        @flagment.empty?
      end

      private

      def make_body
        @flagment
      end
    end

    class StdinDataRecord < GenericDataRecord
      def initialize(id, flagment)
        super FCGI_STDIN, id, flagment
      end
    end

    class StdoutDataRecord < GenericDataRecord
      def initialize(id, flagment)
        super FCGI_STDOUT, id, flagment
      end
    end

    class DataRecord < GenericDataRecord
      def initialize(id, flagment)
        super FCGI_DATA, id, flagment
      end
    end

    class Record   # redefine
      RECORD_CLASS = {
        FCGI_GET_VALUES    => GetValuesRecord,

        FCGI_BEGIN_REQUEST => BeginRequestRecord,
        FCGI_ABORT_REQUEST => AbortRequestRecord,
        FCGI_PARAMS        => ParamsRecord,
        FCGI_STDIN         => StdinDataRecord,
        FCGI_DATA          => DataRecord,
        FCGI_STDOUT        => StdoutDataRecord,
        FCGI_END_REQUEST   => EndRequestRecord
      }
    end

  end # FCGI class
end # begin

# There is no C version of 'each_cgi'
# Note: for ruby-1.6.8 at least, the constants CGI_PARAMS/CGI_COOKIES
# are defined within module 'CGI', even if you have subclassed it

class FCGI
  def self::each_cgi(*args)
    require 'cgi'
    
    eval(<<-EOS,TOPLEVEL_BINDING)
    class CGI
      public :env_table
      def self::remove_params
        if (const_defined?(:CGI_PARAMS))
          remove_const(:CGI_PARAMS)
          remove_const(:CGI_COOKIES)
        end
      end
    end # ::CGI class

    class FCGI
      class CGI < ::CGI
        def initialize(request, *args)
          ::CGI.remove_params
          @request = request
          super(*args)
          @args = *args
        end
        def args
          @args
        end
        def env_table
          @request.env
        end
        def stdinput
          @request.in
        end
        def stdoutput
          @request.out
        end
      end # FCGI::CGI class
    end # FCGI class
    EOS
    
    if FCGI::is_cgi?
      yield ::CGI.new(*args)
    else
      exit_requested = false
      FCGI::each {|request|
        $stdout, $stderr = request.out, request.err

        yield CGI.new(request, *args)
        
        request.finish
      }
    end
  end
end

class ShareLinksController < ApplicationController
  before_filter :require_admin, :only => [:index, :destroy]
  before_filter :require_existing_file, :except => :index
  before_filter :require_existing_share_link, :only => :destroy
  before_filter :require_read_permission, :only => [:new, :create]
  skip_before_filter :require_login, :only => :show

  def index
    @share_links = ShareLink.active_share_links
  end

  # Note: @file is set in require_existing_file
  def show
    send_file @file.attachment.path, :filename => @file.attachment_file_name unless @file.nil?
  end

  # Note: @file is set in require_existing_file
  def new
    @share_link = @file.share_links.build
  end

  # Note: @file is set in require_existing_file
  def create
    @share_link = @file.share_links.build(params[:share_link])

    if @share_link.save
      UserMailer.share_link_email(current_user, @share_link).deliver
      redirect_to folder_url(@folder), :notice => t(:shared_successfully)
    else
      render :action => 'new'
    end
  end

  # Note: @share_link is set in require_existing_share_link
  def destroy
    @share_link.destroy
    redirect_to share_links_url
  end

  private

  def require_existing_file
    @file = params[:file_id].blank? ? ShareLink.file_for_token(params[:id]) : UserFile.find(params[:file_id])
    @folder = @file.folder
  rescue ActiveRecord::RecordNotFound
    redirect_to folder_url(Folder.root), :alert => t(:already_deleted, :type => t(:this_file))
  rescue NoMethodError
    flash[:alert] = t(:already_deleted, :type => t(:this_file))
  rescue RuntimeError => e
    if e.message == 'This share link expired.'
      flash[:alert] = t(:share_link_expired)
    else
      raise e
    end
  end

  def require_existing_share_link
    @share_link = ShareLink.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    redirect_to share_links_url, :alert => t(:already_deleted, :type => t(:this_share_link))
  end
end

# -*- ruby -*-
#--
# Copyright 2006 by Chad Fowler, Rich Kilmer, Jim Weirich and others.
# All rights reserved.
# See LICENSE.txt for permissions.
#++

require 'rubygems/rubygems_version'
require 'rubygems/defaults'
require 'thread'

module Gem
  class LoadError < ::LoadError
    attr_accessor :name, :version_requirement
  end
end

module Kernel

  # Adds a Ruby Gem to the $LOAD_PATH.  Before a Gem is loaded, its
  # required Gems are loaded.  If the version information is omitted,
  # the highest version Gem of the supplied name is loaded.  If a Gem
  # is not found that meets the version requirement and/or a required
  # Gem is not found, a Gem::LoadError is raised. More information on
  # version requirements can be found in the Gem::Version
  # documentation.
  #
  # The +gem+ directive should be executed *before* any require
  # statements (otherwise rubygems might select a conflicting library
  # version).
  #
  # You can define the environment variable GEM_SKIP as a way to not
  # load specified gems.  You might do this to test out changes that
  # haven't been installed yet.  Example:
  #
  #   GEM_SKIP=libA:libB ruby-I../libA -I../libB ./mycode.rb
  #
  # gem:: [String or Gem::Dependency] The gem name or dependency
  #       instance.
  #
  # version_requirement:: [default=">= 0"] The version
  #                       requirement.
  #
  # return:: [Boolean] true if the Gem is loaded, otherwise false.
  #
  # raises:: [Gem::LoadError] if Gem cannot be found, is listed in
  #          GEM_SKIP, or version requirement not met.
  #
  def gem(gem_name, *version_requirements)
    active_gem_with_options(gem_name, version_requirements)
  end

  # Return the file name (string) and line number (integer) of the caller of
  # the caller of this method.
  def location_of_caller
    file, lineno = caller[1].split(':')
    lineno = lineno.to_i
    [file, lineno]
  end
  private :location_of_caller

  def active_gem_with_options(gem_name, version_requirements, options={})
    skip_list = (ENV['GEM_SKIP'] || "").split(/:/)
    raise Gem::LoadError, "skipping #{gem_name}" if skip_list.include? gem_name
    Gem.activate(gem_name, options[:auto_require], *version_requirements)
  end
  private :active_gem_with_options
end

# Main module to hold all RubyGem classes/modules.
#
module Gem

  ConfigMap = {} unless defined?(ConfigMap)
  require 'rbconfig'
  RbConfig = Config unless defined? ::RbConfig
  ConfigMap.merge!(
      :BASERUBY => RbConfig::CONFIG["BASERUBY"],
      :EXEEXT => RbConfig::CONFIG["EXEEXT"],
      :RUBY_INSTALL_NAME => RbConfig::CONFIG["RUBY_INSTALL_NAME"],
      :RUBY_SO_NAME => RbConfig::CONFIG["RUBY_SO_NAME"],
      :arch => RbConfig::CONFIG["arch"],
      :bindir => RbConfig::CONFIG["bindir"],
      :libdir => RbConfig::CONFIG["libdir"],
      :ruby_install_name => RbConfig::CONFIG["ruby_install_name"],
      :ruby_version => RbConfig::CONFIG["ruby_version"],
      :sitedir => RbConfig::CONFIG["sitedir"],
      :sitelibdir => RbConfig::CONFIG["sitelibdir"]
  )

  MUTEX = Mutex.new

  RubyGemsPackageVersion = RubyGemsVersion

  DIRECTORIES = %w[cache doc gems specifications] unless defined?(DIRECTORIES)

  @@source_index = nil
  @@win_platform = nil

  @configuration = nil
  @loaded_specs = {}
  @platforms = nil
  @ruby = nil
  @sources = []

  # Reset the +dir+ and +path+ values.  The next time +dir+ or +path+
  # is requested, the values will be calculated from scratch.  This is
  # mainly used by the unit tests to provide test isolation.
  #
  def self.clear_paths
    @gem_home = nil
    @gem_path = nil
    @@source_index = nil
    MUTEX.synchronize do
      @searcher = nil
    end
  end

  # The version of the Marshal format for your Ruby.
  def self.marshal_version
    "#{Marshal::MAJOR_VERSION}.#{Marshal::MINOR_VERSION}"
  end

  ##
  # The directory prefix this RubyGems was installed at.

  def self.prefix
    prefix = File.dirname File.expand_path(__FILE__)
    if prefix == ConfigMap[:sitelibdir] then
      nil
    else
      File.dirname prefix
    end
  end

  # Returns an Cache of specifications that are in the Gem.path
  #
  # return:: [Gem::SourceIndex] Index of installed Gem::Specifications
  #
  def self.source_index
    @@source_index ||= SourceIndex.from_installed_gems
  end

  ##
  # An Array of Regexps that match windows ruby platforms.

  WIN_PATTERNS = [
    /bccwin/i,
    /cygwin/i,
    /djgpp/i,
    /mingw/i,
    /mswin/i,
    /wince/i,
  ]

  ##
  # Is this a windows platform?

  def self.win_platform?
    if @@win_platform.nil? then
      @@win_platform = !!WIN_PATTERNS.find { |r| RUBY_PLATFORM =~ r }
    end

    @@win_platform
  end

  class << self

    attr_reader :loaded_specs

    # Quietly ensure the named Gem directory contains all the proper
    # subdirectories.  If we can't create a directory due to a permission
    # problem, then we will silently continue.
    def ensure_gem_subdirectories(gemdir)
      require 'fileutils'

      Gem::DIRECTORIES.each do |filename|
        fn = File.join gemdir, filename
        FileUtils.mkdir_p fn rescue nil unless File.exist? fn
      end
    end

    def platforms
      @platforms ||= [Gem::Platform::RUBY, Gem::Platform.local]
    end

    # Returns an Array of sources to fetch remote gems from.  If the sources
    # list is empty, attempts to load the "sources" gem, then uses
    # default_sources if it is not installed.
    def sources
      if @sources.empty? then
        begin
          gem 'sources', '> 0.0.1'
          require 'sources'
        rescue LoadError
          @sources = default_sources
        end
      end

      @sources
    end


    # Provide an alias for the old name.
    alias cache source_index

    # The directory path where Gems are to be installed.
    #
    # return:: [String] The directory path
    #
    def dir
      @gem_home ||= nil
      set_home(ENV['GEM_HOME'] || default_dir) unless @gem_home
      @gem_home
    end

    # The directory path where executables are to be installed.
    #
    def bindir(install_dir=Gem.dir)
      return File.join(install_dir, 'bin') unless
        install_dir.to_s == Gem.default_dir

      if defined? RUBY_FRAMEWORK_VERSION then # mac framework support
        '/usr/bin'
      else # generic install
        ConfigMap[:bindir]
      end
    end

    # List of directory paths to search for Gems.
    #
    # return:: [List<String>] List of directory paths.
    #
    def path
      @gem_path ||= nil
      unless @gem_path
        paths = [ENV['GEM_PATH']]
        paths << APPLE_GEM_HOME if defined? APPLE_GEM_HOME
        set_paths(paths.compact.join(File::PATH_SEPARATOR))
      end
      @gem_path
    end

    # The home directory for the user.
    def user_home
      @user_home ||= find_home
    end

    # Return the path to standard location of the users .gemrc file.
    def config_file
      File.join(Gem.user_home, '.gemrc')
    end

    # The standard configuration object for gems.
    def configuration
      return @configuration if @configuration
      require 'rubygems/config_file'
      @configuration = Gem::ConfigFile.new []
    end

    # Use the given configuration object (which implements the
    # ConfigFile protocol) as the standard configuration object.
    def configuration=(config)
      @configuration = config
    end

    # Return the path the the data directory specified by the gem
    # name.  If the package is not available as a gem, return nil.
    def datadir(gem_name)
      spec = @loaded_specs[gem_name]
      return nil if spec.nil?
      File.join(spec.full_gem_path, 'data', gem_name)
    end

    # Return the searcher object to search for matching gems.
    def searcher
      MUTEX.synchronize do
        @searcher ||= Gem::GemPathSearcher.new
      end
    end

    # Return the Ruby command to use to execute the Ruby interpreter.
    def ruby
      if @ruby.nil? then
        @ruby = File.join(ConfigMap[:bindir],
                          ConfigMap[:ruby_install_name])
        @ruby << ConfigMap[:EXEEXT]
      end

      @ruby
    end

    # Activate a gem (i.e. add it to the Ruby load path).  The gem
    # must satisfy all the specified version constraints.  If
    # +autorequire+ is true, then automatically require the specified
    # autorequire file in the gem spec.
    #
    # Returns true if the gem is loaded by this call, false if it is
    # already loaded, or an exception otherwise.
    #
    def activate(gem, autorequire, *version_requirements)
      if version_requirements.empty? then
        version_requirements = Gem::Requirement.default
      end

      unless gem.respond_to?(:name) && gem.respond_to?(:version_requirements)
        gem = Gem::Dependency.new(gem, version_requirements)
      end

      matches = Gem.source_index.find_name(gem.name, gem.version_requirements)
      report_activate_error(gem) if matches.empty?

      if @loaded_specs[gem.name]
        # This gem is already loaded.  If the currently loaded gem is
        # not in the list of candidate gems, then we have a version
        # conflict.
        existing_spec = @loaded_specs[gem.name]
        if ! matches.any? { |spec| spec.version == existing_spec.version }
          fail Gem::Exception, "can't activate #{gem}, already activated #{existing_spec.full_name}]"
        end
        return false
      end

      # new load
      spec = matches.last
      if spec.loaded?
        return false unless autorequire
        result = spec.autorequire ? require(spec.autorequire) : false
        return result || false
      end

      spec.loaded = true
      @loaded_specs[spec.name] = spec

      # Load dependent gems first
      spec.dependencies.each do |dep_gem|
        activate(dep_gem, autorequire)
      end

      # bin directory must come before library directories
      spec.require_paths.unshift spec.bindir if spec.bindir

      require_paths = spec.require_paths.map do |path|
        File.join spec.full_gem_path, path
      end

      sitelibdir = ConfigMap[:sitelibdir]

      # gem directories must come after -I and ENV['RUBYLIB']
      $:.insert($:.index(sitelibdir), *require_paths)

      # Now autorequire
      if autorequire && spec.autorequire then # DEPRECATED
        Array(spec.autorequire).each do |a_lib|
          require a_lib
        end
      end

      return true
    end

    # Report a load error during activation.  The message of load
    # error depends on whether it was a version mismatch or if there
    # are not gems of any version by the requested name.
    def report_activate_error(gem)
      matches = Gem.source_index.find_name(gem.name)

      if matches.empty? then
        error = Gem::LoadError.new(
          "Could not find RubyGem #{gem.name} (#{gem.version_requirements})\n")
      else
        error = Gem::LoadError.new(
          "RubyGem version error: " +
          "#{gem.name}(#{matches.first.version} not #{gem.version_requirements})\n")
      end

      error.name = gem.name
      error.version_requirement = gem.version_requirements
      raise error
    end
    private :report_activate_error

    # Use the +home+ and (optional) +paths+ values for +dir+ and +path+.
    # Used mainly by the unit tests to provide environment isolation.
    #
    def use_paths(home, paths=[])
      clear_paths
      set_home(home) if home
      set_paths(paths.join(File::PATH_SEPARATOR)) if paths
    end

    # Return a list of all possible load paths for all versions for
    # all gems in the Gem installation.
    #
    def all_load_paths
      result = []
      Gem.path.each do |gemdir|
        each_load_path(all_partials(gemdir)) do |load_path|
          result << load_path
        end
      end
      result
    end

    # Return a list of all possible load paths for the latest version
    # for all gems in the Gem installation.
    def latest_load_paths
      result = []
      Gem.path.each do |gemdir|
        each_load_path(latest_partials(gemdir)) do |load_path|
          result << load_path
        end
      end
      result
    end

    def required_location(gemname, libfile, *version_constraints)
      version_constraints = Gem::Requirement.default if version_constraints.empty?
      matches = Gem.source_index.find_name(gemname, version_constraints)
      return nil if matches.empty?
      spec = matches.last
      spec.require_paths.each do |path|
        result = File.join(spec.full_gem_path, path, libfile)
        return result if File.exist?(result)
      end
      nil
    end

    def suffixes
      ['', '.rb', '.rbw', '.so', '.bundle', '.dll', '.sl', '.jar']
    end

    def suffix_pattern
      @suffix_pattern ||= "{#{suffixes.join(',')}}"
    end

    # manage_gems is useless and deprecated.  Don't call it anymore.  This
    # will warn in two releases.
    def manage_gems
      # do nothing
    end

    private

    # Return all the partial paths in the given +gemdir+.
    def all_partials(gemdir)
      Dir[File.join(gemdir, 'gems/*')]
    end

    # Return only the latest partial paths in the given +gemdir+.
    def latest_partials(gemdir)
      latest = {}
      all_partials(gemdir).each do |gp|
        base = File.basename(gp)
        if base =~ /(.*)-((\d+\.)*\d+)/ then
          name, version = $1, $2
          ver = Gem::Version.new(version)
          if latest[name].nil? || ver > latest[name][0]
            latest[name] = [ver, gp]
          end
        end
      end
      latest.collect { |k,v| v[1] }
    end

    # Expand each partial gem path with each of the required paths
    # specified in the Gem spec.  Each expanded path is yielded.
    def each_load_path(partials)
      partials.each do |gp|
        base = File.basename(gp)
        specfn = File.join(dir, "specifications", base + ".gemspec")
        if File.exist?(specfn)
          spec = eval(File.read(specfn))
          spec.require_paths.each do |rp|
            yield(File.join(gp, rp))
          end
        else
          filename = File.join(gp, 'lib')
          yield(filename) if File.exist?(filename)
        end
      end
    end

    # Set the Gem home directory (as reported by +dir+).
    def set_home(home)
      @gem_home = home
      ensure_gem_subdirectories(@gem_home)
    end

    # Set the Gem search path (as reported by +path+).
    def set_paths(gpaths)
      if gpaths
        @gem_path = gpaths.split(File::PATH_SEPARATOR)
        @gem_path << Gem.dir
      else
        @gem_path = [Gem.dir]
      end
      @gem_path.uniq!
      @gem_path.each do |gp| ensure_gem_subdirectories(gp) end
    end

    # Some comments from the ruby-talk list regarding finding the home
    # directory:
    #
    #   I have HOME, USERPROFILE and HOMEDRIVE + HOMEPATH. Ruby seems
    #   to be depending on HOME in those code samples. I propose that
    #   it should fallback to USERPROFILE and HOMEDRIVE + HOMEPATH (at
    #   least on Win32).
    #
    def find_home
      ['HOME', 'USERPROFILE'].each do |homekey|
        return ENV[homekey] if ENV[homekey]
      end
      if ENV['HOMEDRIVE'] && ENV['HOMEPATH']
        return "#{ENV['HOMEDRIVE']}:#{ENV['HOMEPATH']}"
      end
      begin
        File.expand_path("~")
      rescue StandardError => ex
        if File::ALT_SEPARATOR
          "C:/"
        else
          "/"
        end
      end
    end

  end

end

require "help/script_execution_state"
require "scripts/ec2/ec2_script"
require "help/remote_command_handler"
#require "help/dm_crypt_helper"
require "help/ec2_helper"
require "AWS"

# Creates a bootable EBS storage from an existing AMI.

class Ami2EbsConversion < Ec2Script
  # Input parameters
  # * aws_access_key => the Amazon AWS Access Key (see Your Account -> Security Credentials)
  # * aws_secret_key => the Amazon AWS Secret Key
  # * ami_id => the ID of the AMI to be converted
  # * security_group_name => name of the security group to start
  # * ssh_username => name of the ssh-user (default = root)
  # * ssh_key_data => Key information for the security group that starts the AMI [if not set, use ssh_key_files]
  # * ssh_key_files => Key information for the security group that starts the AMI
  # * remote_command_handler => object that allows to connect via ssh and execute commands (optional)
  # * ec2_api_handler => object that allows to access the EC2 API (optional)
  # * ec2_api_server => server to connect to (option, default is us-east-1.ec2.amazonaws.com)
  # * name => the name of the AMI to be created
  # * description => description on AMI to be created (optional)
  # * temp_device_name => [default /dev/sdj] device name used to attach the temporary storage; change this only if there's already a volume attacged as /dev/sdj (optional, default is /dev/sdj)
  # * root_device_name"=> [default /dev/sda1] device name used for the root device (optional)
  # * connect_trials => number of trials during ssh connect to machine
  # * connect_interval => seconds between two ssh connect trials
  def initialize(input_params)
    super(input_params)
  end

  def check_input_parameters()
    if @input_params[:security_group_name] == nil
      @input_params[:security_group_name] = "default"
    end
    if @input_params[:ami_id] == nil && !(@input_params[:ami_id] =~ /^ami-.*$/)
      raise Exception.new("Invalid AMI ID specified: #{@input_params[:ami_id]}")
    end
    ec2_helper = Ec2Helper.new(@input_params[:ec2_api_handler])
    if !ec2_helper.check_open_port(@input_params[:security_group_name], 22)
      raise Exception.new("Port 22 must be opened for security group #{@input_params[:security_group_name]} to connect via SSH")
    end
    if @input_params[:name] == nil
      @input_params[:name] = "Boot EBS (for AMI #{@input_params[:ami_id]}) at #{Time.now.strftime('%d/%m/%Y %H.%M.%S')}"
    else
    end
    if @input_params[:description] == nil
      @input_params[:description] = @input_params[:name]
    end
    if @input_params[:temp_device_name] == nil
      @input_params[:temp_device_name] = "/dev/sdj"
    end
    if @input_params[:root_device_name] == nil
      @input_params[:root_device_name] = "/dev/sda1"
    end
    if @input_params[:ssh_username] == nil
      @input_params[:ssh_username] = "root"
    end
    if @input_params[:connect_trials] == nil
      @input_params[:connect_trials] = 6
    end
    if @input_params[:connect_interval] == nil
      @input_params[:connect_interval] = 20
    end
  end

  def load_initial_state()
    Ami2EbsConversionState.load_state(@input_params)
  end
  
  private

  # Here begins the state machine implementation
  class Ami2EbsConversionState < ScriptExecutionState
    def self.load_state(context)
      state = context[:initial_state] == nil ? InitialState.new(context) : context[:initial_state]
      state
    end

  end

  # Nothing done yet. Start by instantiating an AMI (in the right zone?)
  # which serves to create 
  class InitialState < Ami2EbsConversionState
    def enter
      puts "DEBUG: params: #{@context[:ami_id]}, #{@context[:key_name]}, #{@context[:security_group_name]}"
      @context[:instance_id], @context[:dns_name], @context[:availability_zone], 
        @context[:kernel_id], @context[:ramdisk_id], @context[:architecture] =
        launch_instance(@context[:ami_id], @context[:key_name], @context[:security_group_name])
      AmiStarted.new(@context)
    end
  end

  # Ami started. Create a storage
  class AmiStarted < Ami2EbsConversionState
    def enter
      @context[:volume_id] = create_volume(@context[:availability_zone], "10")
      StorageCreated.new(@context)
    end
  end

  # Storage created. Attach it.
  class StorageCreated < Ami2EbsConversionState
    def enter
      attach_volume(@context[:volume_id], @context[:instance_id], @context[:temp_device_name])
      StorageAttached.new(@context)
    end
  end

  # Storage attached. Create a file-system and mount it
  class StorageAttached < Ami2EbsConversionState
    def enter
      @context[:result][:os] =
        connect(@context[:dns_name], @context[:ssh_username],
        @context[:ssh_keyfile], @context[:ssh_keydata],
        @context[:connect_trials], @context[:connect_interval]
      )
      # get root partition label and filesystem type
      @context[:label] = get_root_partition_label()
      @context[:fs_type] = get_root_partition_fs_type()
      create_labeled_fs(@context[:dns_name], @context[:temp_device_name], @context[:fs_type], @context[:label])      
      FileSystemCreated.new(@context)
    end
  end

  # File system created. Mount it.
  class FileSystemCreated < Ami2EbsConversionState
    def enter
      @context[:mount_dir] = "/ebs_#{@context[:volume_id]}"
      mount_fs(@context[:mount_dir], @context[:temp_device_name])
      FileSystemMounted.new(@context)
    end
  end

  # File system created and mounted. Copy the root partition.
  class FileSystemMounted < Ami2EbsConversionState
    def enter
      copy_distribution(@context[:mount_dir])
      CopyDone.new(@context)
    end
  end
  
  # Copy operation done. Unmount volume.
  class CopyDone < Ami2EbsConversionState
    def enter
      unmount_fs(@context[:mount_dir])
      VolumeUnmounted.new(@context)
    end
  end

  # Volume unmounted. Detach it.
  class VolumeUnmounted < Ami2EbsConversionState
    def enter
      detach_volume(@context[:volume_id], @context[:instance_id])
      VolumeDetached.new(@context)
    end
  end

  # VolumeDetached. Create snaphot
  class VolumeDetached < Ami2EbsConversionState
    def enter
      @context[:snapshot_id] = create_snapshot(@context[:volume_id])
      SnapshotCreated.new(@context)
    end
  end

  # Snapshot created. Delete volume.
  class SnapshotCreated < Ami2EbsConversionState
    def enter
      delete_volume(@context[:volume_id])
      VolumeDeleted.new(@context)
    end
  end

  # Volume deleted. Register snapshot.
  class VolumeDeleted < Ami2EbsConversionState
    def enter
      @context[:result][:image_id] = register_snapshot(@context[:snapshot_id], @context[:name],
        @context[:root_device_name], @context[:description], @context[:kernel_id],
        @context[:ramdisk_id], @context[:architecture])
      SnapshotRegistered.new(@context)
    end
  end

  # Snapshot registered. Shutdown instance.
  class SnapshotRegistered < Ami2EbsConversionState
    def enter
      shut_down_instance(@context[:instance_id])
      Done.new(@context)      
    end
  end

  # Instance shutdown. Done.
  class Done < Ami2EbsConversionState
    def done?
      true
    end
  end
  
end

############################################################
#                                                          #
# The implementation of PHPRPC Protocol 3.0                #
#                                                          #
# client.rb                                                #

require "net/http"
require "net/https"
require "uri"
require "digest/md5"
require "php/formator"
require "crypt/xxtea"
require "powmod"
require "thread"

module PHPRPC

  class Error < Exception
    attr_accessor :number
  end

  class Client

    VERSION = '3.00'

    @@cookie = ''
    @@cookies = {}
    @@sid = 0
    @@mutex = Mutex.new

    def initialize(url = nil)
      @clientID = "ruby" + rand(1 << 32).to_s + Time.now.to_i.to_s + @@sid.to_s
      @@sid += 1
      Net::HTTP.version_1_2
      @httpclients = []
      @http = Net::HTTP
      @uri = nil
      if url then
        @uri = URI.parse(url)
        if @uri.query.nil? then
            @uri.query = "phprpc_id=" + @clientID
        else
            @uri.query = @uri.query + "&phprpc_id=" + @clientID
        end
      end
      @mutex = Mutex.new
      @timeout = 30
      @output = ''
      @warning = nil
      @key = nil
      @keylength = 128
      @encryptmode = 0
      @keyexchanged = false;
      @charset = 'utf-8'
      @server_version = nil
    end

    def use_service(url = nil, username = nil, password = nil)
      if url then
        close
        @uri = URI.parse(url)
        if @uri.query.nil? then
            @uri.query = "phprpc_id=" + @clientID
        else
            @uri.query = @uri.query + "&phprpc_id=" + @clientID
        end
        @key = nil
        @keylength = 128
        @encryptmode = 0
        @keyexchanged = false;
        @charset = 'utf-8'
        @uri.user = username unless username.nil?
        @uri.password = password unless password.nil?
      end
      Proxy.new(self)
    end

    def set_proxy(p_addr, p_port = nil, p_user = nil, p_pass = nil)
      close
      @http = Net::HTTP::Proxy(p_addr, p_port, p_user, p_pass)
    end

    def proxy=(proxy)
      close
      @http = case proxy
      when Net::HTTP then
        proxy
      when String then
        uri = URI.parse(proxy)
        Net::HTTP::Proxy(uri.host, uri.port, uri.user, uri.password)
      else
        proxy.superclass == Net::HTTP ? proxy : Net::HTTP
      end
    end

    attr_reader :keylength

    def keylength=(val)
      @keylength = val if @key.nil?
    end

    attr_reader :encryptmode

    def encryptmode=(val)
      @encryptmode = ((val >= 0) and (val <= 3)) ? val.floor : 0;
    end

    attr_accessor :charset, :timeout

    attr_reader :output, :warning

    def invoke(methodname, args, byref = false, encryptmode = nil, &block)
      if block_given? then
        Thread.start {
          data = _invoke(methodname, args, byref, encryptmode)
          case block.arity
            when 0: yield
            when 1: yield data[:result]
            when 2: yield data[:result], args
            when 3: yield data[:result], args, data[:output]
            when 4: yield data[:result], args, data[:output], data[:warning]
          end
        }
      else
        data = _invoke(methodname, args, byref, encryptmode)
        @warning = data[:warning]
        @output = data[:output]
        data[:result]
      end
    end

    def close
      loop do
        httpclient = @httpclients.shift
        break if httpclient.nil?
        httpclient.finish if httpclient.started?
      end
    end

    private

    def _invoke(methodname, args, byref = false, encryptmode = nil)
      data = {}
      begin
        encryptmode = @encryptmode if encryptmode.nil?
        @mutex.synchronize {
          encryptmode = _key_exchange(encryptmode)
        }
        request = "phprpc_func=#{methodname}"
        request << '&phprpc_args=' << [_encrypt(PHP::Formator.serialize(args), 1, encryptmode)].pack('m').delete!("\n").gsub('+', '%2B') if args.size > 0
        request << "&phprpc_encrypt=#{encryptmode}"
        request << '&phprpc_ref=false' unless byref
        result = _post(request)
        if result.key?('phprpc_errstr') and result.key?('phprpc_errno') then
          warning = PHPRPC::Error.new(result['phprpc_errstr'].unpack('m')[0])
          warning.number = result['phprpc_errno'].to_i
        elsif result.key?('phprpc_functions') then
          warning = PHPRPC::Error.new("PHPRPC server haven't received the POST data!")
          warning.number = 1
        else
          warning = PHPRPC::Error.new("PHPRPC server occured unknown error!")
          warning.number = 1
        end
        data[:warning] = warning
        if result.key?('phprpc_output') then
          output = result['phprpc_output'].unpack('m')[0]
          output = _decrypt(output, 3, encryptmode) if @server_version >= 3
        else
          output = ''
        end
        data[:output] = output
        if result.key?('phprpc_result') then
          PHP::Formator.unserialize(_decrypt(result['phprpc_arg'].unpack('m')[0], 1, encryptmode)).each { |key, value|
            args[key] = value
          } if result.key?('phprpc_args')
          data[:result] = PHP::Formator.unserialize(_decrypt(result['phprpc_result'].unpack('m')[0], 2, encryptmode))
        else
          data[:result] = warning
        end
      rescue PHPRPC::Error => e
        data[:result] = e
      rescue Exception => ex
        e = PHPRPC::Error.new(ex.message)
        e.number = 1
        data[:result] = e
      ensure
        return data
      end
    end

    def _raise_error(number, message)
      error = Error.new(message)
      error.number = number
      raise error
    end

    def _post(req)
      httpclient = @httpclients.shift
      if httpclient.nil? then
        httpclient = @http.new(@uri.host, @uri.port)
        httpclient.use_ssl = (@uri.scheme == 'https')
        #httpclient.set_debug_output $stderr
        httpclient.start
      end
      headers = {
        'User-Agent' => "PHPRPC 3.0 Client for Ruby (#{RUBY_VERSION})",
        'Cache-Control' => 'no-cache',
        'Content-Type' => "application/x-www-form-urlencoded; charset=#{@charset}",
        'Content-Length' => req.size.to_s,
        'Connection' => 'keep-alive',
      }
      headers['Cookie'] = @@cookie unless @@cookie.empty?
      headers['Authorization'] = 'Basic ' << ["#{@uri.user}:#{@uri.password}"].pack('m').delete!("\n") unless @uri.user.nil? or @uri.password.nil?
      resp, data = httpclient.request_post(@uri.path + '?' + @uri.query, req, headers)
      @httpclients.push(httpclient)
      if resp.code == '200' then
        if resp.key?('x-powered-by') then
          server_version = nil
          resp['x-powered-by'].split(', ').each { |value|
            server_version = value[14..-1].to_f if value[0, 13] == 'PHPRPC Server'
          }
          _raise_error(1, 'Illegal PHPRPC server.') if server_version.nil?
          @server_version = server_version
        else
          _raise_error(1, 'Illegal PHPRPC server.')
        end
        resp['content-type'].split(', ').each { |value|
          @charset = value[20..-1] if value[/^text\/plain; charset=/i]
        }
        if resp.key?('set-cookie') then
          @@mutex.synchronize {
            resp['set-cookie'].split(/[;,]\s?/).each { |pairs|
              name, value = pairs.split('=', 2)
              values ||= ''
              @@cookies[name] = value unless ['domain', 'expires', 'path', 'secure'].include?(name)
            }
            @@cookie = ''
            @@cookies.each { |name, value|
              @@cookie << "#{name}=#{value}; "
            }
          }
        end
        result = {}
        data.split(/;\r\n/).each { |line|
          result.store(*line.match(/^(phprpc_[a-z]+)="(.*)"$/)[1, 2])
        }
        return result
      else
        _raise_error(resp.code.to_i, resp.message)
      end
    end

    def _key_exchange(encryptmode)
      return encryptmode if (!@key.nil?) or (encryptmode == 0)
      return 0 if (@key.nil?) and (@keyexchanged)
      result = _post("phprpc_encrypt=true&phprpc_keylen=#{@keylength.to_s}")
      @keylength = result.key?('phprpc_keylen') ? result['phprpc_keylen'].to_i : 128
      if result.key?('phprpc_encrypt') then
        encrypt = PHP::Formator.unserialize(result['phprpc_encrypt'].unpack("m")[0])
        x = rand(1 << (@keylength - 1)) or (1 << (@keylength - 2))
        key = Math.powmod(encrypt['y'].to_i, x, encrypt['p'].to_i)
        @key = (@keylength == 128) ? [key.to_s(16).rjust(32, '0')].pack('H*') : Digest::MD5.digest(key.to_s)
        y = Math.powmod(encrypt['g'].to_i, x, encrypt['p'].to_i)
        _post("phprpc_encrypt=#{y}")
      else
        @key = nil
        @keyexchanged = true
        @encryptmode = 0
        encryptmode = 0
      end
      return encryptmode
    end

    def _encrypt(str, level, encryptmode)
      ((not @key.nil?) and (encryptmode >= level)) ? Crypt::XXTEA.encrypt(str, @key) : str
    end

    def _decrypt(str, level, encryptmode)
      ((not @key.nil?) and (encryptmode >= level)) ? Crypt::XXTEA.decrypt(str, @key) : str
    end

    def method_missing(methodname, *args, &block)
      self.invoke(methodname, args, &block)
    end

    class Proxy

      def initialize(phprpc_client)
        @phprpc_client = phprpc_client
      end

      def method_missing(methodname, *args, &block)
        @phprpc_client.invoke(methodname, args, &block)
      end

    end # class Proxy

  end # class Client

end # module PHPRPC

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
