begin
  require 'rubygems'
rescue LoadError
  nil
end

begin
  require 'attributes'
rescue LoadError
  warn <<-msg
  attributes.rb not found!
  
    download from:
      - http://rubyforge.org/projects/codeforpeople/
      - http://codeforpeople.com/lib/ruby/
  msg
  raise
end

### TODO - use pervasives throughout
begin
  require 'pervasives'
rescue LoadError
  warn <<-msg
  pervasives.rb not found!
  
    download from:
      - http://rubyforge.org/projects/codeforpeople/
      - http://codeforpeople.com/lib/ruby/
  msg
  raise
end

#
# http://en.wikipedia.org/wiki/Prototype-based_programming
#

class Prototype
  VERSION = '2.1.0'

  module ClassMethods
    def version() VERSION end

    def inherit c = Object, *a, &b
      c = c.class unless Class === c
      c = Class.new c
      new c, *a, &b
    end
    alias_method "exnihilo", "inherit"
    alias_method "ex_nihilo", "inherit"

    def new c = Object, *a, &b
      c = c.class unless Class === c
      obj = c.new *a 
      prototyping obj, &b
      obj
    end

    def clone src, *a, &b
      c = src.class
      c = Class.new c
      dst = c.new *a 

      sc =
        class << src 
          self
        end

      modules = sc.instance_variable_get('@modules') || []
      modules.each{|mod| extend dst, mod}

      src.instance_variables.each do |ivar|
        value = src.instance_variable_get ivar
        dst.instance_variable_set ivar, value
      end
      prototyping dst, &b
      dst
    end

    def prototyping obj, &b
      obj.extend InstanceMethods 
      mod = Prototype.context &b
      ivars = mod.__method__["instance_variables"].call()
      ivars.each do |ivar|
        value = mod.__method__["instance_variable_get"].call(ivar)
        obj.instance_eval{ instance_variable_set ivar, value }
      end
      extend obj, mod
      obj
    end

    def extend obj, mod
      sc =
        class << obj
          self
        end
      sc.module_eval do 
        (@modules ||= []) << mod
        include mod
      end
    end

    def prototyped? obj
      sc =
        class << obj
          self
        end
      sc.module_eval do 
        defined?(@prototyped) and @prototyped
      end
    end

    def prototyped! obj
      sc =
        class << obj
          self
        end
      sc.module_eval do 
        @prototyped = true
      end
    end

    def context &b
      mod = Module.new
      sc = 
        class << mod 
          self
        end

      sc.module_eval do
        __method__ = {} and define_method(:__method__){ __method__ }

        def __call__(m, *a, &b)
          meth = __method__[m.to_s]
          raise NoMethodError, m.to_s unless meth
          meth.call *a, &b
        end

        alias_method '__define_method__', 'define_method'
      end

      mod.methods.each{|m| mod.__method__[m] = mod.method(m) unless %w( __call__ __method__ ).include?(m)}

      mod.methods.each do |m|
        unless m =~ /^__|attribute/
          sc.module_eval{ undef_method m }
        end
      end

      sc.module_eval do
        def method_missing m, *a, &b
          if b
            __define_method__ m, *a, &b
          else
            ivar = "@#{ m }"
            case a.size
            when 0
              if eval("defined? #{ ivar }")
                __call__ 'instance_variable_get', ivar
              else
                super
              end
            when 1
              value = a.shift
              __call__ 'instance_variable_set', ivar, value 
            else
              super
            end
          end
        end
      end

      mod.__call__ 'module_eval', &b if b

      mod.__call__ 'module_eval' do
        defined = __call__('instance_methods').inject({}){|h,m| h.update m => true}

        __call__('instance_variables').each do |ivar|
          m = ivar[1..-1]
          getter, setter, query = defined["#{ m }"], defined["#{ m }="], defined["#{ m }?"]

          if getter.nil? and setter.nil? and query.nil? 
            __call__ 'attribute', m
            next
          end
          if getter.nil?
            __call__ 'module_eval', "def #{ m }() #{ ivar } end"
          end
          if setter.nil?
            __call__ 'module_eval', "def #{ m }=(v) #{ ivar }=v end"
          end
          if query.nil?
            __call__ 'module_eval', "def #{ m }?() defined?(#{ ivar }) and #{ ivar } end"
          end
        end
      end

      mod
    end
  end
  extend ClassMethods

  module InstanceMethods
    def clone *a, &b
      Prototype.clone self, *a, &b
    end
    def dup *a, &b
      Prototype.clone self, *a, &b
    end
    def configured hash = {}, &block
      unless hash.empty?
        prototyping do
          hash.each do |k,v|
            begin
              __send__ "#{ k }=", v
            rescue
              __attribute__ k => v
            end
          end
        end
      end
      prototyping &block if block
      self
    end
    alias_method 'configure', 'configured'
    def extend m=nil, &block
      if block
        prototyping(self, &block)
      else
        super(m)
      end
      self
    end
  end
  include InstanceMethods
end

class Object
  def Prototype(*a, &b) Prototype.inherit *a, &b end
  def prototype(*a, &b) Prototype.inherit *a, &b end
  def Prototyping(obj=nil, &b) Prototype.prototyping obj||self, &b end
  def prototyping(obj=nil, &b) Prototype.prototyping obj||self, &b end
end