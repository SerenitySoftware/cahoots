package RT::Authen::ExternalAuth;

our $VERSION = '0.10_01';

=head1 NAME

  RT::Authen::ExternalAuth - RT Authentication using External Sources

=head1 DESCRIPTION

  A complete package for adding external authentication mechanisms
  to RT. It currently supports LDAP via Net::LDAP and External Database
  authentication for any database with an installed DBI driver.

  It also allows for authenticating cookie information against an
  external database through the use of the RT-Authen-CookieAuth extension.

=head1 UPGRADING

If you are upgrading from an earlier version of this extension, you must
remove the following files manually:

    $RTHOME/local/plugins/RT-Authen-ExternalAuth/lib/RT/User_Vendor.pm
    $RTHOME/local/lib/RT/User_Vendor.pm
    $RTHOME/local/lib/RT/Authen/External_Auth.pm

Otherwise you will most likely encounter an error about modifying a read
only value and be unable to start RT.

You may not have all of these files.  It depends what versions you are
upgrading between.

If you are using a vendor packaged RT, your local directories are likely
to be somewhere under /usr/local instead of in $RTHOME so you will need
to visit Configuration -> Tools -> System Configuration to find your
plugin root.

=head2 VERSION NOTES

If you are using RT 3.6, you want to use the 0.05 version.

If you are using RT 3.8.0 or 3.8.1, you may have trouble using this
due to RT bugs related to plugins, but you may be able to use 0.08.

0.08_02 or later will not work on 3.8.0 or 3.8.1

If you are using RT 4.0.0 or greater, you must use at least 0.09

=head1 MORE ABOUT THIS MODULE 

This module provides the ability to authenticate RT users
against one or more external data sources at once. It will
also allow information about that user to be loaded from
the same, or any other available, source as well as allowing
multple redundant servers for each method.

The extension currently supports authentication and 
information from LDAP via the Net::LDAP module, and from
any data source that an installed DBI driver is available
for. 

It is also possible to use cookies set by an alternate
application for Single Sign-On (SSO) with that application.
For example, you may integrate RT with your own website login
system so that once users log in to your website, they will be
automagically logged in to RT when they access it.

It was originally designed and tested against: 

MySQL v4.1.21-standard
MySQL v5.0.22
Windows Active Directory v2003

But it has been designed so that it should work with ANY
LDAP service and ANY DBI-drivable database, based upon the
configuration given in your $RTHOME/etc/RT_SiteConfig.pm

As of v0.08 ExternalAuth also allows you to pull a browser
cookie value and test it against a DBI data source allowing
the use of cookies for Single Sign-On (SSO) authentication
with another application or website login system. This is
due to the merging of RT::Authen::ExternalAuth and
RT::Authen::CookieAuth. For example, you may integrate RT
with your own website login system so that once users log in
to your website, they will be automagically logged in to RT 
when they access it.


=head1 INSTALLATION

To install this module, run the following commands:

    perl Makefile.PL
    make
    make install

If you are using RT 3.8.x, you need to enable this
module by adding RT::Authen::ExternalAuth to your
@Plugins configuration:

Set( @Plugins, qw(RT::Authen::ExternalAuth) );

If you already have a @Plugins line, add RT::Authen::ExternalAuth to the
existing list.  Adding a second @Plugins line will cause interesting
bugs.

Once installed, you should view the file:
    
3.4/3.6    $RTHOME/local/etc/ExternalAuth/RT_SiteConfig.pm
3.8        $RTHOME/local/plugins/RT-Authen-ExternalAuth/etc/RT_SiteConfig.pm

Then use the examples provided to prepare your own custom 
configuration which should be added to your site configuration in
$RTHOME/etc/RT_SiteConfig.pm

=head1 AUTHOR
        Mike Peachey
        Jennic Ltd.
        zordrak@cpan.org

        Various Best Practical Developers

=head1 COPYRIGHT AND LICENCE

Copyright (C) 2008, Jennic Ltd.

This software is released under version 2 of the GNU 
General Public License. The license is distributed with
this package in the LICENSE file found in the directory 
root.

=cut    

use RT::Authen::ExternalAuth::LDAP;
use RT::Authen::ExternalAuth::DBI;

use strict;

# Ensure passwords are obfuscated on the System Configuration page
$RT::Config::META{ExternalSettings}->{Obfuscate} = sub {
    my ($config, $sources, $user) = @_;

    # XXX $user is never passed from RT as of 4.0.5 :(
    my $msg = 'Password not printed';
       $msg = $user->loc($msg) if $user and $user->Id;

    for my $source (values %$sources) {
        $source->{pass} = $msg;
    }
    return $sources;
};

