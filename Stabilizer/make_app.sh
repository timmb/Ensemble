#!/bin/bash
cd $(dirname $0)
cd UX
./compile_ui.sh
cd ..
python setup.py py2app