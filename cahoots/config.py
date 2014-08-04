from cahoots.parsers import boolean, character, date, email, equation, grammar, location, measurement, name, number, phone, programming, uri

class BaseConfig(object):
    """
    Cahoots Configuration
    Change this file to suit your installation's needs.
    """

    # Are we in debug mode?
    debug = False

    """
    To disable a module, simply comment it out of this list.
        Be aware that modules may have soft-dependencies on one another,
        and a disabled module may impact results results from other
        modules which seek its "council." This may result in unexpected
        confidence scores, a change in result determination, etc.
    """
    enabledModules = [
        name.NameParser,
        number.NumberParser,
        character.CharacterParser,
        boolean.BooleanParser,
        date.DateParser,
        phone.PhoneParser,
        uri.URIParser,
        email.EmailParser,
        programming.ProgrammingParser,
        #grammar.GrammarParser,
        #location.LocationParser,
        equation.EquationParser,
        measurement.MeasurementParser,
    ]

    """
    Redis config
        Specify one of the following three:
        1. host and port
         - Current values are the redis default
        2. unix_socket_path
         - The file path to the unix socket.
        3. connection_pool
          - Instance of redis.connection.ConnectionPool
    """
    redis = {
        'host': 'localhost',
        'port': 6379,
        'unix_socket_path': None,
        'connection_pool': None
    }


    """
    Configuration for the templating system
    """
    template = {
        'lookups': [
            'web/templates/'
        ],
        'modules': '/tmp/makocache/'
    }