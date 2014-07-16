#include <stdio.h>
#include <stdlib.h>

/********************************************************/
/*                                                      */
/*                                                      */
/*    Initialise a 4-d array with successive numbers.   */
/*                                                      */
/*                                                      */
/*     The array is formed dynamically using malloc.    */
/*                                                      */
/*     g.watt.porteous (gemera)     17th June 2012      */
/*                                                      */
/*                 graemewp@yahoo.com                   */
/********************************************************/

#define d4 4
#define d3 4
#define d2 4
#define d1 4


void initarr(int ****array,int hyp_sz,int plane_sz,int row_sz,int col_sz);

int main(void)
{
    int ****array;
    int hyp_sz = d4,plane_sz = d3,row_sz = d2,col_sz = d1;
    int h,i,j;

    array = malloc(hyp_sz * sizeof(int***));
    if (array == NULL)
    {
        fprintf(stderr,"Out Of Memory");
        exit(EXIT_FAILURE);
    }

    for(h = 0;h < hyp_sz;h++)
    {
        array[h] = malloc(plane_sz * sizeof(int**));
        if(array[h] == NULL)
        {
            fprintf(stderr,"Out Of Memory");
            exit(EXIT_FAILURE);
        }

        for(i = 0;i < plane_sz;i++)
        {
            array[h][i] = malloc(row_sz * sizeof(int*));
            if(array[h][i] == NULL)
            {
                fprintf(stderr,"Out Of Memory");
                exit(EXIT_FAILURE);
            }
            for(j = 0;j < row_sz;j++)
            {
                array[h][i][j] = malloc(col_sz * sizeof(int));
                if(array[h][i][j] == NULL)
                {
                    fprintf(stderr,"Out Of Memory");
                    exit(EXIT_FAILURE);
                }
            }
        }
    }
    printf("\n\n");

    initarr(array,hyp_sz,plane_sz,row_sz,col_sz);   // initialise and display array

    getchar();
    return 0;
}

void initarr(int ****array,int hyp_sz,int plane_sz,int row_sz,int col_sz)
{
    int g,h,i,j;

    for(g = 0 ;g < hyp_sz; g++)
    {
        for(h = 0;h < plane_sz; h++)
        {
            for(i = 0;i < row_sz; i++)
            {
                for(j = 0;j < col_sz; j++)
                {
                    array[g][h][i][j] = (g*plane_sz*row_sz*col_sz) + (h*row_sz*col_sz) + (i*col_sz )+ j + 1;
                    printf("%5d", array[g][h][i][j]);
                }
                printf("\n");
            }
            printf("\n");
        }
        printf("\n\n");
    }
}
/* --------------------------------------------------------------------------
 * xchat-ruby.c -- glue code between Ruby interpreter and XChat plugin API
 * Copyright (C) 2003 Jamis Buck (jgb3@email.byu.edu)
 * -------------------------------------------------------------------------- */

#include <stdio.h>
#include <stdlib.h>

#include "ruby.h"
#include "xchat-plugin.h"
#include "xchat-ruby-plugin.h"  /* this is the ruby code as a #define */

/* ``global'' variables (global to the XChat-Ruby plugin) {{{ */

#define XCHAT_RUBY_VERSION "1.2"

static xchat_plugin *static_plugin_handle = NULL;
static xchat_plugin *ph = NULL;
static int           static_ruby_initialized = 0;

static VALUE         static_xchat_module;

static VALUE         static_xchat_klass;
static VALUE         static_xchat_list_klass;
static VALUE         static_xchat_hook_klass;
static VALUE         static_xchat_context_klass;
static VALUE         static_xchat_list_internal_klass;

static ID            static_xchat_process_command_hook;
static ID            static_xchat_process_print_hook;
static ID            static_xchat_process_server_hook;
static ID            static_xchat_process_timer_hook;

/*}}}*/

/* private method declarations {{{*/

/**
 * Initializes the ruby environment.
 */
static void static_init_ruby_environment( void );

/**
 * Initializes the XChat environment.
 */
static void static_init_xchat_environment( xchat_plugin *plugin_handle,
                                           char **plugin_name,
                                           char **plugin_desc,
                                           char **plugin_version );

/**
 * Ruby callback function for adding a new callback hook for a
 * command.
 */
static VALUE static_ruby_xchat_hook_command( VALUE klass,
                                             VALUE name,
                                             VALUE priority,
                                             VALUE help );

/**
 * Ruby callback function for adding a new callback hook for a
 * print event.
 */
static VALUE static_ruby_xchat_hook_print( VALUE klass,
                                           VALUE name,
                                           VALUE priority );

/**
 * Ruby callback function for adding a new callback hook for a
 * server event.
 */
static VALUE static_ruby_xchat_hook_server( VALUE klass,
                                            VALUE name,
                                            VALUE priority );

/**
 * Ruby callback function for adding a new callback hook for a
 * timer event.
 */
static VALUE static_ruby_xchat_hook_timer( VALUE klass,
                                           VALUE name,
                                           VALUE timeout );

/**
 * Ruby callback function for printing text to an XChat window.
 */
static VALUE static_ruby_xchat_print( VALUE klass,
                                      VALUE text );

/**
 * Ruby callback function for removing a callback hook.
 */
static VALUE static_ruby_xchat_unhook( VALUE klass,
                                       VALUE hook_id );

/**
 * Ruby callback function for invoking a command
 */
static VALUE static_ruby_xchat_command( VALUE klass,
                                        VALUE command );

/**
 * Ruby callback function for searching for a specified context.
 */
static VALUE static_ruby_xchat_find_context( VALUE klass,
                                             VALUE server,
                                             VALUE channel );

/**
 * Ruby callback function for getting the current XChat context.
 */
static VALUE static_ruby_xchat_get_context( VALUE klass );

/**
 * Ruby callback function for getting a named information value.
 */
static VALUE static_ruby_xchat_get_info( VALUE klass,
                                         VALUE id );

/**
 * Ruby callback function for getting a named user preference.
 */
static VALUE static_ruby_xchat_get_prefs( VALUE klass,
                                          VALUE name );

/**
 * Ruby callback function for setting the current XChat context.
 */
static VALUE static_ruby_xchat_set_context( VALUE klass,
                                            VALUE ctx );

/**
 * Ruby callback function for comparing two nicks.
 */
static VALUE static_ruby_xchat_nickcmp( VALUE klass,
                                        VALUE s1,
                                        VALUE s2 );

/**
 * Ruby callback function for getting a named list.
 */
static VALUE static_ruby_xchat_list_get( VALUE klass,
                                         VALUE name );

/**
 * Ruby callback function for moving to the next value in
 * a named list.
 */
static VALUE static_ruby_xchat_list_next( VALUE klass,
                                          VALUE list );

/**
 * Ruby callback function for getting a named field from
 * a list as a string value.
 */
static VALUE static_ruby_xchat_list_str( VALUE klass,
                                         VALUE list,
                                         VALUE name );

/**
 * Ruby callback function for getting a named field from
 * a list as an integer value.
 */
static VALUE static_ruby_xchat_list_int( VALUE klass,
                                         VALUE list,
                                         VALUE name );

/**
 * Ruby callback function for emitting a print event.
 */
static VALUE static_ruby_xchat_emit_print( int    argc,
                                           VALUE *argv,
                                           VALUE  klass );

/**
 * XChat callbook hook for handling a custom command written
 * in Ruby.
 */
static int static_ruby_custom_command_hook( char *word[],
                                            char *word_eol[],
                                            void *userdata );

/**
 * XChat callbook hook for handling a custom print event
 * handler written in Ruby.
 */
static int static_ruby_custom_print_hook( char *word[],
                                          void *userdata );

/**
 * XChat callbook hook for handling a custom server event
 * handler written in Ruby.
 */
static int static_ruby_custom_server_hook( char *word[],
                                           char *word_eol[],
                                           void *userdata );

/**
 * XChat callbook hook for handling a custom timer event
 * handler written in Ruby.
 */
static int static_ruby_custom_timer_hook( void *userdata );

/**
 * Callback for destroying a list when Ruby garbage collects
 * the associated XChatListInternal object.
 */
static void static_free_xchat_list( xchat_list *list );