sub DoAuth {
    my ($session,$given_user,$given_pass) = @_;

    unless(defined($RT::ExternalAuthPriority)) {
        return (0, "ExternalAuthPriority not defined, please check your configuration file.");
    }

    my $no_info_check = 0;
    unless(defined($RT::ExternalInfoPriority)) {
        $RT::Logger->debug("ExternalInfoPriority not defined. User information (including user enabled/disabled cannot be externally-sourced");
        $no_info_check = 1;
    }

    # This may be used by single sign-on (SSO) authentication mechanisms for bypassing a password check.
    my $pass_bypass = 0;
    my $success = 0;

    # Should have checked if user is already logged in before calling this function,
    # but just in case, we'll check too.
    return (0, "User already logged in!") if ($session->{'CurrentUser'} && $session->{'CurrentUser'}->Id);
    # We don't have a logged in user. Let's try all our available methods in order.
    # last if success, next if not.
    
    # Get the prioritised list of external authentication services
    my @auth_services = @$RT::ExternalAuthPriority;
    
    # For each of those services..
    foreach my $service (@auth_services) {

    $pass_bypass = 0;

        # Get the full configuration for that service as a hashref
        my $config = $RT::ExternalSettings->{$service};
        $RT::Logger->debug( "Attempting to use external auth service:",
                            $service);

        # $username will be the final username we decide to check
        # This will not necessarily be $given_user
        my $username = undef;
        
        #############################################################
        ####################### SSO Check ###########################
        #############################################################
        if ($config->{'type'} eq 'cookie') {    
            # Currently, Cookie authentication is our only SSO method
            $username = RT::Authen::ExternalAuth::DBI::GetCookieAuth($config);
        }
        #############################################################
        
        # If $username is defined, we have a good SSO $username and can
        # safely bypass the password checking later on; primarily because
        # it's VERY unlikely we even have a password to check if an SSO succeeded.
        $pass_bypass = 0;
    if(defined($username)) {
        $RT::Logger->debug("Pass not going to be checked, attempting SSO");
            $pass_bypass = 1;
        } else {

        # SSO failed and no $user was passed for a login attempt
        # We only don't return here because the next iteration could be an SSO attempt
        unless(defined($given_user)) {
            $RT::Logger->debug("SSO Failed and no user to test with. Nexting");
        next;
        }

            # We don't have an SSO login, so we will be using the credentials given
            # on RT's login page to do our authentication.
            $username = $given_user;
    
            # Don't continue unless the service works.
        # next unless RT::Authen::ExternalAuth::TestConnection($config);

            # Don't continue unless the $username exists in the external service

        $RT::Logger->debug("Calling UserExists with \$username ($username) and \$service ($service)");
            next unless RT::Authen::ExternalAuth::UserExists($username, $service);
        }

        ####################################################################
        ########## Load / Auto-Create ######################################
        ####################################################################
        # We are now sure that we're talking about a valid RT user.
        # If the user already exists, load up their info. If they don't
        # then we need to create the user in RT.

        # Does user already exist internally to RT?
        $session->{'CurrentUser'} = RT::CurrentUser->new();
        $session->{'CurrentUser'}->Load($username);

        # Unless we have loaded a valid user with a UserID create one.
        unless ($session->{'CurrentUser'}->Id) {
            my $UserObj = RT::User->new($RT::SystemUser);
            my ($val, $msg) = 
              $UserObj->Create(%{ref($RT::AutoCreate) ? $RT::AutoCreate : {}},
                               Name   => $username,
                               Gecos  => $username,
                              );
            unless ($val) {
                $RT::Logger->error( "Couldn't create user $username: $msg" );
                next;
            }
            $RT::Logger->info(  "Autocreated external user",
                                $UserObj->Name,
                                "(",
                                $UserObj->Id,
                                ")");
            
            $RT::Logger->debug("Loading new user (",
                                $username,
                                ") into current session");
            $session->{'CurrentUser'}->Load($username);
        } 
        
        ####################################################################
        ########## Authentication ##########################################
        ####################################################################
        # If we successfully used an SSO service, then authentication
        # succeeded. If we didn't then, success is determined by a password
        # test.
        $success = 0;
    if($pass_bypass) {
            $RT::Logger->debug("Password check bypassed due to SSO method being in use");
            $success = 1;
        } else {
            $RT::Logger->debug("Password validation required for service - Executing...");
            $success = RT::Authen::ExternalAuth::GetAuth($service,$username,$given_pass);
        }
       
        $RT::Logger->debug("Password Validation Check Result: ",$success);

        # If the password check succeeded then this is our authoritative service
        # and we proceed to user information update and login.
        last if $success;
    }
    
    # If we got here and don't have a user loaded we must have failed to
    # get a full, valid user from an authoritative external source.
    unless ($session->{'CurrentUser'} && $session->{'CurrentUser'}->Id) {
        delete $session->{'CurrentUser'};
        return (0, "No User");
    }

    unless($success) {
        delete $session->{'CurrentUser'};
    return (0, "Password Invalid");
    }
    
    # Otherwise we succeeded.
    $RT::Logger->debug("Authentication successful. Now updating user information and attempting login.");
        
    ####################################################################################################
    ############################### The following is auth-method agnostic ##############################
    ####################################################################################################
    
    # If we STILL have a completely valid RT user to play with...
    # and therefore password has been validated...
    if ($session->{'CurrentUser'} && $session->{'CurrentUser'}->Id) {
        
        # Even if we have JUST created the user in RT, we are going to
        # reload their information from an external source. This allows us
        # to be sure that the user the cookie gave us really does exist in
        # the database, but more importantly, UpdateFromExternal will check 
        # whether the user is disabled or not which we have not been able to 
        # do during auto-create

    # These are not currently used, but may be used in the future.
    my $info_updated = 0;
    my $info_updated_msg = "User info not updated";

        unless($no_info_check) {
            # Note that UpdateUserInfo does not care how we authenticated the user
            # It will look up user info from whatever is specified in $RT::ExternalInfoPriority
            ($info_updated,$info_updated_msg) = RT::Authen::ExternalAuth::UpdateUserInfo($session->{'CurrentUser'}->Name);
        }
                
        # Now that we definitely have up-to-date user information,
        # if the user is disabled, kick them out. Now!
        if ($session->{'CurrentUser'}->UserObj->Disabled) {
            delete $session->{'CurrentUser'};
            return (0, "User account disabled, login denied");
        }
    }
    
    # If we **STILL** have a full user and the session hasn't already been deleted
    # This If/Else is logically unnecessary, but it doesn't hurt to leave it here
    # just in case. Especially to be a double-check to future modifications.
    if ($session->{'CurrentUser'} && $session->{'CurrentUser'}->Id) {
            
            $RT::Logger->info(  "Successful login for",
                                $session->{'CurrentUser'}->Name,
                                "from",
                                $ENV{'REMOTE_ADDR'});
            # Do not delete the session. User stays logged in and
            # autohandler will not check the password again
    } else {
            # Make SURE the session is deleted.
            delete $session->{'CurrentUser'};
            return (0, "Failed to authenticate externally");
            # This will cause autohandler to request IsPassword 
            # which will in turn call IsExternalPassword
    }
    
    return (1, "Successful login");
}

