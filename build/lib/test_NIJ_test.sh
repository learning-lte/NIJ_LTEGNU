#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/nij/GNU/main/src/gr-NIJ/lib
export PATH=/home/nij/GNU/main/src/gr-NIJ/build/lib:$PATH
export LD_LIBRARY_PATH=/home/nij/GNU/main/src/gr-NIJ/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH
test-NIJ 