/*}}}*/

                                             
static void static_init_ruby_environment( void )
{
  /* only initialize the ruby environment once */
  if( static_ruby_initialized ) return;
  static_ruby_initialized = 1;

  ruby_init();

  /* "XCHAT_RUBY_PLUGIN" is a macro that contains all of the Ruby code needed to
   * define the core XChat-Ruby interface.  Once this has been defined, all we
   * need to do is extract the defined classes and add the C hooks to them.
   */

  rb_eval_string( XCHAT_RUBY_PLUGIN );

  static_xchat_module = rb_define_module( "XChatRuby" );

  static_xchat_klass = rb_define_class_under( static_xchat_module,
                                              "XChatRubyEnvironment",
                                              rb_cObject );
  static_xchat_list_klass = rb_define_class_under( static_xchat_module,
                                                   "XChatRubyList",
                                                   rb_cObject );
  static_xchat_hook_klass = rb_define_class_under( static_xchat_module,
                                                   "XChatRubyCallback",
                                                   rb_cObject );

  static_xchat_context_klass = rb_define_class_under( static_xchat_module,
                                                      "XChatContext",
                                                      rb_cObject );

  static_xchat_list_internal_klass = rb_define_class_under( static_xchat_module,
                                                            "XChatListInternal",
                                                            rb_cObject );

  static_xchat_process_command_hook = rb_intern( "process_command_hook" );
  static_xchat_process_print_hook = rb_intern( "process_print_hook" );
  static_xchat_process_server_hook = rb_intern( "process_server_hook" );
  static_xchat_process_timer_hook = rb_intern( "process_timer_hook" );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_hook_command",
                              static_ruby_xchat_hook_command,
                              3 );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_hook_print",
                              static_ruby_xchat_hook_print,
                              2 );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_hook_server",
                              static_ruby_xchat_hook_server,
                              2 );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_hook_timer",
                              static_ruby_xchat_hook_timer,
                              2 );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_print",
                              static_ruby_xchat_print,
                              1 );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_unhook",
                              static_ruby_xchat_unhook,
                              1 );

  rb_define_singleton_method( static_xchat_klass,
                              "command",
                              static_ruby_xchat_command,
                              1 );

  rb_define_singleton_method( static_xchat_klass,
                              "internal_xchat_find_context",
                              static_ruby_xchat_find_context,
                              2 );

  rb_define_singleton_method( static_xchat_klass,
                              "get_context",
                              static_ruby_xchat_get_context,
                              0 );

  rb_define_singleton_method( static_xchat_klass,
                              "get_info",
                              static_ruby_xchat_get_info,
                              1 );

  rb_define_singleton_method( static_xchat_klass,
                              "get_prefs",
                              static_ruby_xchat_get_prefs,
                              1 );

  rb_define_singleton_method( static_xchat_klass,
                              "set_context",
                              static_ruby_xchat_set_context,
                              1 );

  rb_define_singleton_method( static_xchat_klass,
                              "nickcmp",
                              static_ruby_xchat_nickcmp,
                              2 );

  rb_define_singleton_method( static_xchat_klass,
                              "emit_print",
                              static_ruby_xchat_emit_print,
                              -1 );


  rb_define_method( static_xchat_list_klass,
                    "internal_xchat_list_get",
                    static_ruby_xchat_list_get,
                    1 );

  rb_define_method( static_xchat_list_klass,
                    "internal_xchat_list_next",
                    static_ruby_xchat_list_next,
                    1 );

  rb_define_method( static_xchat_list_klass,
                    "internal_xchat_list_str",
                    static_ruby_xchat_list_str,
                    2 );

  rb_define_method( static_xchat_list_klass,
                    "internal_xchat_list_int",
                    static_ruby_xchat_list_int,
                    2 );


  rb_funcall( static_xchat_klass,
              rb_intern( "register" ),
              0 );
}


static void static_init_xchat_environment( xchat_plugin *plugin_handle,
                                           char **plugin_name,
                                           char **plugin_desc,
                                           char **plugin_version )
{
  *plugin_name = "XChat-Ruby";
  *plugin_desc = "Allows the Ruby interpreter to be interactively called from XChat, "
                 "and for XChat plugins to be written in Ruby.";
  *plugin_version = XCHAT_RUBY_VERSION;
}


static VALUE static_ruby_xchat_hook_command( VALUE klass,
                                             VALUE name,
                                             VALUE priority,
                                             VALUE help )
{
  char *s_name;
  char *s_help;
  int   i_priority;

  xchat_hook *hook;
  VALUE       v_hook;

  Check_Type( name, T_STRING );
  Check_Type( priority, T_FIXNUM );
  Check_Type( help, T_STRING );

  s_name = StringValueCStr( name );
  i_priority = FIX2INT( priority );
  s_help = StringValueCStr( help );

  hook = xchat_hook_command( static_plugin_handle,
                             s_name,
                             i_priority,
                             static_ruby_custom_command_hook,
                             s_help,
                             NULL );

  v_hook = Data_Wrap_Struct( static_xchat_hook_klass,
                             NULL, NULL,
                             hook );

  return v_hook;
}


static VALUE static_ruby_xchat_hook_print( VALUE klass,
                                           VALUE name,
                                           VALUE priority )
{
  char *s_name;
  int   i_priority;
  xchat_hook *hook;
  VALUE v_hook;

  Check_Type( name, T_STRING );
  Check_Type( priority, T_FIXNUM );

  s_name = StringValueCStr( name );
  i_priority = FIX2INT( priority );

  hook = xchat_hook_print( static_plugin_handle,
                           s_name,
                           i_priority,
                           static_ruby_custom_print_hook,
                           (void*)name );

  v_hook = Data_Wrap_Struct( static_xchat_hook_klass,
                             NULL, NULL,
                             hook );

  return v_hook;
}


static VALUE static_ruby_xchat_hook_server( VALUE klass,
                                            VALUE name,
                                            VALUE priority )
{
  char *s_name;
  int   i_priority;
  xchat_hook *hook;
  VALUE v_hook;

  Check_Type( name, T_STRING );
  Check_Type( priority, T_FIXNUM );

  s_name = StringValueCStr( name );
  i_priority = FIX2INT( priority );

  hook = xchat_hook_server( static_plugin_handle,
                            s_name,
                            i_priority,
                            static_ruby_custom_server_hook,
                            NULL );

  v_hook = Data_Wrap_Struct( static_xchat_hook_klass,
                             NULL, NULL,
                             hook );

  return v_hook;
}


static VALUE static_ruby_xchat_hook_timer( VALUE klass,
                                           VALUE name,
                                           VALUE timeout )
{
  char *s_name;
  int   i_timeout;
  xchat_hook *hook;
  VALUE v_hook;

  Check_Type( name, T_STRING );
  Check_Type( timeout, T_FIXNUM );

  s_name = StringValueCStr( name );
  i_timeout = FIX2INT( timeout );

  hook = xchat_hook_timer( static_plugin_handle,
                           i_timeout,
                           static_ruby_custom_timer_hook,
                           (void*)name );

  v_hook = Data_Wrap_Struct( static_xchat_hook_klass,
                             NULL, NULL,
                             hook );

  return v_hook;
}


static VALUE static_ruby_xchat_print( VALUE klass,
                                      VALUE text )
{
  char *s_text;

  Check_Type( text, T_STRING );

  s_text = StringValueCStr( text );

  xchat_print( static_plugin_handle, s_text );

  return Qnil;
}


static VALUE static_ruby_xchat_unhook( VALUE klass,
                                       VALUE hook_id )
{
  xchat_hook *hook;

  Data_Get_Struct( hook_id, xchat_hook, hook );

  xchat_unhook( static_plugin_handle, hook );

  return Qnil;
}


static VALUE static_ruby_xchat_command( VALUE klass,
                                        VALUE command )
{
  char *cmd;

  Check_Type( command, T_STRING );
  cmd = StringValueCStr( command );

  xchat_command( static_plugin_handle,
                 cmd );

  return Qnil;
}


static VALUE static_ruby_xchat_find_context( VALUE klass,
                                             VALUE server,
                                             VALUE channel )
{
  char *s_server = NULL;
  char *s_channel = NULL;
  xchat_context *ctx;
  VALUE v_ctx;

  if( !NIL_P( server ) ) {
    Check_Type( server, T_STRING );
    s_server = StringValueCStr( server );
  }
  if( !NIL_P( channel ) ) {
    Check_Type( channel, T_STRING );
    s_channel = StringValueCStr( channel );
  }

  ctx = xchat_find_context( static_plugin_handle,
                            s_server,
                            s_channel );

  if( ctx == NULL )
    return Qnil;

  v_ctx = Data_Wrap_Struct( static_xchat_context_klass,
                            NULL, NULL,
                            ctx );

  return v_ctx;
}


static VALUE static_ruby_xchat_get_context( VALUE klass )
{
  xchat_context *ctx;
  VALUE v_ctx;

  ctx = xchat_get_context( static_plugin_handle );

  v_ctx = Data_Wrap_Struct( static_xchat_context_klass,
                            NULL, NULL,
                            ctx );

  return v_ctx;
}


static VALUE static_ruby_xchat_get_info( VALUE klass,
                                         VALUE id )
{
  char *s_id;
  const char *s_info;

  Check_Type( id, T_STRING );
  s_id = StringValueCStr( id );

  s_info = xchat_get_info( static_plugin_handle, s_id );

  if( s_info == NULL ) return Qnil;

  return rb_str_new2( s_info );
}


static VALUE static_ruby_xchat_get_prefs( VALUE klass,
                                          VALUE name )
{
  char *s_name;
  char *s_pref;
  int   i_pref;
  int   rc;

  Check_Type( name, T_STRING );
  s_name = StringValueCStr( name );

  rc = xchat_get_prefs( static_plugin_handle,
                        s_name,
                        (const char**)&s_pref, &i_pref );

  switch( rc )
  {
    case 0: /* failed */
      return Qnil;
    case 1: /* returned a string */
      return rb_str_new2( s_pref );
    case 2: /* returned an int */
      return INT2FIX( i_pref );
    case 3: /* returned a bool */
      return ( i_pref ? Qtrue : Qfalse );
  }

  return Qnil;
}


static VALUE static_ruby_xchat_set_context( VALUE klass,
                                            VALUE ctx )
{
  xchat_context *context;
  int rc;

  Data_Get_Struct( ctx, xchat_context, context );

  rc = xchat_set_context( static_plugin_handle,
                          context );

  return INT2FIX( rc );
}


