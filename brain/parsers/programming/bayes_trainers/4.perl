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
