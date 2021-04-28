/* -*- c++ -*- */

#define NIJ_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "NIJ_swig_doc.i"

%{
#include "NIJ/lte_detector.h"
%}

%include "NIJ/lte_detector.h"
GR_SWIG_BLOCK_MAGIC2(NIJ, lte_detector);
