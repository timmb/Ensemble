#!/bin/sh

for f in *.ui; do pyside-uic $f > ${f%.ui}.py ; done 