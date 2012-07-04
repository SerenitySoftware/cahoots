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