sub UpdateUserInfo {
    my $username        = shift;

    # Prepare for the worst...
    my $found           = 0;
    my $updated         = 0;
    my $msg             = "User NOT updated";

    my $user_disabled   = RT::Authen::ExternalAuth::UserDisabled($username);

    my $UserObj = RT::User->new($RT::SystemUser);
    $UserObj->Load($username);        

    # If user is disabled, set the RT::Principal to disabled and return out of the function.
    # I think it's a waste of time and energy to update a user's information if they are disabled
    # and it could be a security risk if they've updated their external information with some 
    # carefully concocted code to try to break RT - worst case scenario, but they have been 
    # denied access after all, don't take any chances.
     
    # If someone gives me a good enough reason to do it, 
    # then I'll update all the info for disabled users

    if ($user_disabled) {
        unless ( $UserObj->Disabled ) {
            # Make sure principal is disabled in RT
            my ($val, $message) = $UserObj->SetDisabled(1);
            # Log what has happened
            $RT::Logger->info("User marked as DISABLED (",
                                $username,
                                ") per External Service", 
                                "($val, $message)\n");
            $msg = "User Disabled";
        }

        return ($updated, $msg);
    }    
        
    # Make sure principal is not disabled in RT
    if ( $UserObj->Disabled ) {
        my ($val, $message) = $UserObj->SetDisabled(0);
        unless ( $val ) {
            $RT::Logger->error("Failed to enable user ($username) per External Service: ".($message||''));
            return ($updated, "Failed to enable");
        }

        $RT::Logger->info("User ($username) was disabled, marked as ENABLED ",
                        "per External Service",
                        "($val, $message)\n");
    }

    # Update their info from external service using the username as the lookup key
    # CanonicalizeUserInfo will work out for itself which service to use
    # Passing it a service instead could break other RT code
    my %args = (Name => $username);
    $UserObj->CanonicalizeUserInfo(\%args);

    # For each piece of information returned by CanonicalizeUserInfo,
    # run the Set method for that piece of info to change it for the user
    foreach my $key (sort(keys(%args))) {
        next unless $args{$key};
        my $method = "Set$key";
        # We do this on the UserObj from above, not self so that there 
        # are no permission restrictions on setting information
        my ($method_success,$method_msg) = $UserObj->$method($args{$key});
        
        # If your user information is not getting updated, 
        # uncomment the following logging statements
        if ($method_success) {
            # At DEBUG level, log that method succeeded
            # $RT::Logger->debug((caller(0))[3],"$method Succeeded. $method_msg");
        } else {
            # At DEBUG level, log that method failed
            # $RT::Logger->debug((caller(0))[3],"$method Failed. $method_msg");
        }
    }

    # Confirm update success
    $updated = 1;
    $RT::Logger->debug( "UPDATED user (",
                        $username,
                        ") from External Service\n");
    $msg = 'User updated';

    return ($updated, $msg);
}

