# Movable Type (r) Open Source (C) 2001-2012 Six Apart, Ltd.
# This program is distributed under the terms of the
# GNU General Public License, version 2.
#
# $Id$

package MT::Builder;

use strict;
use base qw( MT::ErrorHandler );
use MT::Template::Node;
use MT::Template::Handler;

sub NODE () {'MT::Template::Node'}

sub new { bless {}, $_[0] }

sub compile {
    my $build = shift;
    my ( $ctx, $text, $opt ) = @_;
    my $tmpl;

    $opt ||= { uncompiled => 1 };
    my $depth = $opt->{depth} ||= 0;

    my $ids;
    my $classes;
    my $errors;
    $build->{__state}{errors} = [] unless $depth;
    $errors = $build->{__state}{errors};

    # handle $builder->compile($template) signature
    if ( UNIVERSAL::isa( $ctx, 'MT::Template' ) ) {
        $tmpl = $ctx;
        $ctx  = $tmpl->context;
        $text = $tmpl->text;
        $tmpl->reset_tokens();
        $ids     = $build->{__state}{ids}     = {};
        $classes = $build->{__state}{classes} = {};
        $build->{__state}{tmpl} = $tmpl;
    }
    else {
        $ids     = $build->{__state}{ids}     || {};
        $classes = $build->{__state}{classes} || {};
        $tmpl    = $build->{__state}{tmpl};
    }

    return [] unless defined $text;
    if ( $depth <= 0 && $text && Encode::is_utf8($text) ) {
        Encode::_utf8_off($text);
    }

    my $mods;

    # Translate any HTML::Template markup into native MT syntax.
    if (   $depth <= 0
        && $text
        =~ m/<(?:MT_TRANS\b|MT_ACTION\b|(?:tmpl_(?:if|loop|unless|else|var|include)))/i
        )
    {
        translate_html_tmpl($text);
    }

    my $state = $build->{__state};
    local $state->{tokens}  = [];
    local $state->{classes} = $classes;
    local $state->{tmpl}    = $tmpl;
    local $state->{ids}     = $ids;
    local $state->{text}    = \$text;

    my $pos = 0;
    my $len = length $text;

    # MT tag syntax: <MTFoo>, <$MTFoo$>, <$MTFoo>
    #                <MT:Foo>, <$MT:Foo>, <$MT:Foo$>
    #                <MTFoo:Bar>, <$MTFoo:Bar>, <$MTFoo:Bar$>
    # For 'function' tags, the '$' characters are optional
    # For namespace, the ':' is optional for the default 'MT' namespace.
    # Other namespaces (like 'Foo') would require the colon.
    # Tag and attributes are case-insensitive. So you can write:
    #   <mtfoo>...</MTFOO>
    while ( $text
        =~ m!(<\$?(MT:?)((?:<[^>]+?>|"(?:<[^>]+?>|.)*?"|'(?:<[^>]+?>|.)*?'|.)+?)([-]?)[\$/]?>)!gis
        )
    {
        my ( $whole_tag, $prefix, $tag, $space_eater ) = ( $1, $2, $3, $4 );
        ( $tag, my ($args) ) = split /\s+/, $tag, 2;
        my $sec_start = pos $text;
        my $tag_start = $sec_start - length $whole_tag;
        _text_block( $state, $pos, $tag_start ) if $pos < $tag_start;
        $state->{space_eater} = $space_eater;
        $args ||= '';

        # Structure of a node:
        #   tag name, attribute hashref, contained tokens, template text,
        #       attributes arrayref, parent array reference
        my $rec = NODE->new(
            tag            => $tag,
            attributes     => \my %args,
            attribute_list => \my @args
        );
        while (
            $args =~ /
            (?:
                (?:
                    ((?:\w|:)+)                     #1
                    \s*=\s*
                    (?:(?:
                        (["'])                      #2
                        ((?:<[^>]+?>|.)*?)          #3
                        \2
                        (                           #4
                            (?:
                                [,:]
                                (["'])              #5
                                (?:(?:<[^>]+?>|.)*?)
                                \5
                            )+
                        )?
                    ) |
                    (\S+))                          #6
                )
            ) |
            (\w+)                                   #7
            /gsx
            )
        {
            if ( defined $7 ) {

                # An unnamed attribute gets stored in the 'name' argument.
                $args{'name'} = $7;
            }
            else {
                my $attr  = lc $1;
                my $value = defined $6 ? $6 : $3;
                my $extra = $4;
                if ( defined $extra ) {
                    my @extra;
                    push @extra, $2
                        while $extra =~ m/[,:](["'])((?:<[^>]+?>|.)*?)\1/gs;
                    $value = [ $value, @extra ];
                }

                # We need a reference to the filters to check
                # attributes and whether they need to be in the array of
                # attributes for post-processing.
                $mods ||= $ctx->{__filters};
                push @args, [ $attr, $value ] if exists $mods->{$attr};
                $args{$attr} = $value;
                if ( $attr eq 'id' ) {

                    # store a reference to this token based on the 'id' for it
                    $ids->{$3} = $rec;
                }
                elsif ( $attr eq 'class' ) {

                    # store a reference to this token based on the 'id' for it
                    $classes->{ lc $3 } ||= [];
                    push @{ $classes->{ lc $3 } }, $rec;
                }
            }
        }
        my $hdlr = $ctx->handler_for($tag);
        my ( $h, $is_container );
        if ($hdlr) {
            ( $h, $is_container ) = $hdlr->values;
        }
        if ( !$h ) {

            # determine line #
            my $pre_error = substr( $text, 0, $tag_start );
            my @m = $pre_error =~ m/\r?\n/g;
            my $line = scalar @m;
            if ($depth) {
                $opt->{error_line} = $line;
                push @$errors,
                    {
                    message => MT->translate(
                        "<[_1]> at line [_2] is unrecognized.",
                        $prefix . $tag, "#"
                    ),
                    line => $line + 1
                    };
            }
            else {
                push @$errors,
                    {
                    message => MT->translate(
                        "<[_1]> at line [_2] is unrecognized.",
                        $prefix . $tag,
                        $line + 1
                    ),
                    line => $line
                    };
            }
        }
        if ($is_container) {
            if ( $whole_tag !~ m|/>$| ) {
                my ( $sec_end, $tag_end )
                    = _consume_up_to( \$text, $sec_start, $tag );
                if ($sec_end) {
                    my $sec = $tag =~ m/ignore/i
                        ? ''    # ignore MTIgnore blocks
                        : substr $text, $sec_start, $sec_end - $sec_start;
                    if ( $sec !~ m/<\$?MT/i ) {
                        $rec->childNodes(
                            [   (   $sec ne ''
                                    ? NODE->new(
                                        tag       => 'TEXT',
                                        nodeValue => $sec
                                        )
                                    : ()
                                )
                            ]
                        );
                    }
                    else {
                        local $opt->{depth}  = $opt->{depth} + 1;
                        local $opt->{parent} = $rec;
                        $rec->childNodes(
                            $build->compile( $ctx, $sec, $opt ) );
                        if (@$errors) {
                            my $pre_error = substr( $text, 0, $sec_start );
                            my @m = $pre_error =~ m/\r?\n/g;
                            my $line = scalar @m;
                            foreach (@$errors) {
                                $line += $_->{line};
                                $_->{line} = $line;
                                $_->{message} =~ s/#/$line/ unless $depth;
                            }
                        }

             # unless (defined $rec->[2]) {
             #     my $pre_error = substr($text, 0, $sec_start);
             #     my @m = $pre_error =~ m/\r?\n/g;
             #     my $line = scalar @m;
             #     if ($depth) {
             #         $opt->{error_line} = $line + ($opt->{error_line} || 0);
             #         return;
             #     }
             #     else {
             #         $line += ($opt->{error_line} || 0) + 1;
             #         my $err = $build->errstr;
             #         $err =~ s/#/$line/;
             #         return $build->error($err);
             #     }
             # }
                    }
                    $rec->nodeValue($sec) if $opt->{uncompiled};
                }
                else {
                    my $pre_error = substr( $text, 0, $tag_start );
                    my @m = $pre_error =~ m/\r?\n/g;
                    my $line = scalar @m;
                    if ($depth) {

# $opt->{error_line} = $line;
# return $build->error(MT->translate("<[_1]> with no </[_1]> on line #", $prefix . $tag));
                        push @$errors,
                            {
                            message => MT->translate(
                                "<[_1]> with no </[_1]> on line [_2].",
                                $prefix . $tag, "#"
                            ),
                            line => $line
                            };
                    }
                    else {
                        push @$errors,
                            {
                            message => MT->translate(
                                "<[_1]> with no </[_1]> on line [_2].",
                                $prefix . $tag,
                                $line + 1
                            ),
                            line => $line + 1
                            };

# return $build->error(MT->translate("<[_1]> with no </[_1]> on line [_2]", $prefix . $tag, $line + 1));
                    }
                    last;    # return undef;
                }
                $pos = $tag_end + 1;
                ( pos $text ) = $tag_end;
            }
            else {
                $rec->nodeValue('');
            }
        }
        $rec->parentNode( $opt->{parent} || $tmpl );
        $rec->template($tmpl);
        push @{ $state->{tokens} }, $rec;
        $pos = pos $text;
    }
    _text_block( $state, $pos, $len ) if $pos < $len;
    if ( defined $tmpl ) {

        # assign token and id references to template
        $tmpl->tokens( $state->{tokens} );
        $tmpl->token_ids( $state->{ids} );
        $tmpl->token_classes( $state->{classes} );
        $tmpl->errors( $state->{errors} )
            if $state->{errors} && ( @{ $state->{errors} } );
    }
    else {
        if ( $errors && @$errors ) {
            return $build->error( $errors->[0]->{message} );
        }
    }

    if ( $depth <= 0 ) {
        for my $t ( @{ $state->{tokens} } ) {
            $t->upgrade;
        }
        Encode::_utf8_on($text)
            if !Encode::is_utf8($text);
    }
    return $state->{tokens};
}

sub translate_html_tmpl {
    $_[0] =~ s!<(/?)tmpl_(if|loop|unless|else|var|include)\b!<$1mt:$2!ig;
    $_[0] =~ s!<MT_TRANS\b!<__trans!ig;
    $_[0] =~ s!<MT_ACTION\b!<__action!ig;
}

sub _consume_up_to {
    my ( $text, $start, $stoptag ) = @_;
    my $pos;
    ( pos $$text ) = $start;
    while ( $$text =~ m!(<([\$/]?)MT:?([^\s\$>]+)(?:[^>]*?)[\$/]?>)!gi ) {
        my ( $whole_tag, $prefix, $tag ) = ( $1, $2, $3 );
        next if lc $tag ne lc $stoptag;
        my $end = pos $$text;
        if ( $prefix && ( $prefix eq '/' ) ) {
            return ( $end - length($whole_tag), $end );
        }
        elsif ( $whole_tag !~ m|/>| ) {
            my ( $sec_end, $end_tag ) = _consume_up_to( $text, $end, $tag );
            last if !$sec_end;
            ( pos $$text ) = $end_tag;
        }
    }

    # special case for unclosed 'else' tag:
    if ( lc($stoptag) eq 'else' || lc($stoptag) eq 'elseif' ) {
        return ( $start + length($$text), $start + length($$text) );
    }
    return ( 0, 0 );
}

sub _text_block {
    my $text = substr ${ $_[0]->{text} }, $_[1], $_[2] - $_[1];
    if ( ( defined $text ) && ( $text ne '' ) ) {
        return if $_[0]->{space_eater} && ( $text =~ m/^\s+$/s );
        $text =~ s/^\s+//s if $_[0]->{space_eater};
        my $rec = NODE->new(
            tag        => 'TEXT',
            nodeValue  => $text,
            parentNode => $_[0]->{tokens},
            template   => $_[0]->{tmpl}
        );
        push @{ $_[0]->{tokens} }, $rec;
    }
}

sub syntree2str {
    my ( $tokens, $depth ) = @_;
    my $string = '';
    foreach my $t (@$tokens) {
        my ( $name, $args, $tokens, $uncompiled )
            = ( $t->tag, $t->attributes, $t->childNodes, $t->nodeValue );
        $string .= ( " " x $depth ) . $name;
        if ( ref $args eq 'HASH' ) {
            $string .= join( ", ",
                ( map { " $_ => " . $args->{$_} } ( keys %$args ) ) );
        }

        $string .= "\n";
        $string .= syntree2str( $tokens, $depth + 2 );
    }
    return $string;
}

sub build {
    my $build = shift;
    my ( $ctx, $tokens, $cond ) = @_;

    my $timer;
    if ( $MT::DebugMode & 8 ) {
        $timer = MT->get_timer();
    }

    if ($cond) {
        my %lcond;

        # lowercase condtional keys since we're storing tags in lowercase now
        # When both the lowercase key and the CamelCase key exist,
        # the value will be overwrited in the CamelCase key's value.
        $lcond{ lc $_ } = $cond->{$_} for reverse sort keys %$cond;
        $cond = \%lcond;
    }
    else {
        $cond = {};
    }

    # Avoids circular reference between MT::Template::Context and MT::Builder.
    local $ctx->{__stash}{builder} = $build;
    my $res = '';
    my $ph  = $ctx->post_process_handler;

    for my $t (@$tokens) {
        if ( $t->tag eq 'TEXT' ) {
            $res .= $t->nodeValue;
        }
        else {
            my ( $tokens, $tokens_else, $uncompiled );
            my $tag = lc $t->tag;
            if ( $cond && ( exists $cond->{$tag} && !$cond->{$tag} ) ) {

                # if there's a cond for this tag and it's false,
                # walk the children and look for an MTElse.
                # the children of the MTElse will become $tokens
                for my $tok ( @{ $t->childNodes } ) {
                    my $tag = lc $tok->tag;
                    if ( $tag eq 'else' || $tag eq 'elseif' ) {
                        $tokens     = $tok->childNodes;
                        $uncompiled = $tok->nodeValue;
                        last;
                    }
                }
                next unless $tokens;
            }
            else {
                my $childNodes = $t->childNodes;
                if ( $childNodes && ref($childNodes) ) {

                    # either there is no cond for this tag, or it's true,
                    # so we want to partition the children into
                    # those which are inside an else and those which are not.
                    ( $tokens, $tokens_else ) = ( [], [] );
                    for my $sub (@$childNodes) {
                        my $tag = lc $sub->tag;
                        if ( $tag eq 'else' || $tag eq 'elseif' ) {
                            push @$tokens_else, $sub;
                        }
                        else {
                            push @$tokens, $sub;
                        }
                    }
                }
                $uncompiled = $t->nodeValue;
            }
            my $hdlr = $ctx->handler_for( $t->tag );
            my ( $h, $type, $orig ) = $hdlr->values;
            my $conditional = defined $type && $type == 2;

            if ($h) {
                $timer->pause_partial if $timer;
                local ( $ctx->{__stash}{tag} ) = $t->tag;
                local ( $ctx->{__stash}{tokens} )
                    = ref($tokens)
                    ? bless $tokens, 'MT::Template::Tokens'
                    : undef;
                local ( $ctx->{__stash}{tokens_else} )
                    = ref($tokens_else)
                    ? bless $tokens_else, 'MT::Template::Tokens'
                    : undef;
                local ( $ctx->{__stash}{uncompiled} ) = $uncompiled;
                my %args = %{ $t->attributes } if defined $t->attributes;
                my @args = @{ $t->attribute_list }
                    if defined $t->attribute_list;

                # process variables
                foreach my $v ( keys %args ) {
                    if ( ref $args{$v} eq 'ARRAY' ) {
                        my @array = @{ $args{$v} };
                        foreach (@array) {
                            if (m/^\$([A-Za-z_](\w|\.)*)$/) {
                                $_ = $ctx->var($1);
                            }
                        }
                        $args{$v} = \@array;
                    }
                    else {
                        if ( $args{$v} =~ m/^\$([A-Za-z_](\w|\.)*)$/ ) {
                            $args{$v} = $ctx->var($1);
                        }
                    }
                }
                foreach (@args) {
                    $_ = [ $_->[0], $_->[1] ];
                    my $arg = $_;
                    if ( ref $arg->[1] eq 'ARRAY' ) {
                        $arg->[1] = [ @{ $arg->[1] } ];
                        foreach ( @{ $arg->[1] } ) {
                            if (m/^\$([A-Za-z_](\w|\.)*)$/) {
                                $_ = $ctx->var($1);
                            }
                        }
                    }
                    else {
                        if ( $arg->[1] =~ m/^\$([A-Za-z_](\w|\.)*)$/ ) {
                            $arg->[1] = $ctx->var($1);
                        }
                    }
                }

                # Stores a reference to the ordered list of arguments,
                # just in case the handler wants them
                local $args{'@'} = \@args;

                my $vars = $ctx->{__stash}{vars};
                local $vars->{__cond_value__} = $vars->{__cond_value__}
                    if $conditional;
                local $vars->{__cond_name__} = $vars->{__cond_name__}
                    if $conditional;

                my $out = $hdlr->invoke( $ctx, \%args, $cond );

                unless ( defined $out ) {
                    my $err = $ctx->errstr;
                    if ( defined $err ) {
                        return $build->error(
                            MT->translate(
                                "Error in <mt[_1]> tag: [_2]", $t->tag,
                                $ctx->errstr
                            )
                        );
                    }
                    else {

                        # no error was given, so undef will mean '' in
                        # such a scenario
                        $out = '';
                    }
                }

                if ($conditional) {

                    # conditional; process result
                    $out
                        = $out
                        ? $ctx->slurp( \%args, $cond )
                        : $ctx->else( \%args, $cond );
                    delete $vars->{__cond_tag__};
                    return $build->error(
                        MT->translate(
                            "Error in <mt[_1]> tag: [_2]", $t->tag,
                            $ctx->errstr
                        )
                    ) unless defined $out;
                }

                $out = $ph->( $ctx, \%args, $out, \@args )
                    if %args && $ph;
                $res .= $out
                    if defined $out;

                if ($timer) {
                    $timer->mark(
                        "tag_" . lc( $t->tag ) . args_to_string( \%args ) );
                }
            }
            else {
                if ( $t->tag !~ m/^_/ ) {    # placeholder tag. just ignore
                    return $build->error(
                        MT->translate( "Unknown tag found: [_1]", $t->tag ) );
                }
            }
        }
    }

    return $res;
}

sub args_to_string {
    my ($args) = @_;
    my $str = '';
    foreach my $a ( keys %$args ) {
        next if $a eq '@';
        next unless defined $args->{$a};
        next if $args->{$a} eq '';
        $str .= ';' . $a . ':';
        if ( ref $args->{$a} eq 'ARRAY' ) {
            foreach my $aa ( @{ $args->{$a} } ) {
                $aa = '...' if $aa =~ m/ /;
                $str .= $aa . ';';
            }
            chop($str);
        }
        else {
            $str .= $args->{$a} =~ m/ / ? '...' : $args->{$a};
        }
    }
    my $more_args = $args->{'@'};
    if ( $more_args && @$more_args ) {
        foreach my $a (@$more_args) {
            if ( ref $a->[1] eq 'ARRAY' ) {
                $str .= ' ' . $a->[0] . '=';
                foreach my $aa ( @{ $a->[1] } ) {
                    $aa = '...' if $aa =~ m/ /;
                    $str .= $aa . ';';
                }
                chop($str);
            }
            else {
                next
                    if exists $args->{ $a->[0] }
                        && ( $args->{ $a->[0] } eq $a->[1] );
                $str .= ';' . $a->[0] . ':';
                $str .= $a->[1];
            }
        }
    }
    return $str ne '' ? '[' . substr( $str, 1 ) . ']' : '';
}
1;
__END__

=head1 NAME

MT::Builder - Parser and interpreter for MT templates

=head1 SYNOPSIS

    use MT::Builder;
    use MT::Template::Context;

    my $build = MT::Builder->new;
    my $ctx = MT::Template::Context->new;

    my $tokens = $build->compile($ctx, '<$MTVersion$>')
        or die $build->errstr;
    defined(my $out = $build->build($ctx, $tokens))
        or die $build->errstr;

=head1 DESCRIPTION

I<MT::Builder> provides the parser and interpreter for taking a template
body and turning it into a generated output page. An I<MT::Builder> object
knows how to parse a string of text into tokens, then take those tokens and
build a scalar string representing the output of the page. It does not,
however, know anything about the types of tags that it encounters; it hands
off this work to the I<MT::Template::Context> object, which can look up a
tag and determine whether it's valid, whether it's a container or substitution
tag, etc.

All I<MT::Builder> knows is the basic structure of a Movable Type tag, and
how to break up a string into pieces: plain text pieces interspersed with
tag callouts. It then knows how to take a list of these tokens/pieces and
build a completed page, using the same I<MT::Template::Context> object to
actually fill in the values for the Movable Type tags.

=head1 USAGE

=head2 MT::Builder->new

Constructs and returns a new parser/interpreter object.

=head2 $build->compile($ctx, $string)

Given an I<MT::Template::Context> object I<$ctx>, breaks up the scalar string
I<$string> into tokens and returns the list of tokens as a reference to an
array. Returns C<undef> on compilation failure.

=head2 $build->build($ctx, \@tokens [, \%cond ])

Given an I<MT::Template::Context> object I<$ctx>, turns a list of tokens
I<\@tokens> and generates an output page. Returns the output page on success,
C<undef> on failure. Note that the empty string (C<''>) and the number zero
(C<0>) are both valid return values for this method, so you should check
specifically for an undefined value when checking for errors.

The optional argument I<\%cond> specifies a list of conditions under which
the tokens will be interpreted. If provided, I<\%cond> should be a reference
to a hash, where the keys are MT tag names (without the leading C<MT>), and
the values are boolean flags specifying whether to include the tag; a true
value means that the tag should be included in the final output, a false value
that it should not. This is useful when a template includes conditional
container tags (eg C<E<lt>MTEntryIfExtendedE<gt>>), and you wish to influence
the inclusion of these container tags. For example, if a template contains
the container

    <MTEntryIfExtended>
    <$MTEntryMore$>
    </MTEntryIfExtended>

and you wish to exclude this conditional, you could call I<build> like this:

    my $out = $build->build($ctx, $tokens, { EntryIfExtended => 0 });

=head2 $build->syntree2str(\@tokens)

Internal debugging routine to dump a set of template tokens. Returns a
readable string of contents of the C<$tokens> parameter.

=head1 ERROR HANDLING

On an error, the above methods return C<undef>, and the error message can
be obtained by calling the method I<errstr> on the object. For example:

    defined(my $out = $build->build($ctx, $tokens))
        or die $build->errstr;

=head1 AUTHOR & COPYRIGHTS

Please see the I<MT> manpage for author, copyright, and license information.

=cut

###
# XML::SAX::Writer - SAX2 XML Writer
# Robin Berjon <robin@knowscape.com>
###

package XML::SAX::Writer;
use strict;
use vars qw($VERSION %DEFAULT_ESCAPE %COMMENT_ESCAPE);
$VERSION = '0.53';

use Encode                  qw();
use XML::SAX::Exception     qw();
use XML::SAX::Writer::XML   qw();
use XML::Filter::BufferText qw();
@XML::SAX::Writer::Exception::ISA = qw(XML::SAX::Exception);


%DEFAULT_ESCAPE = (
                    '&'     => '&amp;',
                    '<'     => '&lt;',
                    '>'     => '&gt;',
                    '"'     => '&quot;',
                    "'"     => '&apos;',
                  );

%COMMENT_ESCAPE = (
                    '--'    => '&#45;&#45;',
                  );


#-------------------------------------------------------------------#
# new
#-------------------------------------------------------------------#
sub new {
    my $class = ref($_[0]) ? ref(shift) : shift;
    my $opt   = (@_ == 1)  ? { %{shift()} } : {@_};

    # default the options
    $opt->{Writer}          ||= 'XML::SAX::Writer::XML';
    $opt->{Escape}          ||= \%DEFAULT_ESCAPE;
    $opt->{CommentEscape}   ||= \%COMMENT_ESCAPE;
    $opt->{EncodeFrom}      ||= 'utf-8';
    $opt->{EncodeTo}        ||= 'utf-8';
    $opt->{Format}          ||= {}; # needs options w/ defaults, we'll see later
    $opt->{Output}          ||= *{STDOUT}{IO};
    $opt->{QuoteCharacter}  ||= q['];
    
    eval "use $opt->{Writer};";

    my $obj = bless $opt, $opt->{Writer};
    $obj->init;

    # we need to buffer the text to escape it right
    my $bf = XML::Filter::BufferText->new( Handler => $obj );

    return $bf;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# init
#-------------------------------------------------------------------#
sub init {} # noop, for subclasses
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# setConverter
#-------------------------------------------------------------------#
sub setConverter {
    my $self = shift;

    if (lc($self->{EncodeFrom}) ne lc($self->{EncodeTo})) {
        $self->{Encoder} = XML::SAX::Writer::Encode->new($self->{EncodeFrom}, $self->{EncodeTo});
    }
    else {
        $self->{Encoder} = XML::SAX::Writer::NullConverter->new;
    }
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# setConsumer
#-------------------------------------------------------------------#
sub setConsumer {
    my $self = shift;

    # create the Consumer
    my $ref = ref $self->{Output};
    if ($ref eq 'SCALAR') {
        $self->{Consumer} = XML::SAX::Writer::StringConsumer->new($self->{Output});
    }
    elsif ($ref eq 'CODE') {
        $self->{Consumer} = XML::SAX::Writer::CodeConsumer->new($self->{Output});
    }
    elsif ($ref eq 'ARRAY') {
        $self->{Consumer} = XML::SAX::Writer::ArrayConsumer->new($self->{Output});
    }
    elsif (
            $ref eq 'GLOB'                                or
            UNIVERSAL::isa(\$self->{Output}, 'GLOB')      or
            UNIVERSAL::isa($self->{Output}, 'IO::Handle')) {
        $self->{Consumer} = XML::SAX::Writer::HandleConsumer->new($self->{Output});
    }
    elsif (not $ref) {
        $self->{Consumer} = XML::SAX::Writer::FileConsumer->new($self->{Output});
    }
    elsif (UNIVERSAL::can($self->{Output}, 'output')) {
        $self->{Consumer} = $self->{Output};
    }
    else {
        XML::SAX::Writer::Exception->throw( Message => 'Unknown option for Output' );
    }
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# setEscaperRegex
#-------------------------------------------------------------------#
sub setEscaperRegex {
    my $self = shift;

    $self->{EscaperRegex} = eval 'qr/'                                                .
                            join( '|', map { $_ = "\Q$_\E" } keys %{$self->{Escape}}) .
                            '/;'                                                  ;
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# setCommentEscaperRegex
#-------------------------------------------------------------------#
sub setCommentEscaperRegex {
    my $self = shift;

    $self->{CommentEscaperRegex} =
                        eval 'qr/'                                                .
                        join( '|', map { $_ = "\Q$_\E" } keys %{$self->{CommentEscape}}) .
                        '/;'                                                  ;
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# escape
#-------------------------------------------------------------------#
sub escape {
    my $self = shift;
    my $str  = shift;

    $str =~ s/($self->{EscaperRegex})/$self->{Escape}->{$1}/oge;
    return $str;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# escapeComment
#-------------------------------------------------------------------#
sub escapeComment {
    my $self = shift;
    my $str  = shift;

    $str =~ s/($self->{CommentEscaperRegex})/$self->{CommentEscape}->{$1}/oge;
    return $str;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# convert and checking the return value
#-------------------------------------------------------------------#
sub safeConvert {
    my $self = shift;
    my $str = shift;

    my $out = $self->{Encoder}->convert($str);
    
    if (!defined $out and defined $str) {
    warn "Conversion error returned by Encoder [$self->{Encoder}], string: '$str'";
    $out = '_LOST_DATA_';
    }
    return $out;
}
#-------------------------------------------------------------------#


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, The Empty Consumer ,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

# this package is only there to provide a smooth upgrade path in case
# new methods are added to the interface

package XML::SAX::Writer::ConsumerInterface;

sub new {
    my $class = shift;
    my $ref = shift;
    ## $self is a reference to the reference that we will send output
    ## to.  This allows us to bless $self without blessing $$self.
    return bless \$ref, ref $class || $class;
}

sub output {}
sub finalize {}


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, The String Consumer `,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::StringConsumer;
@XML::SAX::Writer::StringConsumer::ISA = qw(XML::SAX::Writer::ConsumerInterface);

#-------------------------------------------------------------------#
# new
#-------------------------------------------------------------------#
sub new {
    my $self = shift->SUPER::new( @_ );
    ${${$self}} = '';
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# output
#-------------------------------------------------------------------#
sub output { ${${$_[0]}} .= $_[1] }
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# finalize
#-------------------------------------------------------------------#
sub finalize { ${$_[0]} }
#-------------------------------------------------------------------#

#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, The Code Consumer `,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::CodeConsumer;
@XML::SAX::Writer::CodeConsumer::ISA = qw(XML::SAX::Writer::ConsumerInterface );

#-------------------------------------------------------------------#
# new
#-------------------------------------------------------------------#
sub new {
    my $self = shift->SUPER::new( @_ );
    $$self->( 'start_document', '' );
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# output
#-------------------------------------------------------------------#
sub output { ${$_[0]}->('data', pop) } ## Avoid an extra copy
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# finalize
#-------------------------------------------------------------------#
sub finalize { ${$_[0]}->('end_document', '') }
#-------------------------------------------------------------------#


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, The Array Consumer ,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::ArrayConsumer;
@XML::SAX::Writer::ArrayConsumer::ISA = qw(XML::SAX::Writer::ConsumerInterface);

#-------------------------------------------------------------------#
# new
#-------------------------------------------------------------------#
sub new {
    my $self = shift->SUPER::new( @_ );
    @$$self = ();
    return $self;
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# output
#-------------------------------------------------------------------#
sub output { push @${$_[0]}, pop }
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# finalize
#-------------------------------------------------------------------#
sub finalize { return ${$_[0]} }
#-------------------------------------------------------------------#


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, The Handle Consumer `,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::HandleConsumer;
@XML::SAX::Writer::HandleConsumer::ISA = qw(XML::SAX::Writer::ConsumerInterface);

#-------------------------------------------------------------------#
# output
#-------------------------------------------------------------------#
sub output {
    my $fh = ${$_[0]};
    print $fh pop or XML::SAX::Exception->throw(
        Message => "Could not write to handle: $fh ($!)"
    );
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# finalize
#-------------------------------------------------------------------#
sub finalize { return 0 }
#-------------------------------------------------------------------#


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, The File Consumer `,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::FileConsumer;
@XML::SAX::Writer::FileConsumer::ISA = qw(XML::SAX::Writer::HandleConsumer);

#-------------------------------------------------------------------#
# new
#-------------------------------------------------------------------#
sub new {
    my ( $proto, $file ) = ( shift, shift );

    XML::SAX::Writer::Exception->throw(
        Message => "No filename provided to " . ref( $proto || $proto )
    ) unless defined $file;

    local *XFH;

    open XFH, ">$file" or XML::SAX::Writer::Exception->throw(
        Message => "Error opening file $file: $!"
    );

    return $proto->SUPER::new( *{XFH}{IO}, @_ );
}
#-------------------------------------------------------------------#

#-------------------------------------------------------------------#
# finalize
#-------------------------------------------------------------------#
sub finalize {
    close ${$_[0]};
    return 0;
}
#-------------------------------------------------------------------#


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, Noop Converter ,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::NullConverter;
sub new     { return bless [], __PACKAGE__ }
sub convert { $_[1] }


#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, Encode Converter ,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

package XML::SAX::Writer::Encode;
sub new {
    my $class = shift;
    my $self = {
        from_enc => shift,
        to_enc => shift,
    };
    return bless $self, $class;
}
sub convert {
    my $self = shift;
    my $data = shift;
    eval {
        Encode::from_to( $data, $self->{from_enc}, $self->{to_enc}, Encode::FB_CROAK );
    };
    return $@ ? undef : $data;
};


1;
__END__
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,#
#`,`, Documentation `,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,`,#
#```````````````````````````````````````````````````````````````````#

=pod

=head1 NAME

XML::SAX::Writer - SAX2 Writer

=head1 SYNOPSIS

  use XML::SAX::Writer;
  use XML::SAX::SomeDriver;

  my $w = XML::SAX::Writer->new;
  my $d = XML::SAX::SomeDriver->new(Handler => $w);

  $d->parse('some options...');

=head1 DESCRIPTION


=head2 Why yet another XML Writer ?

A new XML Writer was needed to match the SAX2 effort because quite
naturally no existing writer understood SAX2. My first intention had
been to start patching XML::Handler::YAWriter as it had previously
been my favourite writer in the SAX1 world.

However the more I patched it the more I realised that what I thought
was going to be a simple patch (mostly adding a few event handlers and
changing the attribute syntax) was turning out to be a rewrite due to
various ideas I'd been collecting along the way. Besides, I couldn't
find a way to elegantly make it work with SAX2 without breaking the
SAX1 compatibility which people are probably still using. There are of
course ways to do that, but most require user interaction which is
something I wanted to avoid.

So in the end there was a new writer. I think it's in fact better this
way as it helps keep SAX1 and SAX2 separated.

=head1 METHODS

=over 4

=item * new(%hash)

This is the constructor for this object. It takes a number of
parameters, all of which are optional.

=item -- Output

This parameter can be one of several things. If it is a simple
scalar, it is interpreted as a filename which will be opened for
writing. If it is a scalar reference, output will be appended to this
scalar. If it is an array reference, output will be pushed onto this
array as it is generated. If it is a filehandle, then output will be
sent to this filehandle.

Finally, it is possible to pass an object for this parameter, in which
case it is assumed to be an object that implements the consumer
interface L<described later in the documentation|/THE CONSUMER
INTERFACE>.

If this parameter is not provided, then output is sent to STDOUT.

=item -- Escape

This should be a hash reference where the keys are characters
sequences that should be escaped and the values are the escaped form
of the sequence. By default, this module will escape the ampersand
(&), less than (<), greater than (>), double quote ("), and apostrophe
('). Note that some browsers don't support the &apos; escape used for
apostrophes so that you should be careful when outputting XHTML.

If you only want to add entries to the Escape hash, you can first
copy the contents of %XML::SAX::Writer::DEFAULT_ESCAPE.

=item -- CommentEscape

Comment content often needs to be escaped differently from other
content. This option works exactly as the previous one except that
by default it only escapes the double dash (--) and that the contents
can be copied from %XML::SAX::Writer::COMMENT_ESCAPE.

=item -- EncodeFrom

The character set encoding in which incoming data will be provided.
This defaults to UTF-8, which works for US-ASCII as well.

=item -- EncodeTo

The character set encoding in which output should be encoded. Again,
this defaults to UTF-8.

=item -- QuoteCharacter

Set the character used to quote attributes. This defaults to single quotes (') 
for backwards compatiblity.

=back

=head1 THE CONSUMER INTERFACE

XML::SAX::Writer can receive pluggable consumer objects that will be
in charge of writing out what is formatted by this module. Setting a
Consumer is done by setting the Output option to the object of your
choice instead of to an array, scalar, or file handle as is more
commonly done (internally those in fact map to Consumer classes and
and simply available as options for your convienience).

If you don't understand this, don't worry. You don't need it most of
the time.

That object can be from any class, but must have two methods in its
API. It is also strongly recommended that it inherits from
XML::SAX::Writer::ConsumerInterface so that it will not break if that
interface evolves over time. There are examples at the end of
XML::SAX::Writer's code.

The two methods that it needs to implement are:

=over 4

=item * output STRING

(Required)

This is called whenever the Writer wants to output a string formatted
in XML. Encoding conversion, character escaping, and formatting have
already taken place. It's up to the consumer to do whatever it wants
with the string.

=item * finalize()

(Optional)

This is called once the document has been output in its entirety,
during the end_document event. end_document will in fact return
whatever finalize() returns, and that in turn should be returned
by parse() for whatever parser was invoked. It might be useful if
you need to provide feedback of some sort.

=back

Here's an example of a custom consumer.  Note the extra C<$> signs in
front of $self; the base class is optimized for the overwhelmingly
common case where only one data member is required and $self is a
reference to that data member.

    package MyConsumer;

    @ISA = qw( XML::SAX::Writer::ConsumerInterface );

    use strict;

    sub new {
        my $self = shift->SUPER::new( my $output );

        $$self = '';      # Note the extra '$'

        return $self;
    }

    sub output {
        my $self = shift;
        $$self .= uc shift;
    }

    sub get_output {
        my $self = shift;
        return $$self;
    }

And here's one way to use it:

    my $c = MyConsumer->new;
    my $w = XML::SAX::Writer->new( Output => $c );

    ## ... send events to $w ...

    print $c->get_output;

If you need to store more that one data member, pass in an array or hash
reference:

        my $self = shift->SUPER::new( {} );

and access it like:

    sub output {
        my $self = shift;
        $$self->{Output} .= uc shift;
    }

=head1 THE ENCODER INTERFACE

Encoders can be plugged in to allow one to use one's favourite encoder
object. Presently there are two encoders: Encode and NullEncoder. They
need to implement two methods, and may inherit from
XML::SAX::Writer::NullConverter if they wish to

=over 4

=item new FROM_ENCODING, TO_ENCODING

Creates a new Encoder. The arguments are the chosen encodings.

=item convert STRING

Converts that string and returns it.

=back

Note that the return value of the convert method is B<not> checked. Output may
be truncated if a character couldn't be converted correctly. To avoid problems
the encoder should take care encoding errors itself, for example by raising an
exception.

=head1 CUSTOM OUTPUT

This module is generally used to write XML -- which it does most of the
time -- but just like the rest of SAX it can be used as a generic
framework to output data, the opposite of a non-XML SAX parser.

Of course there's only so much that one can abstract, so depending on
your format this may or may not be useful. If it is, you'll need to
know the followin API (and probably to have a look inside
C<XML::SAX::Writer::XML>, the default Writer).

=over

=item init

Called before the writing starts, it's a chance for the subclass to do
some initialisation if it needs it.

=item setConverter

This is used to set the proper converter for character encodings. The
default implementation should suffice but you can override it. It must
set C<< $self->{Encoder} >> to an Encoder object. Subclasses *should* call
it.

=item setConsumer

Same as above, except that it is for the Consumer object, and that it
must set C<< $self->{Consumer} >>.

=item setEscaperRegex

Will initialise the escaping regex C<< $self->{EscaperRegex} >> based on
what is needed.

=item escape STRING

Takes a string and escapes it properly.

=item setCommentEscaperRegex and escapeComment STRING

These work exactly the same as the two above, except that they are meant
to operate on comment contents, which often have different escaping rules
than those that apply to regular content.

=back

=head1 TODO

    - proper UTF-16 handling

    - the formatting options need to be developed.

    - test, test, test (and then some tests)

    - doc, doc, doc (actually this part is in better shape)

    - remove the xml_decl and replace it with intelligent logic, as
    discussed on perl-xml

    - make a the Consumer selecting code available in the API, to avoid
    duplicating

    - add an Apache output Consumer, triggered by passing $r as Output

=head1 CREDITS

Michael Koehne (XML::Handler::YAWriter) for much inspiration and Barrie
Slaymaker for the Consumer pattern idea, the coderef output option and
miscellaneous bugfixes and performance tweaks. Of course the usual
suspects (Kip Hampton and Matt Sergeant) helped in the usual ways.

=head1 AUTHOR

Robin Berjon, robin@knowscape.com

=head1 COPYRIGHT

Copyright (c) 2001-2006 Robin Berjon and Perl XML project. Some rights reserved. 
This program is free software; you can redistribute it and/or modify it under 
the same terms as Perl itself.

=head1 SEE ALSO

XML::SAX::*

=cut

use strict;

# 
# This script also prints the contents of all the listed files, but
# it first scans through the list to check that each file exists and
# is readable.  It will stop if there are any errors.
#

my $bad = 0;
foreach my $fn (@ARGV) {
    if(! -r $fn) {
        # File cannot be read.  See if it exists or not for a better 
        # error message.
        if(-e $fn) {
            print STDERR "You do not have permission to read $fn.\n";
        } else {
            print STDERR "File $fn does not exist.\n";
        }

        # One way or the other, it's bad.
        $bad = 1;
    }
}

# If there was a problem, bail out.
if($bad) { exit 2; }

# Copy all the files.
while(my $fn = shift @ARGV) {

    # Open the file.
    if(!open(INFILE, $fn)) {
        # We know the file is readable, but sometimes something else goes 
        # wrong.  It's safer to check.
        print STDERR "Cannot open $fn: $!\n";
        next;
    }

    # Copy it.
    while(my $l = <INFILE>) {
        print $l;
    }

    close INFILE;
}
# See the man page for the very long list of file tests, some of which are
# Unix-specific.  To find it from perl documentation, choose the
# standard documentation pack, supporting manpages, perlfunc, then
# choose -X (first in the alphabetical list).

# This code is a part of Slash, and is released under the GPL.
# Copyright 1997-2005 by Open Source Technology Group. See README
# and COPYING for more information, or see http://slashcode.com/.

package Slash::Client;

use strict;
use warnings;

use Digest::MD5 'md5_hex';
use File::Spec::Functions;

our $VERSION = 0.01;

sub new {
    my($class, $opts) = @_;

    my $self = {};
    $self->{host} = $opts->{host} or return;
    $self->{http} = $opts->{ssl} ? 'https' : 'http';

    $self->{uid}  = $opts->{uid};
    $self->{pass} = $opts->{pass};
    $self->{logtoken}    = $opts->{logtoken};
    $self->{cookie_file} = $opts->{cookie_file};

    bless $self, $class;
    return $self;
}

sub soap {
    my($self) = @_;
    my $uri   = $self->{soap}{uri}   or return;
    my $proxy = $self->{soap}{proxy} or return;

    return $self->{soap}{cache} if $self->{soap}{cache};

    require HTTP::Cookies;
    require SOAP::Lite;

    my $cookies = HTTP::Cookies->new;

    if ($self->{logtoken}) {
        $cookies->set_cookie(0, user => $self->{logtoken}, '/', $self->{host});

    } elsif ($self->{uid} && $self->{pass}) {
        my $cookie = bakeUserCookie($self->{uid}, $self->{pass});
        $cookies->set_cookie(0, user => $cookie, '/', $self->{host});

    } else {
        my $cookie_file = $self->{cookie_file} || find_cookie_file();
        if ($cookie_file) {
            $cookies = HTTP::Cookies::Netscape->new;
            $cookies->load($cookie_file);
        }
    }

    my $soap = SOAP::Lite->uri($uri)->proxy($proxy, cookie_jar => $cookies);
    $self->{soap}{cache} = $soap;
    return $soap;
}


sub find_cookie_file {
    my $app = shift || 'Firefox';
    my $file;
    if ($^O eq 'MacOS' || $^O eq 'darwin') {
        require Mac::Files;
        Mac::Files->import(':DEFAULT');

        my($dir, $vref, $type);
        if ($^O eq 'darwin') {
            $vref = &kUserDomain;
            if ($app eq 'Chimera' || $app eq 'Firefox') {
                $type = &kApplicationSupportFolderType;
            } elsif ($app eq 'Mozilla') {
                $type = &kDomainLibraryFolderType;
            }
        } elsif ($^O eq 'MacOS') {
            $vref = &kOnSystemDisk;
            $type = &kDocumentsFolderType;
        }

        $dir = FindFolder($vref, $type, &kDontCreateFolder);
        $dir = catdir($dir, $app, 'Profiles');
        for (0, 1) {
            last if -e catfile($dir, 'cookies.txt');
            opendir(my $dh, $dir) or die "Can't open $dir: $!";
            $dir = catdir($dir, (grep !/^\./, readdir($dh))[0]);
            closedir($dh);
        }
        $file = catfile($dir, 'cookies.txt');
    }
    return $file;
}

sub bakeUserCookie {
    my($uid, $pass) = @_;
    my $cookie = $uid . '::' . md5_hex($pass);
    $cookie =~ s/(.)/sprintf("%%%02x", ord($1))/ge;
    $cookie =~ s/%/%25/g;
    return $cookie;
}

sub literal {
    my($str) = @_;
    $str =~ s/&/&amp;/g;
    $str =~ s/</&lt;/og;
    $str =~ s/>/&gt;/og;
    return $str;
}

sub fixparam {
    my($str) = @_;
    $str =~ s/([^$URI::unreserved ])/$URI::Escape::escapes{$1}/og;
    $str =~ s/ /+/g;
    return $str;
}

1;

__END__

=head1 NAME

Slash::Client - Write clients for Slash

=head1 SYNOPSIS

    my $client = Slash::Client::Journal->new({
        host => 'use.perl.org',
    });
    my $entry = $client->get_entry(10_000);

=head1 DESCRIPTION

Slash::Client allows writing clients to access Slash.  So far, only one
client is implemented: accessing journals, which is done via SOAP.  See
L<Slash::Client::Journal> for more information.

=head2 Constructor

You create an object with the C<new> constructor, which takes a hashref
of options.

=over 4

=item host

The Slash site's host name.

=item ssl

Boolean, true if the Slash site can be accessed via SSL.

=item uid

=item pass

If uid and pass have true values, they are used to construct the cookie
for authentication purposes.  See L<Authentication>.

=item logtoken

Logtoken is used for the cookie if it is passed.

=item cookie_file

Path to the file in Netscape format containing a cookie.

=back

=head2 Authentication

Some methods require authentication; others may require authentication,
depending on the site.

There are three ways to authenticate.  The first that's tried is uid/pass.
If those are not supplied, logtoken is used: this is the value actually
stored in the browser cookie (and used in the query string for some
user-authenticated feed URLS).  The third is to just try to load the cookie
from a cookie file, either passing in a path in cookie_file, or trying to
find the file automatically.

I've only tested the cookie authentication recently with Firefox on Mac OS X.
Feel free to submit patches for other browsers and platforms.

If the given authentication method fails, others are not attempted, and the
method will attempt to execute anyway.


=head1 TODO

Work on error handling.

Other platforms for finding/reading cookies.


=head1 SEE ALSO

Slash::Client::Journal(3).

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This Source Code Form is "Incompatible With Secondary Licenses", as
# defined by the Mozilla Public License, v. 2.0.

package Bugzilla::Auth;

use strict;
use fields qw(
    _info_getter
    _verifier
    _persister
);

use Bugzilla::Constants;
use Bugzilla::Error;
use Bugzilla::Mailer;
use Bugzilla::Util qw(datetime_from);
use Bugzilla::User::Setting ();
use Bugzilla::Auth::Login::Stack;
use Bugzilla::Auth::Verify::Stack;
use Bugzilla::Auth::Persist::Cookie;
use Socket;

sub new {
    my ($class, $params) = @_;
    my $self = fields::new($class);

    $params            ||= {};
    $params->{Login}   ||= Bugzilla->params->{'user_info_class'} . ',Cookie';
    $params->{Verify}  ||= Bugzilla->params->{'user_verify_class'};

    $self->{_info_getter} = new Bugzilla::Auth::Login::Stack($params->{Login});
    $self->{_verifier} = new Bugzilla::Auth::Verify::Stack($params->{Verify});
    # If we ever have any other login persistence methods besides cookies,
    # this could become more configurable.
    $self->{_persister} = new Bugzilla::Auth::Persist::Cookie();

    return $self;
}

sub login {
    my ($self, $type) = @_;
    my $dbh = Bugzilla->dbh;

    # Get login info from the cookie, form, environment variables, etc.
    my $login_info = $self->{_info_getter}->get_login_info();

    if ($login_info->{failure}) {
        return $self->_handle_login_result($login_info, $type);
    }

    # Now verify his username and password against the DB, LDAP, etc.
    if ($self->{_info_getter}->{successful}->requires_verification) {
        $login_info = $self->{_verifier}->check_credentials($login_info);
        if ($login_info->{failure}) {
            return $self->_handle_login_result($login_info, $type);
        }
        $login_info =
          $self->{_verifier}->{successful}->create_or_update_user($login_info);
    }
    else {
        $login_info = $self->{_verifier}->create_or_update_user($login_info);
    }

    if ($login_info->{failure}) {
        return $self->_handle_login_result($login_info, $type);
    }

    # Make sure the user isn't disabled.
    my $user = $login_info->{user};
    if (!$user->is_enabled) {
        return $self->_handle_login_result({ failure => AUTH_DISABLED,
                                              user    => $user }, $type);
    }
    $user->set_authorizer($self);

    return $self->_handle_login_result($login_info, $type);
}

sub can_change_password {
    my ($self) = @_;
    my $verifier = $self->{_verifier}->{successful};
    $verifier  ||= $self->{_verifier};
    my $getter   = $self->{_info_getter}->{successful};
    $getter      = $self->{_info_getter} 
        if (!$getter || $getter->isa('Bugzilla::Auth::Login::Cookie'));
    return $verifier->can_change_password &&
           $getter->user_can_create_account;
}

sub can_login {
    my ($self) = @_;
    my $getter = $self->{_info_getter}->{successful};
    $getter    = $self->{_info_getter}
        if (!$getter || $getter->isa('Bugzilla::Auth::Login::Cookie'));
    return $getter->can_login;
}

sub can_logout {
    my ($self) = @_;
    my $getter = $self->{_info_getter}->{successful};
    # If there's no successful getter, we're not logged in, so of
    # course we can't log out!
    return 0 unless $getter;
    return $getter->can_logout;
}

sub user_can_create_account {
    my ($self) = @_;
    my $verifier = $self->{_verifier}->{successful};
    $verifier  ||= $self->{_verifier};
    my $getter   = $self->{_info_getter}->{successful};
    $getter      = $self->{_info_getter}
        if (!$getter || $getter->isa('Bugzilla::Auth::Login::Cookie'));
    return $verifier->user_can_create_account
           && $getter->user_can_create_account;
}

sub extern_id_used {
    my ($self) = @_;
    return $self->{_info_getter}->extern_id_used
           ||  $self->{_verifier}->extern_id_used;
}

sub can_change_email {
    return $_[0]->user_can_create_account;
}

sub _handle_login_result {
    my ($self, $result, $login_type) = @_;
    my $dbh = Bugzilla->dbh;

    my $user      = $result->{user};
    my $fail_code = $result->{failure};

    if (!$fail_code) {
        # We don't persist logins over GET requests in the WebService,
        # because the persistance information can't be re-used again.
        # (See Bugzilla::WebService::Server::JSONRPC for more info.)
        if ($self->{_info_getter}->{successful}->requires_persistence
            and !Bugzilla->request_cache->{auth_no_automatic_login}) 
        {
            $self->{_persister}->persist_login($user);
        }
    }
    elsif ($fail_code == AUTH_ERROR) {
        if ($result->{user_error}) {
            ThrowUserError($result->{user_error}, $result->{details});
        }
        else {
            ThrowCodeError($result->{error}, $result->{details});
        }
    }
    elsif ($fail_code == AUTH_NODATA) {
        $self->{_info_getter}->fail_nodata($self) 
            if $login_type == LOGIN_REQUIRED;

        # If we're not LOGIN_REQUIRED, we just return the default user.
        $user = Bugzilla->user;
    }
    # The username/password may be wrong
    # Don't let the user know whether the username exists or whether
    # the password was just wrong. (This makes it harder for a cracker
    # to find account names by brute force)
    elsif ($fail_code == AUTH_LOGINFAILED or $fail_code == AUTH_NO_SUCH_USER) {
        my $remaining_attempts = MAX_LOGIN_ATTEMPTS 
                                 - ($result->{failure_count} || 0);
        ThrowUserError("invalid_username_or_password", 
                       { remaining => $remaining_attempts });
    }
    # The account may be disabled
    elsif ($fail_code == AUTH_DISABLED) {
        $self->{_persister}->logout();
        # XXX This is NOT a good way to do this, architecturally.
        $self->{_persister}->clear_browser_cookies();
        # and throw a user error
        ThrowUserError("account_disabled",
            {'disabled_reason' => $result->{user}->disabledtext});
    }
    elsif ($fail_code == AUTH_LOCKOUT) {
        my $attempts = $user->account_ip_login_failures;

        # We want to know when the account will be unlocked. This is 
        # determined by the 5th-from-last login failure (or more/less than
        # 5th, if MAX_LOGIN_ATTEMPTS is not 5).
        my $determiner = $attempts->[scalar(@$attempts) - MAX_LOGIN_ATTEMPTS];
        my $unlock_at = datetime_from($determiner->{login_time}, 
                                      Bugzilla->local_timezone);
        $unlock_at->add(minutes => LOGIN_LOCKOUT_INTERVAL);

        # If we were *just* locked out, notify the maintainer about the
        # lockout.
        if ($result->{just_locked_out}) {
            # We're sending to the maintainer, who may be not a Bugzilla 
            # account, but just an email address. So we use the
            # installation's default language for sending the email.
            my $default_settings = Bugzilla::User::Setting::get_defaults();
            my $template = Bugzilla->template_inner(
                               $default_settings->{lang}->{default_value});
            my $address = $attempts->[0]->{ip_addr};
            # Note: inet_aton will only resolve IPv4 addresses.
            # For IPv6 we'll need to use inet_pton which requires Perl 5.12.
            my $n = inet_aton($address);
            if ($n) {
                $address = gethostbyaddr($n, AF_INET) . " ($address)"
            }
            my $vars = {
                locked_user => $user,
                attempts    => $attempts,
                unlock_at   => $unlock_at,
                address     => $address,
            };
            my $message;
            $template->process('email/lockout.txt.tmpl', $vars, \$message)
                || ThrowTemplateError($template->error);
            MessageToMTA($message);
        }

        $unlock_at->set_time_zone($user->timezone);
        ThrowUserError('account_locked', 
            { ip_addr => $determiner->{ip_addr}, unlock_at => $unlock_at });
    }
    # If we get here, then we've run out of options, which shouldn't happen.
    else {
        ThrowCodeError("authres_unhandled", { value => $fail_code });
    }

    return $user;
}

1;

__END__

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This Source Code Form is "Incompatible With Secondary Licenses", as
# defined by the Mozilla Public License, v. 2.0.

package Bugzilla::BugUrl;
use strict;
use base qw(Bugzilla::Object);

use Bugzilla::Util;
use Bugzilla::Error;
use Bugzilla::Constants;
use Bugzilla::Hook;

use URI::QueryParam;

###############################
####    Initialization     ####
###############################

use constant DB_TABLE   => 'bug_see_also';
use constant NAME_FIELD => 'value';
use constant LIST_ORDER => 'id';
# See Also is tracked in bugs_activity.
use constant AUDIT_CREATES => 0;
use constant AUDIT_UPDATES => 0;
use constant AUDIT_REMOVES => 0;

use constant DB_COLUMNS => qw(
    id
    bug_id
    value
    class
);

# This must be strings with the names of the validations,
# instead of coderefs, because subclasses override these
# validators with their own.
use constant VALIDATORS => {
    value  => '_check_value',
    bug_id => '_check_bug_id',
    class  => \&_check_class,
};

# This is the order we go through all of subclasses and
# pick the first one that should handle the url. New
# subclasses should be added at the end of the list.
use constant SUB_CLASSES => qw(
    Bugzilla::BugUrl::Bugzilla::Local
    Bugzilla::BugUrl::Bugzilla
    Bugzilla::BugUrl::Launchpad
    Bugzilla::BugUrl::Google
    Bugzilla::BugUrl::Debian
    Bugzilla::BugUrl::JIRA
    Bugzilla::BugUrl::Trac
    Bugzilla::BugUrl::MantisBT
    Bugzilla::BugUrl::SourceForge
    Bugzilla::BugUrl::GitHub
);

###############################
####      Accessors      ######
###############################

sub class  { return $_[0]->{class}  }
sub bug_id { return $_[0]->{bug_id} }

###############################
####        Methods        ####
###############################

sub new {
    my $class = shift;
    my $param = shift;

    if (ref $param) {
        my $bug_id = $param->{bug_id};
        my $name   = $param->{name} || $param->{value};
        if (!defined $bug_id) {
            ThrowCodeError('bad_arg',
                { argument => 'bug_id',
                  function => "${class}::new" });
        }
        if (!defined $name) {
            ThrowCodeError('bad_arg',
                { argument => 'name',
                  function => "${class}::new" });
        }

        my $condition = 'bug_id = ? AND value = ?';
        my @values = ($bug_id, $name);
        $param = { condition => $condition, values => \@values };
    }

    unshift @_, $param;
    return $class->SUPER::new(@_);
}

sub _do_list_select {
    my $class = shift;
    my $objects = $class->SUPER::_do_list_select(@_);

    foreach my $object (@$objects) {
        eval "use " . $object->class; die $@ if $@;
        bless $object, $object->class;
    }

    return $objects
}

# This is an abstract method. It must be overridden
# in every subclass.
sub should_handle {
    my ($class, $input) = @_;
    ThrowCodeError('unknown_method',
        { method => "${class}::should_handle" });
}

sub class_for {
    my ($class, $value) = @_;

    my @sub_classes = $class->SUB_CLASSES;
    Bugzilla::Hook::process("bug_url_sub_classes",
        { sub_classes => \@sub_classes });

    my $uri = URI->new($value);
    foreach my $subclass (@sub_classes) {
        eval "use $subclass";
        die $@ if $@;
        return wantarray ? ($subclass, $uri) : $subclass
            if $subclass->should_handle($uri);
    }

    ThrowUserError('bug_url_invalid', { url => $value });
}

sub _check_class {
    my ($class, $subclass) = @_;
    eval "use $subclass"; die $@ if $@;
    return $subclass;
}

sub _check_bug_id {
    my ($class, $bug_id) = @_;

    my $bug;
    if (blessed $bug_id) {
        # We got a bug object passed in, use it
        $bug = $bug_id;
        $bug->check_is_visible;
    }
    else {
        # We got a bug id passed in, check it and get the bug object
        $bug = Bugzilla::Bug->check({ id => $bug_id });
    }

    return $bug->id;
}

sub _check_value {
    my ($class, $uri) = @_;

    my $value = $uri->as_string;

    if (!$value) {
        ThrowCodeError('param_required',
                       { function => 'add_see_also', param => '$value' });
    }

    # We assume that the URL is an HTTP URL if there is no (something):// 
    # in front.
    if (!$uri->scheme) {
        # This works better than setting $uri->scheme('http'), because
        # that creates URLs like "http:domain.com" and doesn't properly
        # differentiate the path from the domain.
        $uri = new URI("http://$value");
    }
    elsif ($uri->scheme ne 'http' && $uri->scheme ne 'https') {
        ThrowUserError('bug_url_invalid', { url => $value, reason => 'http' });
    }

    # This stops the following edge cases from being accepted:
    # * show_bug.cgi?id=1
    # * /show_bug.cgi?id=1
    # * http:///show_bug.cgi?id=1
    if (!$uri->authority or $uri->path !~ m{/}) {
        ThrowUserError('bug_url_invalid',
                       { url => $value, reason => 'path_only' });
    }

    if (length($uri->path) > MAX_BUG_URL_LENGTH) {
        ThrowUserError('bug_url_too_long', { url => $uri->path });
    }

    return $uri;
}

1;

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This Source Code Form is "Incompatible With Secondary Licenses", as
# defined by the Mozilla Public License, v. 2.0.

package Bugzilla::RNG;
use strict;
use base qw(Exporter);
use Bugzilla::Constants qw(ON_WINDOWS);

use Math::Random::ISAAC;
use if ON_WINDOWS, 'Win32::API';

our $RNG;
our @EXPORT_OK = qw(rand srand irand);

# ISAAC, a 32-bit generator, should only be capable of generating numbers
# between 0 and 2^32 - 1. We want _to_float to generate numbers possibly
# including 0, but always less than 1.0. Dividing the integer produced
# by irand() by this number should do that exactly.
use constant DIVIDE_BY => 2**32;

# How many bytes of seed to read.
use constant SEED_SIZE => 16; # 128 bits.

#################
# Windows Stuff #
#################

# The type of cryptographic service provider we want to use.
# This doesn't really matter for our purposes, so we just pick
# PROV_RSA_FULL, which seems reasonable. For more info, see
# http://msdn.microsoft.com/en-us/library/aa380244(v=VS.85).aspx
use constant PROV_RSA_FULL => 1;

# Flags for CryptGenRandom:
# Don't ever display a UI to the user, just fail if one would be needed.
use constant CRYPT_SILENT => 64;
# Don't require existing public/private keypairs.
use constant CRYPT_VERIFYCONTEXT => 0xF0000000;

# For some reason, BOOLEAN doesn't work properly as a return type with 
# Win32::API.
use constant RTLGENRANDOM_PROTO => <<END;
INT SystemFunction036(
  PVOID RandomBuffer,
  ULONG RandomBufferLength
)
END

#################
# RNG Functions #
#################

sub rand (;$) {
    my ($limit) = @_;
    my $int = irand();
    return _to_float($int, $limit);
}

sub irand (;$) {
    my ($limit) = @_;
    Bugzilla::RNG::srand() if !defined $RNG;
    my $int = $RNG->irand();
    if (defined $limit) {
        # We can't just use the mod operator because it will bias
        # our output. Search for "modulo bias" on the Internet for
        # details. This is slower than mod(), but does not have a bias,
        # as demonstrated by Math::Random::Secure's uniform.t test.
        return int(_to_float($int, $limit));
    }
    return $int;
}

sub srand (;$) {
    my ($value) = @_;
    # Remove any RNG that might already have been made.
    $RNG = undef;
    my %args;
    if (defined $value) {
        $args{seed} = $value;
    }
    $RNG = _create_rng(\%args);
}

sub _to_float {
    my ($integer, $limit) = @_;
    $limit ||= 1;
    return ($integer / DIVIDE_BY) * $limit;
}

##########################
# Seed and PRNG Creation #
##########################

sub _create_rng {
    my ($params) = @_;

    if (!defined $params->{seed}) {
        $params->{seed} = _get_seed();
    }

    _check_seed($params->{seed});

    my @seed_ints = unpack('L*', $params->{seed});

    my $rng = Math::Random::ISAAC->new(@seed_ints);

    # It's faster to skip the frontend interface of Math::Random::ISAAC
    # and just use the backend directly. However, in case the internal
    # code of Math::Random::ISAAC changes at some point, we do make sure
    # that the {backend} element actually exists first.
    return $rng->{backend} ? $rng->{backend} : $rng;
}

sub _check_seed {
    my ($seed) = @_;
    if (length($seed) < 8) {
        warn "Your seed is less than 8 bytes (64 bits). It could be"
             . " easy to crack";
    }
    # If it looks like we were seeded with a 32-bit integer, warn the
    # user that they are making a dangerous, easily-crackable mistake.
    elsif (length($seed) <= 10 and $seed =~ /^\d+$/) {
        warn "RNG seeded with a 32-bit integer, this is easy to crack";
    }
}

sub _get_seed {
    return _windows_seed() if ON_WINDOWS;

    if (-r '/dev/urandom') {
        return _read_seed_from('/dev/urandom');
    }

    return _read_seed_from('/dev/random');
}

sub _read_seed_from {
    my ($from) = @_;

    open(my $fh, '<', $from) or die "$from: $!";
    my $buffer;
    read($fh, $buffer, SEED_SIZE);
    if (length($buffer) < SEED_SIZE) {
        die "Could not read enough seed bytes from $from, got only " 
            . length($buffer);
    }
    close $fh;
    return $buffer;
}

sub _windows_seed {
    my ($major, $minor) = (Win32::GetOSVersion())[1,2];
    if ($major < 5) {
        die "Bugzilla does not support versions of Windows before"
            . " Windows 2000";
    }
    # This means Windows 2000.
    if ($major == 5 and $minor == 0) {
        return _win2k_seed();
    }

    my $rtlgenrand = Win32::API->new('advapi32', RTLGENRANDOM_PROTO);
    if (!defined $rtlgenrand) {
        die "Could not import RtlGenRand: $^E";
    }
    my $buffer = chr(0) x SEED_SIZE;
    my $result = $rtlgenrand->Call($buffer, SEED_SIZE);
    if (!$result) {
        die "RtlGenRand failed: $^E";
    }
    return $buffer;
}

sub _win2k_seed {
    my $crypt_acquire = Win32::API->new(
        "advapi32", 'CryptAcquireContext', 'PPPNN', 'I');
    if (!defined $crypt_acquire) {
        die "Could not import CryptAcquireContext: $^E";
    }

    my $crypt_release = Win32::API->new(
        "advapi32", 'CryptReleaseContext', 'NN', 'I');
    if (!defined $crypt_release) {
        die "Could not import CryptReleaseContext: $^E";
    }

    my $crypt_gen_random = Win32::API->new(
        "advapi32", 'CryptGenRandom', 'NNP', 'I');
    if (!defined $crypt_gen_random) {
        die "Could not import CryptGenRandom: $^E";
    }

    my $context = chr(0) x Win32::API::Type->sizeof('PULONG');
    my $acquire_result = $crypt_acquire->Call(
        $context, 0, 0, PROV_RSA_FULL, CRYPT_SILENT | CRYPT_VERIFYCONTEXT);
    if (!defined $acquire_result) {
        die "CryptAcquireContext failed: $^E";
    }

    my $pack_type = Win32::API::Type::packing('PULONG');
    $context = unpack($pack_type, $context);

    my $buffer = chr(0) x SEED_SIZE;
    my $rand_result = $crypt_gen_random->Call($context, SEED_SIZE, $buffer);
    my $rand_error = $^E;
    # We don't check this if it fails, we don't care.
    $crypt_release->Call($context, 0);
    if (!defined $rand_result) {
        die "CryptGenRandom failed: $rand_error";
    }
    return $buffer;
}

1;