static VALUE static_ruby_xchat_nickcmp( VALUE klass,
                                        VALUE s1,
                                        VALUE s2 )
{
  char *s_s1;
  char *s_s2;

  Check_Type( s1, T_STRING );
  Check_Type( s2, T_STRING );
  s_s1 = StringValueCStr( s1 );
  s_s2 = StringValueCStr( s2 );

  return INT2FIX( xchat_nickcmp( static_plugin_handle, s_s1, s_s2 ) );
}


static VALUE static_ruby_xchat_list_get( VALUE klass,
                                         VALUE name )
{
  xchat_list *list;
  char *s_name;
  VALUE v_list;

  Check_Type( name, T_STRING );
  s_name = StringValueCStr( name );

  list = xchat_list_get( static_plugin_handle, s_name );
  if( list == NULL )
    return Qnil;

  v_list = Data_Wrap_Struct( static_xchat_list_internal_klass,
                             NULL, static_free_xchat_list,
                             list );

  return v_list;
}


static VALUE static_ruby_xchat_list_next( VALUE klass,
                                          VALUE list )
{
  xchat_list *x_list;
  int rc;

  Data_Get_Struct( list, xchat_list, x_list );
  if( x_list == NULL )
    return Qfalse;

  rc = xchat_list_next( static_plugin_handle, x_list );

  return ( rc ? Qtrue : Qfalse );
}


static VALUE static_ruby_xchat_list_str( VALUE klass,
                                         VALUE list,
                                         VALUE name )
{
  xchat_list *x_list;
  char *str;
  char *s_name;

  Check_Type( name, T_STRING );
  Data_Get_Struct( list, xchat_list, x_list );
  s_name = StringValueCStr( name );

  str = (char*)xchat_list_str( static_plugin_handle, x_list, (const char*)s_name );
  if( str == NULL )
    return Qnil;

  return rb_str_new2( str );
}


static VALUE static_ruby_xchat_list_int( VALUE klass,
                                         VALUE list,
                                         VALUE name )
{
  xchat_list *x_list;
  int rc;
  char *s_name;

  Check_Type( name, T_STRING );
  Data_Get_Struct( list, xchat_list, x_list );
  s_name = StringValueCStr( name );

  rc = xchat_list_int( static_plugin_handle, x_list, s_name );

  return INT2FIX( rc );
}

/* http://blog.evanweaver.com/files/readme.ext.txt

.\" README.EXT -  -*- Text -*- created at: Mon Aug  7 16:45:54 JST 1995

The `argc' represents the number of the arguments to the C function,
which must be less than 17.

If argc is -1, the function will be called as:

  VALUE func(int argc, VALUE *argv, VALUE obj)

where argc is the actual number of arguments, argv is the C array of
the arguments, and obj is the receiver.
*/
static VALUE static_ruby_xchat_emit_print( int    argc,
                                           VALUE *argv,
                                           VALUE  klass )
{
  char *parms[16];
  int   i;

  if( argc < 1 )
    return Qfalse;

  for( i = 0; i < 16; i++ )
  {
    if( i < argc ) parms[i] = StringValueCStr( argv[i] );
    else parms[i] = NULL;
  }

  i = xchat_emit_print( static_plugin_handle,
                        parms[ 0], parms[ 1], parms[ 2], parms[ 3],
                        parms[ 4], parms[ 5], parms[ 6], parms[ 7],
                        parms[ 8], parms[ 9], parms[10], parms[11],
                        parms[12], parms[13], parms[14], parms[15],
                        NULL );

  return ( i ? Qtrue : Qfalse );
}


static int static_ruby_custom_command_hook( char *word[],
                                            char *word_eol[],
                                            void *userdata )
{
  VALUE rb_word;
  VALUE rb_word_eol;
  VALUE rc;
  int   i;

  if(!word[0]){ return 0; }

  rb_word = rb_ary_new();
  rb_word_eol = rb_ary_new();

  for( i = 1; word[i]; i++ )
  {
    if('\0' == word[i][0]){ break; }
    rb_ary_push( rb_word, rb_str_new2( word[i] ) );
    rb_ary_push( rb_word_eol, rb_str_new2( word_eol[i] ) );
  }

  rc = rb_funcall( static_xchat_klass,
                   static_xchat_process_command_hook,
                   3,
                   rb_ary_entry( rb_word, 0 ),
                   rb_word,
                   rb_word_eol );

  return FIX2INT( rc );
}


static int static_ruby_custom_print_hook( char *word[],
                                          void *userdata )
{
  VALUE rb_name;
  VALUE rb_word;
  VALUE rc;
  int   i;

  if(!word[0]){ return 0; }

  rb_name = (VALUE)userdata;
  rb_word = rb_ary_new();

  for( i = 1; word[i]; i++ )
  {
    if('\0' == word[i][0]){ break; }
    rb_ary_push( rb_word, rb_str_new2( word[i] ) );
  }

  rc = rb_funcall( static_xchat_klass,
                   static_xchat_process_print_hook,
                   2,
                   rb_name,
                   rb_word );

  return FIX2INT( rc );
}


static int static_ruby_custom_server_hook( char *word[],
                                           char *word_eol[],
                                           void *userdata )
{
  VALUE rb_word;
  VALUE rb_word_eol;
  VALUE rc;
  int   i;

  if(!word[0]){ return 0; }

  rb_word = rb_ary_new();
  rb_word_eol = rb_ary_new();

  for( i = 1; word[i]; i++ )
  {
    if('\0' == word[i][0]){ break; }
    rb_ary_push( rb_word, rb_str_new2( word[i] ) );
    rb_ary_push( rb_word_eol, rb_str_new2( word_eol[i] ) );
  }

  rc = rb_funcall( static_xchat_klass,
                   static_xchat_process_server_hook,
                   3,
                   rb_ary_entry( rb_word, 1 ),
                   rb_word,
                   rb_word_eol );

  return FIX2INT( rc );
}


static int static_ruby_custom_timer_hook( void *userdata )
{
  VALUE rc;
  VALUE name;

  name = (VALUE)userdata;

  rc = rb_funcall( static_xchat_klass,
                   static_xchat_process_timer_hook,
                   1,
                   name );

  return FIX2INT( rc );
}


static void static_free_xchat_list( xchat_list *list )
{
  xchat_list_free( static_plugin_handle, list );
}


int xchat_plugin_init(xchat_plugin *plugin_handle,
                      char **plugin_name,
                      char **plugin_desc,
                      char **plugin_version,
                      char *arg)
{
  ph = static_plugin_handle = plugin_handle;

  static_init_xchat_environment( plugin_handle,
                                 plugin_name,
                                 plugin_desc,
                                 plugin_version );

  static_init_ruby_environment();

  xchat_print( static_plugin_handle,
               "Ruby interface loaded\n" );

  return 1;
}


int xchat_plugin_deinit()
{
  rb_funcall( static_xchat_klass,
              rb_intern( "unregister" ),
              0 );

  return 1;
}

#include<stdio.h>
#include<conio.h>
#include<stdlib.h>
 
main()
{
   FILE *fs1, *fs2, *ft;
 
   char ch, file1[20], file2[20], file3[20];
 
   printf("Enter name of first file ");
   gets(file1);
 
   printf("Enter name of second file ");
   gets(file2);
 
   printf("Enter name of file which will store contents of two files ");
   gets(file3);
 
   fs1 = fopen(file1,"r");
   fs2 = fopen(file2,"r");
 
   if( fs1 == NULL || fs2 == NULL )
   {
      perror("Error ");
      printf("Press any key to exit...\n");
      getch();
      exit(EXIT_FAILURE);
   }
 
   ft = fopen(file3,"w");
 
   if( ft == NULL )
   {
      perror("Error ");
      printf("Press any key to exit...\n");
      exit(EXIT_FAILURE);
   }
 
   while( ( ch = fgetc(fs1) ) != EOF )
      fputc(ch,ft);
 
   while( ( ch = fgetc(fs2) ) != EOF )
      fputc(ch,ft);
 
   printf("Two files were merged into %s file successfully.\n",file3);
 
   fclose(fs1);
   fclose(fs2);
   fclose(ft);
 
   getch();
   return 0;
}

#include "common.h" 
#include "c-icap.h"
#include "module.h"
#include "lookup_table.h"
#include "net_io.h"
#include "cache.h"
#include "debug.h"
#include "common.h"


int init_dnsbl_tables(struct ci_server_conf *server_conf);
void release_dnsbl_tables();

CI_DECLARE_MOD_DATA common_module_t module = {
    "dnsbl_tables",
    init_dnsbl_tables,
    NULL,
    release_dnsbl_tables,
    NULL,
};



void *dnsbl_table_open(struct ci_lookup_table *table); 
void  dnsbl_table_close(struct ci_lookup_table *table);
void *dnsbl_table_search(struct ci_lookup_table *table, void *key, void ***vals);
void  dnsbl_table_release_result(struct ci_lookup_table *table_data,void **val);

struct ci_lookup_table_type dnsbl_table_type={
    dnsbl_table_open,
    dnsbl_table_close,
    dnsbl_table_search,
    dnsbl_table_release_result,
    NULL,
    "dnsbl"
};


int init_dnsbl_tables(struct ci_server_conf *server_conf)
{
    return (ci_lookup_table_type_register(&dnsbl_table_type) != NULL);
}

void release_dnsbl_tables()
{
    ci_lookup_table_type_unregister(&dnsbl_table_type);
}

/***********************************************************/
/*  bdb_table_type inmplementation                         */

