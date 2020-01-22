#!/bin/bash
# script to run tests locally in shell
# requirement is to have python enviroment with ../requirements modules

python manage.py test UserApp.tests.TestHashAndSaltPassword
