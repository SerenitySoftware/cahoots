"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# pylint: disable=invalid-name,too-many-public-methods,missing-docstring
from cahoots.parsers.location.postalcode import PostalCodeParser
from cahoots.parsers.location.landmark import LandmarkParser
from cahoots.parsers.location.coordinate import CoordinateParser
from cahoots.parsers.location.address import AddressParser
from cahoots.parsers.uri import URIParser
from cahoots.parsers.phone import PhoneParser
from cahoots.parsers.number import NumberParser
from cahoots.parsers.name import NameParser
from cahoots.parsers.measurement import MeasurementParser
from cahoots.parsers.equation import EquationParser
from cahoots.parsers.email import EmailParser
from cahoots.parsers.date import DateParser
from cahoots.parsers.character import CharacterParser
from cahoots.parsers.boolean import BooleanParser
from cahoots.config import BaseConfig


class TestConfig(BaseConfig):

    enabled_modules = [
        URIParser,
        PostalCodeParser,
        PhoneParser,
        NumberParser,
        NameParser,
        MeasurementParser,
        LandmarkParser,
        EquationParser,
        EmailParser,
        DateParser,
        CoordinateParser,
        CharacterParser,
        BooleanParser,
        AddressParser,
    ]

    enabled_confidence_normalizers = [
    ]