struct dnsbl_data {
    char check_domain[CI_MAXHOSTNAMELEN+1];
    ci_cache_t *cache;
};

void *dnsbl_table_open(struct ci_lookup_table *table)
{
    struct dnsbl_data *dnsbl_data;
    if (strlen(table->path) >= CI_MAXHOSTNAMELEN ) {
         ci_debug_printf(1, "dnsbl_table_open: too long domain name: %s\n",
                        table->path);
        return NULL;
    }

    if (table->key_ops != &ci_str_ops || table->val_ops!= &ci_str_ops) {
        ci_debug_printf(1, "dnsbl_table_open:  Only searching with strings and returning strings supported\n");
        return NULL;
    }

    dnsbl_data = malloc(sizeof(struct dnsbl_data));
    if (!dnsbl_data) {
        ci_debug_printf(1, "dnsbl_table_open: error allocating memory (dnsbl_data)!\n");
        return NULL;
    }
    strcpy(dnsbl_data->check_domain, table->path);
    dnsbl_data->cache = ci_cache_build(65536, CI_MAXHOSTNAMELEN+1, 0, 60, &ci_str_ops,
                                       &ci_cache_store_vector_val, /*copy_to*/
                                       &ci_cache_read_vector_val /*copy_from*/
        );

    table->data = dnsbl_data; 
    return table->data;
}

void  dnsbl_table_close(struct ci_lookup_table *table)
{
     struct dnsbl_data *dnsbl_data = table->data;
     table->data = NULL;
     ci_cache_destroy(dnsbl_data->cache);
     free(dnsbl_data);
}

static ci_vector_t  *resolv_hostname(char *hostname);
void *dnsbl_table_search(struct ci_lookup_table *table, void *key, void ***vals)
{
    char dnsname[CI_MAXHOSTNAMELEN + 1];
    char *server;
    ci_str_vector_t  *v;
    struct dnsbl_data *dnsbl_data = table->data;

    if(table->key_ops != &ci_str_ops) {
     ci_debug_printf(1,"Only keys of type string allowed in this type of table:\n");
     return NULL;
    }
    server = (char *)key;

    if (dnsbl_data->cache && ci_cache_search(dnsbl_data->cache, server, (void **)&v, table->allocator)) {
     ci_debug_printf(6,"dnsbl_table_search: cache hit for %s value %p\n", server,  v);
        if (!v) {
            *vals = NULL;
            return NULL;
        }
        *vals = (void **)ci_vector_cast_to_voidvoid(v);
        return key;
    }

    snprintf(dnsname, CI_MAXHOSTNAMELEN, "%s.%s", server, dnsbl_data->check_domain);
    dnsname[CI_MAXHOSTNAMELEN] = '\0';
    v = resolv_hostname(dnsname);
    if (dnsbl_data->cache)
        ci_cache_update(dnsbl_data->cache, server, v);
    
    if (!v)
        return NULL;

    *vals = (void **)ci_vector_cast_to_voidvoid(v);
    return key;
}

void  dnsbl_table_release_result(struct ci_lookup_table *table,void **val)
{
    ci_str_vector_t  *v = ci_vector_cast_from_voidvoid((const void **)val);
    ci_str_vector_destroy(v);
}

/**************************/
/* Utility functions               */

/*Return the list of ip address for a given  hostname*/
static ci_vector_t  *resolv_hostname(char *hostname)
{
    ci_str_vector_t  *vect = NULL;
    int ret;
    struct addrinfo hints, *res, *cur;
    ci_sockaddr_t addr;
    char buf[256];

     memset(&hints, 0, sizeof(hints));
     hints.ai_family = AF_UNSPEC;
     hints.ai_socktype = SOCK_STREAM;
     hints.ai_protocol = 0;
     if ((ret = getaddrinfo(hostname, NULL, &hints, &res)) != 0) {
      ci_debug_printf(5, "Error geting addrinfo:%s\n", gai_strerror(ret));
      return NULL;
     }

     if (res)
         vect = ci_str_vector_create(1024);

     if (vect) {
         for(cur = res; cur != NULL; cur = cur->ai_next){
             memcpy(&(addr.sockaddr), cur->ai_addr, CI_SOCKADDR_SIZE);
             ci_fill_sockaddr(&addr);
             if (ci_sockaddr_t_to_ip(&addr, buf, sizeof(buf)))
                 (void)ci_str_vector_add(vect, buf);
         }
         freeaddrinfo(res);
     }

     return vect;
}

/*
 * List Abstract Data Type
 * Copyright (C) 1997 Kaz Kylheku <kaz@ashi.footprints.net>
 *
 * Free Software License:
 *
 * All rights are reserved by the author, with the following exceptions:
 * Permission is granted to freely reproduce and distribute this software,
 * possibly in exchange for a fee, provided that this copyright notice appears
 * intact. Permission is also granted to adapt this software to produce
 * derivative works, as long as the modified versions carry this copyright
 * notice and additional notices stating that the work has been modified.
 * This source code may be translated into executable form and incorporated
 * into proprietary software; there is no requirement for such software to
 * contain a copyright notice related to this source.
 *
 * $Id: list.c,v 1.19.2.1 2000/04/17 01:07:21 kaz Exp $
 * $Name: kazlib_1_20 $
 */

/*
 * Modifications by Kostas Chatzikokolakis
 *   11/3/2005: #include <config.h>
 */

#if HAVE_CONFIG_H
#include <config.h>
#endif

#include <stdlib.h>
#include <stddef.h>
#include <assert.h>
#define LIST_IMPLEMENTATION
#include "list.h"

#define next list_next
#define prev list_prev
#define data list_data

#define pool list_pool
#define fre list_free
#define size list_size

#define nilnode list_nilnode
#define nodecount list_nodecount
#define maxcount list_maxcount

#define list_nil(L)     (&(L)->nilnode)
#define list_first_priv(L)  ((L)->nilnode.next)
#define list_last_priv(L)   ((L)->nilnode.prev)
#define lnode_next(N)       ((N)->next)
#define lnode_prev(N)       ((N)->prev)

#ifdef KAZLIB_RCSID
static const char rcsid[] = "$Id: list.c,v 1.19.2.1 2000/04/17 01:07:21 kaz Exp $";
#endif

/*
 * Initialize a list object supplied by the client such that it becomes a valid
 * empty list. If the list is to be ``unbounded'', the maxcount should be
 * specified as LISTCOUNT_T_MAX, or, alternately, as -1. The value zero
 * is not permitted.
 */

list_t *list_init(list_t *list, listcount_t maxcount)
{
    assert (maxcount != 0);
    list->nilnode.next = &list->nilnode;
    list->nilnode.prev = &list->nilnode;
    list->nodecount = 0;
    list->maxcount = maxcount;
    return list;
}

/*
 * Dynamically allocate a list object using malloc(), and initialize it so that
 * it is a valid empty list. If the list is to be ``unbounded'', the maxcount
 * should be specified as LISTCOUNT_T_MAX, or, alternately, as -1.
 */

list_t *list_create(listcount_t maxcount)
{
    list_t *new = malloc(sizeof *new);
    if (new) {
    assert (maxcount != 0);
    new->nilnode.next = &new->nilnode;
    new->nilnode.prev = &new->nilnode;
    new->nodecount = 0;
    new->maxcount = maxcount;
    }
    return new;
}

/*
 * Destroy a dynamically allocated list object.
 * The client must remove the nodes first.
 */

void list_destroy(list_t *list)
{
    assert (list_isempty(list));
    free(list);
}

/*
 * Free all of the nodes of a list. The list must contain only 
 * dynamically allocated nodes. After this call, the list
 * is empty.
 */

void list_destroy_nodes(list_t *list)
{
    lnode_t *lnode = list_first_priv(list), *nil = list_nil(list), *tmp;

    while (lnode != nil) {
    tmp = lnode->next;
    lnode->next = NULL;
    lnode->prev = NULL;
    lnode_destroy(lnode);
    lnode = tmp;
    }

    list_init(list, list->maxcount);
}

/*
 * Return all of the nodes of a list to a node pool. The nodes in
 * the list must all have come from the same pool.
 */

void list_return_nodes(list_t *list, lnodepool_t *pool)
{
    lnode_t *lnode = list_first_priv(list), *tmp, *nil = list_nil(list);

    while (lnode != nil) {
    tmp = lnode->next;
    lnode->next = NULL;
    lnode->prev = NULL;
    lnode_return(pool, lnode);
    lnode = tmp;
    }

    list_init(list, list->maxcount);
}

/*
 * Insert the node ``new'' into the list immediately after ``this'' node.
 */

void list_ins_after(list_t *list, lnode_t *new, lnode_t *this)
{
    lnode_t *that = this->next;

    assert (new != NULL);
    assert (!list_contains(list, new));
    assert (!lnode_is_in_a_list(new));
    assert (this == list_nil(list) || list_contains(list, this));
    assert (list->nodecount + 1 > list->nodecount);

    new->prev = this;
    new->next = that;
    that->prev = new;
    this->next = new;
    list->nodecount++;

    assert (list->nodecount <= list->maxcount);
}

/*
 * Insert the node ``new'' into the list immediately before ``this'' node.
 */

void list_ins_before(list_t *list, lnode_t *new, lnode_t *this)
{
    lnode_t *that = this->prev;

    assert (new != NULL);
    assert (!list_contains(list, new));
    assert (!lnode_is_in_a_list(new));
    assert (this == list_nil(list) || list_contains(list, this));
    assert (list->nodecount + 1 > list->nodecount);

    new->next = this;
    new->prev = that;
    that->next = new;
    this->prev = new;
    list->nodecount++;

    assert (list->nodecount <= list->maxcount);
}

