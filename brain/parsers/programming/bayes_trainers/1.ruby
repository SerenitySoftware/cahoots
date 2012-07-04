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