#!/bin/bash

cd /vagrant


echo
echo " [Cahoots] Step 1: Removing old coverage files"
rm -f .coverage*

echo
echo " [Cahoots] Step 2: Executing Unit Tests"
echo
nosetests tests/unit/test.py --with-coverage --cover-package=cahoots --cover-min-percentage 100
echo "Exit Code:" $?

echo
echo
echo " [Cahoots] Step 3: Executing pep8 and pyflakes Tests (flake8)."
echo
flake8 cahoots tests web
echo "Exit Code:" $?

echo
echo " [Cahoots] Step 4: Executing pylint Tests"
echo
pylint cahoots tests web --reports=no
echo "Exit Code:" $?
echo