/*
 * Delete the given node from the list.
 */

lnode_t *list_delete(list_t *list, lnode_t *del)
{
    lnode_t *next = del->next;
    lnode_t *prev = del->prev;

    assert (list_contains(list, del));

    prev->next = next;
    next->prev = prev;
    list->nodecount--;

    del->next = del->prev = NULL;

    return del;
}

/*
 * For each node in the list, execute the given function. The list,
 * current node and the given context pointer are passed on each
 * call to the function.
 */

void list_process(list_t *list, void *context,
    void (* function)(list_t *list, lnode_t *lnode, void *context))
{
    lnode_t *node = list_first_priv(list), *next, *nil = list_nil(list);

    while (node != nil) {
    /* check for callback function deleting */
    /* the next node from under us      */
    assert (list_contains(list, node));
    next = node->next;
    function(list, node, context);
    node = next;
    }
}

/*
 * Dynamically allocate a list node and assign it the given piece of data.
 */

lnode_t *lnode_create(void *data)
{
    lnode_t *new = malloc(sizeof *new);
    if (new) {
    new->data = data;
    new->next = NULL;
    new->prev = NULL;
    }
    return new;
}

/*
 * Initialize a user-supplied lnode.
 */

lnode_t *lnode_init(lnode_t *lnode, void *data)
{
    lnode->data = data;
    lnode->next = NULL;
    lnode->prev = NULL;
    return lnode;
}

/*
 * Destroy a dynamically allocated node.
 */

void lnode_destroy(lnode_t *lnode)
{
    assert (!lnode_is_in_a_list(lnode));
    free(lnode);
}

/*
 * Initialize a node pool object to use a user-supplied set of nodes.
 * The ``nodes'' pointer refers to an array of lnode_t objects, containing
 * ``n'' elements.
 */

lnodepool_t *lnode_pool_init(lnodepool_t *pool, lnode_t *nodes, listcount_t n)
{
    listcount_t i;

    assert (n != 0);

    pool->pool = nodes;
    pool->fre = nodes;
    pool->size = n;
    for (i = 0; i < n - 1; i++) {
    nodes[i].next = nodes + i + 1;
    }
    nodes[i].next = NULL;
    nodes[i].prev = nodes;  /* to make sure node is marked ``on list'' */
    return pool;
}

/*
 * Create a dynamically allocated pool of n nodes.
 */

lnodepool_t *lnode_pool_create(listcount_t n)
{
    lnodepool_t *pool;
    lnode_t *nodes;

    assert (n != 0);

    pool = malloc(sizeof *pool);
    if (!pool)
    return NULL;
    nodes = malloc(n * sizeof *nodes);
    if (!nodes) {
    free(pool);
    return NULL;
    }
    lnode_pool_init(pool, nodes, n);
    return pool;
}

/*
 * Determine whether the given pool is from this pool.
 */

int lnode_pool_isfrom(lnodepool_t *pool, lnode_t *node)
{
    listcount_t i;

    /* this is carefully coded this way because ANSI C forbids pointers
       to different objects from being subtracted or compared other
       than for exact equality */

    for (i = 0; i < pool->size; i++) {
    if (pool->pool + i == node)
        return 1;
    }
    return 0;
}

/*
 * Destroy a dynamically allocated pool of nodes.
 */

void lnode_pool_destroy(lnodepool_t *p)
{
    free(p->pool);
    free(p);
}

/*
 * Borrow a node from a node pool. Returns a null pointer if the pool
 * is exhausted. 
 */

lnode_t *lnode_borrow(lnodepool_t *pool, void *data)
{
    lnode_t *new = pool->fre;
    if (new) {
    pool->fre = new->next;
    new->data = data;
    new->next = NULL;
    new->prev = NULL;
    }
    return new;
}

/*
 * Return a node to a node pool. A node must be returned to the pool
 * from which it came.
 */

void lnode_return(lnodepool_t *pool, lnode_t *node)
{
    assert (lnode_pool_isfrom(pool, node));
    assert (!lnode_is_in_a_list(node));

    node->next = pool->fre;
    node->prev = node;
    pool->fre = node;
}

/*
 * Determine whether the given list contains the given node.
 * According to this function, a list does not contain its nilnode.
 */

int list_contains(list_t *list, lnode_t *node)
{
    lnode_t *n, *nil = list_nil(list);

    for (n = list_first_priv(list); n != nil; n = lnode_next(n)) {
    if (node == n)
        return 1;
    }

    return 0;
}

/*
 * A more generalized variant of list_transfer. This one removes a
 * ``slice'' from the source list and appends it to the destination
 * list.
 */

void list_extract(list_t *dest, list_t *source, lnode_t *first, lnode_t *last)
{
    listcount_t moved = 1;

    assert (first == NULL || list_contains(source, first));
    assert (last == NULL || list_contains(source, last));

    if (first == NULL || last == NULL)
    return;

    /* adjust the destination list so that the slice is spliced out */

    first->prev->next = last->next;
    last->next->prev = first->prev;

    /* graft the splice at the end of the dest list */

    last->next = &dest->nilnode;
    first->prev = dest->nilnode.prev;
    dest->nilnode.prev->next = first;
    dest->nilnode.prev = last;

    while (first != last) {
    first = first->next;
    assert (first != list_nil(source)); /* oops, last before first! */
    moved++;
    }
    
    /* assert no overflows */
    assert (source->nodecount - moved <= source->nodecount);
    assert (dest->nodecount + moved >= dest->nodecount);

    /* assert no weirdness */
    assert (moved <= source->nodecount);

    source->nodecount -= moved;
    dest->nodecount += moved;

    /* assert list sanity */
    assert (list_verify(source));
    assert (list_verify(dest));
}


/*
 * Split off a trailing sequence of nodes from the source list and relocate
 * them to the tail of the destination list. The trailing sequence begins
 * with node ``first'' and terminates with the last node of the source
 * list. The nodes are added to the end of the new list in their original
 * order.
 */

void list_transfer(list_t *dest, list_t *source, lnode_t *first)
{
    listcount_t moved = 1;
    lnode_t *last;

    assert (first == NULL || list_contains(source, first));

    if (first == NULL)
    return;

    last = source->nilnode.prev;

    source->nilnode.prev = first->prev;
    first->prev->next = &source->nilnode;

    last->next = &dest->nilnode;
    first->prev = dest->nilnode.prev;
    dest->nilnode.prev->next = first;
    dest->nilnode.prev = last;

    while (first != last) {
    first = first->next;
    moved++;
    }
    
    /* assert no overflows */
    assert (source->nodecount - moved <= source->nodecount);
    assert (dest->nodecount + moved >= dest->nodecount);

    /* assert no weirdness */
    assert (moved <= source->nodecount);

    source->nodecount -= moved;
    dest->nodecount += moved;

    /* assert list sanity */
    assert (list_verify(source));
    assert (list_verify(dest));
}

void list_merge(list_t *dest, list_t *sour,
    int compare (const void *, const void *))
{
    lnode_t *dn, *sn, *tn;
    lnode_t *d_nil = list_nil(dest), *s_nil = list_nil(sour);

    /* Nothing to do if source and destination list are the same. */
    if (dest == sour)
    return;

    /* overflow check */
    assert (list_count(sour) + list_count(dest) >= list_count(sour));

    /* lists must be sorted */
    assert (list_is_sorted(sour, compare));
    assert (list_is_sorted(dest, compare));

    dn = list_first_priv(dest);
    sn = list_first_priv(sour);

    while (dn != d_nil && sn != s_nil) {
    if (compare(lnode_get(dn), lnode_get(sn)) >= 0) {
        tn = lnode_next(sn);
        list_delete(sour, sn);
        list_ins_before(dest, sn, dn);
        sn = tn;
    } else {
        dn = lnode_next(dn);
    }
    }

    if (dn != d_nil)
    return;

    if (sn != s_nil)
    list_transfer(dest, sour, sn);
}

void list_sort(list_t *list, int compare(const void *, const void *))
{
    list_t extra;
    listcount_t middle;
    lnode_t *node;

    if (list_count(list) > 1) {
    middle = list_count(list) / 2;
    node = list_first_priv(list);

    list_init(&extra, list_count(list) - middle);

    while (middle--)
        node = lnode_next(node);
    
    list_transfer(&extra, list, node);
    list_sort(list, compare);
    list_sort(&extra, compare);
    list_merge(list, &extra, compare);
    } 
    assert (list_is_sorted(list, compare));
}

lnode_t *list_find(list_t *list, const void *key, int compare(const void *, const void *))
{
    lnode_t *node;

    for (node = list_first_priv(list); node != list_nil(list); node = node->next) {
    if (compare(lnode_get(node), key) == 0)
        return node;
    }
    
    return 0;
}


/*
 * Return 1 if the list is in sorted order, 0 otherwise
 */

int list_is_sorted(list_t *list, int compare(const void *, const void *))
{
    lnode_t *node, *next, *nil;

    next = nil = list_nil(list);
    node = list_first_priv(list);

    if (node != nil)
    next = lnode_next(node);

    for (; next != nil; node = next, next = lnode_next(next)) {
    if (compare(lnode_get(node), lnode_get(next)) > 0)
        return 0;
    }

    return 1;
}