sub GetAuth {

    # Request a username/password check from the specified service
    # This is only valid for non-SSO services.
    
    my ($service,$username,$password) = @_;
    
    my $success = 0;
    
    # Get the full configuration for that service as a hashref
    my $config = $RT::ExternalSettings->{$service};
    
    # And then act accordingly depending on what type of service it is.
    # Right now, there is only code for DBI and LDAP non-SSO services
    if ($config->{'type'} eq 'db') {    
        $success = RT::Authen::ExternalAuth::DBI::GetAuth($service,$username,$password);
    $RT::Logger->debug("DBI password validation result:",$success);
    } elsif ($config->{'type'} eq 'ldap') {
        $success = RT::Authen::ExternalAuth::LDAP::GetAuth($service,$username,$password);
    $RT::Logger->debug("LDAP password validation result:",$success);
    } else {
        $RT::Logger->error("Invalid service type for GetAuth:",$service);
    }
    
    return $success; 
}

sub UserExists {

    # Request a username/password check from the specified service
    # This is only valid for non-SSO services.

    my ($username,$service) = @_;

    my $success = 0;

    # Get the full configuration for that service as a hashref
    my $config = $RT::ExternalSettings->{$service};

    # And then act accordingly depending on what type of service it is.
    # Right now, there is only code for DBI and LDAP non-SSO services
    if ($config->{'type'} eq 'db') {
        $success = RT::Authen::ExternalAuth::DBI::UserExists($username,$service);
    } elsif ($config->{'type'} eq 'ldap') {
        $success = RT::Authen::ExternalAuth::LDAP::UserExists($username,$service);
    } else {
        $RT::Logger->debug("Invalid service type for UserExists:",$service);
    }

    return $success;
}

sub UserDisabled {
    
    my $username = shift;
    my $user_disabled = 0;
    
    my @info_services = $RT::ExternalInfoPriority ? @{$RT::ExternalInfoPriority} : ();

    # For each named service in the list
    # Check to see if the user is found in the external service
    # If not found, jump to next service
    # If found, check to see if user is considered disabled by the service
    # Then update the user's info in RT and return
    foreach my $service (@info_services) {
        
        # Get the external config for this service as a hashref        
        my $config = $RT::ExternalSettings->{$service};
        
        # If the config doesn't exist, don't bother doing anything, skip to next in list.
        unless(defined($config)) {
            $RT::Logger->debug("You haven't defined a configuration for the service named \"",
                                $service,
                                "\" so I'm not going to try to get user information from it. Skipping...");
            next;
        }
        
        # If it's a DBI config:
        if ($config->{'type'} eq 'db') {
            
            unless(RT::Authen::ExternalAuth::DBI::UserExists($username,$service)) {
                $RT::Logger->debug("User (",
                                    $username,
                                    ") doesn't exist in service (",
                                    $service,
                                    ") - Cannot update information - Skipping...");
                next;
            }
            $user_disabled = RT::Authen::ExternalAuth::DBI::UserDisabled($username,$service);
            
        } elsif ($config->{'type'} eq 'ldap') {
            
            unless(RT::Authen::ExternalAuth::LDAP::UserExists($username,$service)) {
                $RT::Logger->debug("User (",
                                    $username,
                                    ") doesn't exist in service (",
                                    $service,
                                    ") - Cannot update information - Skipping...");
                next;
            }
            $user_disabled = RT::Authen::ExternalAuth::LDAP::UserDisabled($username,$service);
                    
        } elsif ($config->{'type'} eq 'cookie') {
            RT::Logger->error("You cannot use SSO Cookies as an information service.");
            next;
        } else {
            # The type of external service doesn't currently have any methods associated with it. Or it's a typo.
            RT::Logger->error("Invalid type specification for config %config->{'name'}");
            # Drop out to next service in list
            next;
        }
    
    }
    return $user_disabled;
}

