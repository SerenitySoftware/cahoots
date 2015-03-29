#!/bin/bash
echo
echo
echo " [Cahoots] Step 1: Executing Unit Tests (Python 2)"
echo
nosetests tests/test.py --with-coverage --cover-package=cahoots --cover-min-percentage 100
rm -f .coverage*
echo -e "\nExit Code:" $?
echo
echo " [Cahoots] Step 1: Executing Unit Tests (Python 3)"
echo
nosetests3 tests/test.py --with-coverage --cover-package=cahoots --cover-min-percentage 100
rm -f .coverage*
echo -e "\nExit Code:" $?

echo
echo " [Cahoots] Step 2: Executing pep8 and pyflakes Tests (flake8). (Python 2)"
echo
flake8 cahoots tests cahootserver
echo "Exit Code:" $?
echo
echo " [Cahoots] Step 2: Executing pep8 and pyflakes Tests (flake8). (Python 3)"
echo
flake83 cahoots tests cahootserver
echo "Exit Code:" $?

echo
echo " [Cahoots] Step 3: Executing pylint Tests (Python 2)"
echo
pylint cahoots tests cahootserver --reports=no
echo "Exit Code:" $?
echo
echo " [Cahoots] Step 3: Executing pylint Tests (Python 3)"
echo
pylint3 cahoots tests cahootserver --reports=no
echo "Exit Code:" $?
echo