/*
 * Get rid of macro functions definitions so they don't interfere
 * with the actual definitions
 */

#undef list_isempty
#undef list_isfull
#undef lnode_pool_isempty
#undef list_append
#undef list_prepend
#undef list_first
#undef list_last
#undef list_next
#undef list_prev
#undef list_count
#undef list_del_first
#undef list_del_last
#undef lnode_put
#undef lnode_get

/*
 * Return 1 if the list is empty, 0 otherwise
 */

int list_isempty(list_t *list)
{
    return list->nodecount == 0;
}

/*
 * Return 1 if the list is full, 0 otherwise
 * Permitted only on bounded lists. 
 */

int list_isfull(list_t *list)
{
    return list->nodecount == list->maxcount;
}

/*
 * Check if the node pool is empty.
 */

int lnode_pool_isempty(lnodepool_t *pool)
{
    return (pool->fre == NULL);
}

/*
 * Add the given node at the end of the list
 */

void list_append(list_t *list, lnode_t *node)
{
    list_ins_before(list, node, &list->nilnode);
}

/*
 * Add the given node at the beginning of the list.
 */

void list_prepend(list_t *list, lnode_t *node)
{
    list_ins_after(list, node, &list->nilnode);
}

/*
 * Retrieve the first node of the list
 */

lnode_t *list_first(list_t *list)
{
    if (list->nilnode.next == &list->nilnode)
    return NULL;
    return list->nilnode.next;
}

/*
 * Retrieve the last node of the list
 */

lnode_t *list_last(list_t *list)
{
    if (list->nilnode.prev == &list->nilnode)
    return NULL;
    return list->nilnode.prev;
}

/*
 * Retrieve the count of nodes in the list
 */

listcount_t list_count(list_t *list)
{
    return list->nodecount;
}

/*
 * Remove the first node from the list and return it.
 */

lnode_t *list_del_first(list_t *list)
{
    return list_delete(list, list->nilnode.next);
}

/*
 * Remove the last node from the list and return it.
 */

lnode_t *list_del_last(list_t *list)
{
    return list_delete(list, list->nilnode.prev);
}


/*
 * Associate a data item with the given node.
 */

void lnode_put(lnode_t *lnode, void *data)
{
    lnode->data = data;
}

/*
 * Retrieve the data item associated with the node.
 */

void *lnode_get(lnode_t *lnode)
{
    return lnode->data;
}

/*
 * Retrieve the node's successor. If there is no successor, 
 * NULL is returned.
 */

lnode_t *list_next(list_t *list, lnode_t *lnode)
{
    assert (list_contains(list, lnode));

    if (lnode->next == list_nil(list))
    return NULL;
    return lnode->next;
}

/*
 * Retrieve the node's predecessor. See comment for lnode_next().
 */

lnode_t *list_prev(list_t *list, lnode_t *lnode)
{
    assert (list_contains(list, lnode));

    if (lnode->prev == list_nil(list))
    return NULL;
    return lnode->prev;
}

/*
 * Return 1 if the lnode is in some list, otherwise return 0.
 */

int lnode_is_in_a_list(lnode_t *lnode)
{
    return (lnode->next != NULL || lnode->prev != NULL);
}


int list_verify(list_t *list)
{
    lnode_t *node = list_first_priv(list), *nil = list_nil(list);
    listcount_t count = list_count(list);

    if (node->prev != nil)
    return 0;

    if (count > list->maxcount)
    return 0;

    while (node != nil && count--) {
    if (node->next->prev != node)
        return 0;
    node = node->next;
    }

    if (count != 0 || node != nil)
    return 0;
    
    return 1;
}

#ifdef KAZLIB_TEST_MAIN

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>

typedef char input_t[256];

static int tokenize(char *string, ...)
{
    char **tokptr; 
    va_list arglist;
    int tokcount = 0;

    va_start(arglist, string);
    tokptr = va_arg(arglist, char **);
    while (tokptr) {
    while (*string && isspace((unsigned char) *string))
        string++;
    if (!*string)
        break;
    *tokptr = string;
    while (*string && !isspace((unsigned char) *string))
        string++;
    tokptr = va_arg(arglist, char **);
    tokcount++;
    if (!*string)
        break;
    *string++ = 0;
    }
    va_end(arglist);

    return tokcount;
}

static int comparef(const void *key1, const void *key2)
{
    return strcmp(key1, key2);
}

static char *dupstring(char *str)
{
    int sz = strlen(str) + 1;
    char *new = malloc(sz);
    if (new)
    memcpy(new, str, sz);
    return new;
}

int main(void)
{
    input_t in;
    list_t *l = list_create(LISTCOUNT_T_MAX);
    lnode_t *ln;
    char *tok1, *val;
    int prompt = 0;

    char *help =
    "a <val>                append value to list\n"
    "d <val>                delete value from list\n"
    "l <val>                lookup value in list\n"
    "s                      sort list\n"
    "c                      show number of entries\n"
    "t                      dump whole list\n"
    "p                      turn prompt on\n"
    "q                      quit";

    if (!l)
    puts("list_create failed");

    for (;;) {
    if (prompt)
        putchar('>');
    fflush(stdout);

    if (!fgets(in, sizeof(input_t), stdin))
        break;

    switch(in[0]) {
        case '?':
        puts(help);
        break;
        case 'a':
        if (tokenize(in+1, &tok1, (char **) 0) != 1) {
            puts("what?");
            break;
        }
        val = dupstring(tok1);
        ln = lnode_create(val);
    
        if (!val || !ln) {
            puts("allocation failure");
            if (ln)
            lnode_destroy(ln);
            free(val);
            break;
        }
    
        list_append(l, ln);
        break;
        case 'd':
        if (tokenize(in+1, &tok1, (char **) 0) != 1) {
            puts("what?");
            break;
        }
        ln = list_find(l, tok1, comparef);
        if (!ln) {
            puts("list_find failed");
            break;
        }
        list_delete(l, ln);
        val = lnode_get(ln);
        lnode_destroy(ln);
        free(val);
        break;
        case 'l':
        if (tokenize(in+1, &tok1, (char **) 0) != 1) {
            puts("what?");
            break;
        }
        ln = list_find(l, tok1, comparef);
        if (!ln)
            puts("list_find failed");
        else
            puts("found");
        break;
        case 's':
        list_sort(l, comparef);
        break;
        case 'c':
        printf("%lu\n", (unsigned long) list_count(l));
        break;
        case 't':
        for (ln = list_first(l); ln != 0; ln = list_next(l, ln))
            puts(lnode_get(ln));
        break;
        case 'q':
        exit(0);
        break;
        case '\0':
        break;
        case 'p':
        prompt = 1;
        break;
        default:
        putchar('?');
        putchar('\n');
        break;
    }
    }

    return 0;
}

#endif  /* defined TEST_MAIN */

/*
 * Hash Table Data Type vi:ts=4:sw=4:expandtab:
 * Copyright (C) 1997 Kaz Kylheku <kaz@ashi.footprints.net>
 *
 * Free Software License:
 *
 * All rights are reserved by the author, with the following exceptions:
 * Permission is granted to freely reproduce and distribute this software,
 * possibly in exchange for a fee, provided that this copyright notice appears
 * intact. Permission is also granted to adapt this software to produce
 * derivative works, as long as the modified versions carry this copyright
 * notice and additional notices stating that the work has been modified.
 * This source code may be translated into executable form and incorporated
 * into proprietary software; there is no requirement for such software to
 * contain a copyright notice related to this source.
 *
 * $Id: hash.c,v 1.36.2.11 2000/11/13 01:36:45 kaz Exp $
 * $Name: kazlib_1_20 $
 */

#include <stdlib.h>
#include <stddef.h>
#include <assert.h>
#include <string.h>
#define HASH_IMPLEMENTATION
#include "hash.h"

#ifdef KAZLIB_RCSID
static const char rcsid[] = "$Id: hash.c,v 1.36.2.11 2000/11/13 01:36:45 kaz Exp $";
#endif

#define INIT_BITS   6
#define INIT_SIZE   (1UL << (INIT_BITS))    /* must be power of two     */
#define INIT_MASK   ((INIT_SIZE) - 1)

#define next hash_next
#define key hash_key
#define data hash_data
#define hkey hash_hkey

#define table hash_table
#define nchains hash_nchains
#define nodecount hash_nodecount
#define maxcount hash_maxcount
#define highmark hash_highmark
#define lowmark hash_lowmark
#define compare hash_compare
#define function hash_function
#define allocnode hash_allocnode
#define freenode hash_freenode
#define context hash_context
#define mask hash_mask
#define dynamic hash_dynamic

#define table hash_table
#define chain hash_chain

static hnode_t *hnode_alloc(void *context);
static void hnode_free(hnode_t *node, void *context);
static hash_val_t hash_fun_default(const void *key);
static int hash_comp_default(const void *key1, const void *key2);

static int hash_val_t_bit;

/*
 * Compute the number of bits in the hash_val_t type.  We know that hash_val_t
 * is an unsigned integral type. Thus the highest value it can hold is a
 * Mersenne number (power of two, less one). We initialize a hash_val_t
 * object with this value and then shift bits out one by one while counting.
 * Notes:
 * 1. HASH_VAL_T_MAX is a Mersenne number---one that is one less than a power
 *    of two. This means that its binary representation consists of all one
 *    bits, and hence ``val'' is initialized to all one bits.
 * 2. While bits remain in val, we increment the bit count and shift it to the
 *    right, replacing the topmost bit by zero.
 */