sub CanonicalizeUserInfo {
    
    # Careful, this $args hashref was given to RT::User::CanonicalizeUserInfo and
    # then transparently passed on to this function. The whole purpose is to update
    # the original hash as whatever passed it to RT::User is expecting to continue its
    # code with an update args hash.
    
    my $UserObj = shift;
    my $args    = shift;
    
    my $found   = 0;
    my %params  = (Name         => undef,
                  EmailAddress => undef,
                  RealName     => undef);
    
    $RT::Logger->debug( (caller(0))[3], 
                        "called by", 
                        caller, 
                        "with:", 
                        join(", ", map {sprintf("%s: %s", $_, ($args->{$_} ? $args->{$_} : ''))}
                            sort(keys(%$args))));

    # Get the list of defined external services
    my @info_services = $RT::ExternalInfoPriority ? @{$RT::ExternalInfoPriority} : undef;
    # For each external service...
    foreach my $service (@info_services) {
        
        $RT::Logger->debug( "Attempting to get user info using this external service:",
                            $service);
        
        # Get the config for the service so that we know what attrs we can canonicalize
        my $config = $RT::ExternalSettings->{$service};
        
        if($config->{'type'} eq 'cookie'){
            $RT::Logger->debug("You cannot use SSO cookies as an information service!");
            next;
        }  
        
        # For each attr we've been told to canonicalize in the match list
        foreach my $rt_attr (@{$config->{'attr_match_list'}}) {
            # Jump to the next attr in $args if this one isn't in the attr_match_list
            $RT::Logger->debug( "Attempting to use this canonicalization key:",$rt_attr);
            unless(defined($args->{$rt_attr})) {
                $RT::Logger->debug("This attribute (",
                                    $rt_attr,
                                    ") is null or incorrectly defined in the attr_map for this service (",
                                    $service,
                                    ")");
                next;
            }
                               
            # Else, use it as a canonicalization key and lookup the user info    
            my $key = $config->{'attr_map'}->{$rt_attr};
            my $value = $args->{$rt_attr};
            
            # Check to see that the key being asked for is defined in the config's attr_map
            my $valid = 0;
            my ($attr_key, $attr_value);
            my $attr_map = $config->{'attr_map'};
            while (($attr_key, $attr_value) = each %$attr_map) {
                $valid = 1 if ($key eq $attr_value);
            }
            unless ($valid){
                $RT::Logger->debug( "This key (",
                                    $key,
                                    "is not a valid attribute key (",
                                    $service,
                                    ")");
                next;
            }
            
            # Use an if/elsif structure to do a lookup with any custom code needed 
            # for any given type of external service, or die if no code exists for
            # the service requested.
            
            if($config->{'type'} eq 'ldap'){    
                ($found, %params) = RT::Authen::ExternalAuth::LDAP::CanonicalizeUserInfo($service,$key,$value);
            } elsif ($config->{'type'} eq 'db') {
                ($found, %params) = RT::Authen::ExternalAuth::DBI::CanonicalizeUserInfo($service,$key,$value);
            } else {
                $RT::Logger->debug( (caller(0))[3],
                                    "does not consider",
                                    $service,
                                    "a valid information service");
            }
       
            # Don't Check any more attributes
            last if $found;
        }
        # Don't Check any more services
        last if $found;
    }
    
    # If found, Canonicalize Email Address and 
    # update the args hash that we were given the hashref for
    if ($found) {
        # It's important that we always have a canonical email address
        if ($params{'EmailAddress'}) {
            $params{'EmailAddress'} = $UserObj->CanonicalizeEmailAddress($params{'EmailAddress'});
        } 
        %$args = (%$args, %params);
    }

    $RT::Logger->info(  (caller(0))[3], 
                        "returning", 
                        join(", ", map {sprintf("%s: %s", $_, ($args->{$_} ? $args->{$_} : ''))}
                            sort(keys(%$args))));

    ### HACK: The config var below is to overcome the (IMO) bug in
    ### RT::User::Create() which expects this function to always
    ### return true or rejects the user for creation. This should be
    ### a different config var (CreateUncanonicalizedUsers) and 
    ### should be honored in RT::User::Create()
    return($found || $RT::AutoCreateNonExternalUsers);
   
}

{
    no warnings 'redefine';
    *RT::User::CanonicalizeUserInfo = sub {
        my $self = shift;
        my $args = shift;
        return ( CanonicalizeUserInfo( $self, $args ) );
    };
}

1;