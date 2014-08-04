from cahoots.parsers import\
    boolean,\
    character,\
    date,\
    email,\
    equation,\
    measurement,\
    name,\
    number,\
    phone,\
    uri
from cahoots.config import BaseConfig


class TestConfig(BaseConfig):

    enabledModules = [
        name.NameParser,
        number.NumberParser,
        character.CharacterParser,
        boolean.BooleanParser,
        date.DateParser,
        phone.PhoneParser,
        uri.URIParser,
        email.EmailParser,
        # programming.ProgrammingParser,
        # grammar.GrammarParser,
        # location.LocationParser,
        equation.EquationParser,
        measurement.MeasurementParser,
    ]