static void compute_bits(void)
{
    hash_val_t val = HASH_VAL_T_MAX;    /* 1 */
    int bits = 0;

    while (val) {   /* 2 */
    bits++;
    val >>= 1;
    }

    hash_val_t_bit = bits;
}

/*
 * Verify whether the given argument is a power of two.
 */

static int is_power_of_two(hash_val_t arg)
{
    if (arg == 0)
    return 0;
    while ((arg & 1) == 0)
    arg >>= 1;
    return (arg == 1);
}

/*
 * Compute a shift amount from a given table size 
 */

static hash_val_t compute_mask(hashcount_t size)
{
    assert (is_power_of_two(size));
    assert (size >= 2);

    return size - 1;
}

/*
 * Initialize the table of pointers to null.
 */

static void clear_table(hash_t *hash)
{
    hash_val_t i;

    for (i = 0; i < hash->nchains; i++)
    hash->table[i] = NULL;
}

/*
 * Double the size of a dynamic table. This works as follows. Each chain splits
 * into two adjacent chains.  The shift amount increases by one, exposing an
 * additional bit of each hashed key. For each node in the original chain, the
 * value of this newly exposed bit will decide which of the two new chains will
 * receive the node: if the bit is 1, the chain with the higher index will have
 * the node, otherwise the lower chain will receive the node. In this manner,
 * the hash table will continue to function exactly as before without having to
 * rehash any of the keys.
 * Notes:
 * 1.  Overflow check.
 * 2.  The new number of chains is twice the old number of chains.
 * 3.  The new mask is one bit wider than the previous, revealing a
 *     new bit in all hashed keys.
 * 4.  Allocate a new table of chain pointers that is twice as large as the
 *     previous one.
 * 5.  If the reallocation was successful, we perform the rest of the growth
 *     algorithm, otherwise we do nothing.
 * 6.  The exposed_bit variable holds a mask with which each hashed key can be
 *     AND-ed to test the value of its newly exposed bit.
 * 7.  Now loop over each chain in the table and sort its nodes into two
 *     chains based on the value of each node's newly exposed hash bit.
 * 8.  The low chain replaces the current chain.  The high chain goes
 *     into the corresponding sister chain in the upper half of the table.
 * 9.  We have finished dealing with the chains and nodes. We now update
 *     the various bookeeping fields of the hash structure.
 */

static void grow_table(hash_t *hash)
{
    hnode_t **newtable;

    assert (2 * hash->nchains > hash->nchains); /* 1 */

    newtable = realloc(hash->table,
        sizeof *newtable * hash->nchains * 2);  /* 4 */

    if (newtable) { /* 5 */
    hash_val_t mask = (hash->mask << 1) | 1;    /* 3 */
    hash_val_t exposed_bit = mask ^ hash->mask; /* 6 */
    hash_val_t chain;

    assert (mask != hash->mask);

    for (chain = 0; chain < hash->nchains; chain++) { /* 7 */
        hnode_t *low_chain = 0, *high_chain = 0, *hptr, *next;

        for (hptr = newtable[chain]; hptr != 0; hptr = next) {
        next = hptr->next;

        if (hptr->hkey & exposed_bit) {
            hptr->next = high_chain;
            high_chain = hptr;
        } else {
            hptr->next = low_chain;
            low_chain = hptr;
        }
        }

        newtable[chain] = low_chain;    /* 8 */
        newtable[chain + hash->nchains] = high_chain;
    }

    hash->table = newtable;         /* 9 */
    hash->mask = mask;
    hash->nchains *= 2;
    hash->lowmark *= 2;
    hash->highmark *= 2;
    }
    assert (hash_verify(hash));
}

/*
 * Cut a table size in half. This is done by folding together adjacent chains
 * and populating the lower half of the table with these chains. The chains are
 * simply spliced together. Once this is done, the whole table is reallocated
 * to a smaller object.
 * Notes:
 * 1.  It is illegal to have a hash table with one slot. This would mean that
 *     hash->shift is equal to hash_val_t_bit, an illegal shift value.
 *     Also, other things could go wrong, such as hash->lowmark becoming zero.
 * 2.  Looping over each pair of sister chains, the low_chain is set to
 *     point to the head node of the chain in the lower half of the table, 
 *     and high_chain points to the head node of the sister in the upper half.
 * 3.  The intent here is to compute a pointer to the last node of the
 *     lower chain into the low_tail variable. If this chain is empty,
 *     low_tail ends up with a null value.
 * 4.  If the lower chain is not empty, we simply tack the upper chain onto it.
 *     If the upper chain is a null pointer, nothing happens.
 * 5.  Otherwise if the lower chain is empty but the upper one is not,
 *     If the low chain is empty, but the high chain is not, then the
 *     high chain is simply transferred to the lower half of the table.
 * 6.  Otherwise if both chains are empty, there is nothing to do.
 * 7.  All the chain pointers are in the lower half of the table now, so
 *     we reallocate it to a smaller object. This, of course, invalidates
 *     all pointer-to-pointers which reference into the table from the
 *     first node of each chain.
 * 8.  Though it's unlikely, the reallocation may fail. In this case we
 *     pretend that the table _was_ reallocated to a smaller object.
 * 9.  Finally, update the various table parameters to reflect the new size.
 */

static void shrink_table(hash_t *hash)
{
    hash_val_t chain, nchains;
    hnode_t **newtable, *low_tail, *low_chain, *high_chain;

    assert (hash->nchains >= 2);            /* 1 */
    nchains = hash->nchains / 2;

    for (chain = 0; chain < nchains; chain++) {
    low_chain = hash->table[chain];     /* 2 */
    high_chain = hash->table[chain + nchains];
    for (low_tail = low_chain; low_tail && low_tail->next; low_tail = low_tail->next)
        ;   /* 3 */
    if (low_chain != 0)             /* 4 */
        low_tail->next = high_chain;
    else if (high_chain != 0)           /* 5 */
        hash->table[chain] = high_chain;
    else
        assert (hash->table[chain] == NULL);    /* 6 */
    }
    newtable = realloc(hash->table,
        sizeof *newtable * nchains);        /* 7 */
    if (newtable)                   /* 8 */
    hash->table = newtable;
    hash->mask >>= 1;           /* 9 */
    hash->nchains = nchains;
    hash->lowmark /= 2;
    hash->highmark /= 2;
    assert (hash_verify(hash));
}


/*
 * Create a dynamic hash table. Both the hash table structure and the table
 * itself are dynamically allocated. Furthermore, the table is extendible in
 * that it will automatically grow as its load factor increases beyond a
 * certain threshold.
 * Notes:
 * 1. If the number of bits in the hash_val_t type has not been computed yet,
 *    we do so here, because this is likely to be the first function that the
 *    user calls.
 * 2. Allocate a hash table control structure.
 * 3. If a hash table control structure is successfully allocated, we
 *    proceed to initialize it. Otherwise we return a null pointer.
 * 4. We try to allocate the table of hash chains.
 * 5. If we were able to allocate the hash chain table, we can finish
 *    initializing the hash structure and the table. Otherwise, we must
 *    backtrack by freeing the hash structure.
 * 6. INIT_SIZE should be a power of two. The high and low marks are always set
 *    to be twice the table size and half the table size respectively. When the
 *    number of nodes in the table grows beyond the high size (beyond load
 *    factor 2), it will double in size to cut the load factor down to about
 *    about 1. If the table shrinks down to or beneath load factor 0.5,
 *    it will shrink, bringing the load up to about 1. However, the table
 *    will never shrink beneath INIT_SIZE even if it's emptied.
 * 7. This indicates that the table is dynamically allocated and dynamically
 *    resized on the fly. A table that has this value set to zero is
 *    assumed to be statically allocated and will not be resized.
 * 8. The table of chains must be properly reset to all null pointers.
 */

hash_t *hash_create(hashcount_t maxcount, hash_comp_t compfun,
    hash_fun_t hashfun)
{
    hash_t *hash;

    if (hash_val_t_bit == 0)    /* 1 */
    compute_bits();

    hash = malloc(sizeof *hash);    /* 2 */

    if (hash) {     /* 3 */
    hash->table = malloc(sizeof *hash->table * INIT_SIZE);  /* 4 */
    if (hash->table) {  /* 5 */
        hash->nchains = INIT_SIZE;      /* 6 */
        hash->highmark = INIT_SIZE * 2;
        hash->lowmark = INIT_SIZE / 2;
        hash->nodecount = 0;
        hash->maxcount = maxcount;
        hash->compare = compfun ? compfun : hash_comp_default;
        hash->function = hashfun ? hashfun : hash_fun_default;
        hash->allocnode = hnode_alloc;
        hash->freenode = hnode_free;
        hash->context = NULL;
        hash->mask = INIT_MASK;
        hash->dynamic = 1;          /* 7 */
        clear_table(hash);          /* 8 */
        assert (hash_verify(hash));
        return hash;
    } 
    free(hash);
    }

    return NULL;
}

/*
 * Select a different set of node allocator routines.
 */

void hash_set_allocator(hash_t *hash, hnode_alloc_t al,
    hnode_free_t fr, void *context)
{
    assert (hash_count(hash) == 0);
    assert ((al == 0 && fr == 0) || (al != 0 && fr != 0));

    hash->allocnode = al ? al : hnode_alloc;
    hash->freenode = fr ? fr : hnode_free;
    hash->context = context;
}

