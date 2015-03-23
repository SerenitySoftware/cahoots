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
import cahoots


class TestConfig(cahoots.config.BaseConfig):

    enabledModules = [
        cahoots.parsers.name.NameParser,
        cahoots.parsers.number.NumberParser,
        cahoots.parsers.character.CharacterParser,
        cahoots.parsers.boolean.BooleanParser,
        cahoots.parsers.date.DateParser,
        cahoots.parsers.phone.PhoneParser,
        cahoots.parsers.uri.URIParser,
        cahoots.parsers.email.EmailParser,
        # cahoots.parsers.programming.ProgrammingParser,
        cahoots.parsers.location.address.AddressParser,
        cahoots.parsers.location.coordinate.CoordinateParser,
        cahoots.parsers.location.landmark.LandmarkParser,
        cahoots.parsers.location.postalcode.PostalCodeParser,
        cahoots.parsers.equation.EquationParser,
        cahoots.parsers.measurement.MeasurementParser,
    ]