/*
 * Free every node in the hash using the hash->freenode() function pointer, and
 * cause the hash to become empty.
 */

void hash_free_nodes(hash_t *hash)
{
    hscan_t hs;
    hnode_t *node;
    hash_scan_begin(&hs, hash);
    while ((node = hash_scan_next(&hs))) {
    hash_scan_delete(hash, node);
    hash->freenode(node, hash->context);
    }
    hash->nodecount = 0;
    clear_table(hash);
}

/*
 * Obsolescent function for removing all nodes from a table,
 * freeing them and then freeing the table all in one step.
 */

void hash_free(hash_t *hash)
{
#ifdef KAZLIB_OBSOLESCENT_DEBUG
    assert ("call to obsolescent function hash_free()" && 0);
#endif
    hash_free_nodes(hash);
    hash_destroy(hash);
}

/*
 * Free a dynamic hash table structure.
 */

void hash_destroy(hash_t *hash)
{
    assert (hash_val_t_bit != 0);
    assert (hash_isempty(hash));
    free(hash->table);
    free(hash);
}

/*
 * Initialize a user supplied hash structure. The user also supplies a table of
 * chains which is assigned to the hash structure. The table is static---it
 * will not grow or shrink.
 * 1. See note 1. in hash_create().
 * 2. The user supplied array of pointers hopefully contains nchains nodes.
 * 3. See note 7. in hash_create().
 * 4. We must dynamically compute the mask from the given power of two table
 *    size. 
 * 5. The user supplied table can't be assumed to contain null pointers,
 *    so we reset it here.
 */

hash_t *hash_init(hash_t *hash, hashcount_t maxcount,
    hash_comp_t compfun, hash_fun_t hashfun, hnode_t **table,
    hashcount_t nchains)
{
    if (hash_val_t_bit == 0)    /* 1 */
    compute_bits();

    assert (is_power_of_two(nchains));

    hash->table = table;    /* 2 */
    hash->nchains = nchains;
    hash->nodecount = 0;
    hash->maxcount = maxcount;
    hash->compare = compfun ? compfun : hash_comp_default;
    hash->function = hashfun ? hashfun : hash_fun_default;
    hash->dynamic = 0;      /* 3 */
    hash->mask = compute_mask(nchains); /* 4 */
    clear_table(hash);      /* 5 */

    assert (hash_verify(hash));

    return hash;
}

/*
 * Reset the hash scanner so that the next element retrieved by
 * hash_scan_next() shall be the first element on the first non-empty chain. 
 * Notes:
 * 1. Locate the first non empty chain.
 * 2. If an empty chain is found, remember which one it is and set the next
 *    pointer to refer to its first element.
 * 3. Otherwise if a chain is not found, set the next pointer to NULL
 *    so that hash_scan_next() shall indicate failure.
 */

void hash_scan_begin(hscan_t *scan, hash_t *hash)
{
    hash_val_t nchains = hash->nchains;
    hash_val_t chain;

    scan->table = hash;

    /* 1 */

    for (chain = 0; chain < nchains && hash->table[chain] == 0; chain++)
    ;

    if (chain < nchains) {  /* 2 */
    scan->chain = chain;
    scan->next = hash->table[chain];
    } else {            /* 3 */
    scan->next = NULL;
    }
}

/*
 * Retrieve the next node from the hash table, and update the pointer
 * for the next invocation of hash_scan_next(). 
 * Notes:
 * 1. Remember the next pointer in a temporary value so that it can be
 *    returned.
 * 2. This assertion essentially checks whether the module has been properly
 *    initialized. The first point of interaction with the module should be
 *    either hash_create() or hash_init(), both of which set hash_val_t_bit to
 *    a non zero value.
 * 3. If the next pointer we are returning is not NULL, then the user is
 *    allowed to call hash_scan_next() again. We prepare the new next pointer
 *    for that call right now. That way the user is allowed to delete the node
 *    we are about to return, since we will no longer be needing it to locate
 *    the next node.
 * 4. If there is a next node in the chain (next->next), then that becomes the
 *    new next node, otherwise ...
 * 5. We have exhausted the current chain, and must locate the next subsequent
 *    non-empty chain in the table.
 * 6. If a non-empty chain is found, the first element of that chain becomes
 *    the new next node. Otherwise there is no new next node and we set the
 *    pointer to NULL so that the next time hash_scan_next() is called, a null
 *    pointer shall be immediately returned.
 */


hnode_t *hash_scan_next(hscan_t *scan)
{
    hnode_t *next = scan->next;     /* 1 */
    hash_t *hash = scan->table;
    hash_val_t chain = scan->chain + 1;
    hash_val_t nchains = hash->nchains;

    assert (hash_val_t_bit != 0);   /* 2 */

    if (next) {         /* 3 */
    if (next->next) {   /* 4 */
        scan->next = next->next;
    } else {
        while (chain < nchains && hash->table[chain] == 0)  /* 5 */
            chain++;
        if (chain < nchains) {  /* 6 */
        scan->chain = chain;
        scan->next = hash->table[chain];
        } else {
        scan->next = NULL;
        }
    }
    }
    return next;
}

/*
 * Insert a node into the hash table.
 * Notes:
 * 1. It's illegal to insert more than the maximum number of nodes. The client
 *    should verify that the hash table is not full before attempting an
 *    insertion.
 * 2. The same key may not be inserted into a table twice.
 * 3. If the table is dynamic and the load factor is already at >= 2,
 *    grow the table.
 * 4. We take the bottom N bits of the hash value to derive the chain index,
 *    where N is the base 2 logarithm of the size of the hash table. 
 */

void hash_insert(hash_t *hash, hnode_t *node, const void *key)
{
    hash_val_t hkey, chain;

    assert (hash_val_t_bit != 0);
    assert (node->next == NULL);
    assert (hash->nodecount < hash->maxcount);  /* 1 */
    assert (hash_lookup(hash, key) == NULL);    /* 2 */

    if (hash->dynamic && hash->nodecount >= hash->highmark) /* 3 */
    grow_table(hash);

    hkey = hash->function(key);
    chain = hkey & hash->mask;  /* 4 */

    node->key = key;
    node->hkey = hkey;
    node->next = hash->table[chain];
    hash->table[chain] = node;
    hash->nodecount++;

    assert (hash_verify(hash));
}

/*
 * Find a node in the hash table and return a pointer to it.
 * Notes:
 * 1. We hash the key and keep the entire hash value. As an optimization, when
 *    we descend down the chain, we can compare hash values first and only if
 *    hash values match do we perform a full key comparison. 
 * 2. To locate the chain from among 2^N chains, we look at the lower N bits of
 *    the hash value by anding them with the current mask.
 * 3. Looping through the chain, we compare the stored hash value inside each
 *    node against our computed hash. If they match, then we do a full
 *    comparison between the unhashed keys. If these match, we have located the
 *    entry.
 */

hnode_t *hash_lookup(hash_t *hash, const void *key)
{
    hash_val_t hkey, chain;
    hnode_t *nptr;

    hkey = hash->function(key);     /* 1 */
    chain = hkey & hash->mask;      /* 2 */

    for (nptr = hash->table[chain]; nptr; nptr = nptr->next) {  /* 3 */
    if (nptr->hkey == hkey && hash->compare(nptr->key, key) == 0)
        return nptr;
    }

    return NULL;
}

/*
 * Delete the given node from the hash table.  Since the chains
 * are singly linked, we must locate the start of the node's chain
 * and traverse.
 * Notes:
 * 1. The node must belong to this hash table, and its key must not have
 *    been tampered with.
 * 2. If this deletion will take the node count below the low mark, we
 *    shrink the table now. 
 * 3. Determine which chain the node belongs to, and fetch the pointer
 *    to the first node in this chain.
 * 4. If the node being deleted is the first node in the chain, then
 *    simply update the chain head pointer.
 * 5. Otherwise advance to the node's predecessor, and splice out
 *    by updating the predecessor's next pointer.
 * 6. Indicate that the node is no longer in a hash table.
 */

hnode_t *tr_hash_delete(hash_t *hash, hnode_t *node)
{
    hash_val_t chain;
    hnode_t *hptr;

    assert (hash_lookup(hash, node->key) == node);  /* 1 */
    assert (hash_val_t_bit != 0);

    if (hash->dynamic && hash->nodecount <= hash->lowmark
        && hash->nodecount > INIT_SIZE)
    shrink_table(hash);             /* 2 */

    chain = node->hkey & hash->mask;            /* 3 */
    hptr = hash->table[chain];

    if (hptr == node) {                 /* 4 */
    hash->table[chain] = node->next;
    } else {
    while (hptr->next != node) {            /* 5 */
        assert (hptr != 0);
        hptr = hptr->next;
    }
    assert (hptr->next == node);
    hptr->next = node->next;
    }
    
    hash->nodecount--;
    assert (hash_verify(hash));

    node->next = NULL;                  /* 6 */
    return node;
}

int hash_alloc_insert(hash_t *hash, const void *key, void *data)
{
    hnode_t *node = hash->allocnode(hash->context);

    if (node) {
    hnode_init(node, data);
    hash_insert(hash, node, key);
    return 1;
    }
    return 0;
}

void hash_delete_free(hash_t *hash, hnode_t *node)
{
    tr_hash_delete(hash, node);
    hash->freenode(node, hash->context);
}
