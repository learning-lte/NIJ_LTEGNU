/* -*- c++ -*- */
/* 
 * Copyright 2021 NIJ.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "lte_detector_impl.h"
#include <iostream>
#include <chrono>

namespace gr {
  namespace NIJ {

    //Number of samples in LTE subframe at 7.68 MHz sampling rate (BW=25 PRB or 5 MHz)
    static const int MAX_SAMPLES = 7680;

    lte_detector::sptr
    lte_detector::make(double cor_thresh, double amp_thresh, int buffer, int samp_fact, bool debug, int plateau, const std::string& filename)
    {
      return gnuradio::get_initial_sptr
        (new lte_detector_impl(cor_thresh, amp_thresh, buffer, samp_fact, debug, plateau, filename));
    }

    /*
     * The private constructor
     */
    lte_detector_impl::lte_detector_impl(double cor_thresh, double amp_thresh, int buffer, int samp_fact, bool debug, int plateau, const std::string& filename)
      : gr::block("lte_detector",
              gr::io_signature::makev(3, 3, get_input_sizes()),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
            d_corr_thresh(cor_thresh),
            d_amp_thresh(amp_thresh),
            d_buffer(buffer),
            d_samp_fact(samp_fact),
            d_debug(debug),
            d_plateau(0),
            d_state(SEARCH),
            d_copied(0),
            d_frame_counter(0),
            MIN_PLATEAU(plateau),
            d_filename(filename),
            parsed_data(d_filename, std::ios::out | std::ios::trunc){
      set_tag_propagation_policy(block::TPP_DONT);
    }

    /*
     * Our virtual destructor.
     */
    lte_detector_impl::~lte_detector_impl()
    {
      parsed_data.close();
    }

    void
    lte_detector_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = noutput_items;
        ninput_items_required[1] = noutput_items;
        ninput_items_required[2] = noutput_items;
    }

    int
    lte_detector_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      //Initialize block variables
      const float *in_cor = (const float*)input_items[0];
      const gr_complex *in = (const gr_complex*) input_items[1];
      const gr_complex *in_ant2 = (const gr_complex*) input_items[2];
      gr_complex *out = (gr_complex*) output_items[0];

      int noutput = noutput_items;
	    int ninput = std::min(std::min(ninput_items[0], ninput_items[1]), ninput_items[2]);
      //std::cout << noutput << " " << ninput << '\n';
      //std::cout << "Input " << ninput << " " << in[0] << '\n';

      switch(d_state) {

      case SEARCH: {
        int i;
        
        for(i = 0; i < ninput; i++) {
          //If autocorrelation and amplitude both go above thresholds for plateau number of samples, copy frame and add position of frame to file
          if(in_cor[i] > d_corr_thresh && abs(in[i]) > d_amp_thresh) {
            if(d_plateau < MIN_PLATEAU) {
              d_plateau++;
            } 
            else {
              d_state = COPY;
              d_frame_counter++;
              d_copied = 0;
              d_plateau = 0;
              parsed_data << nitems_read(0) + i << std::endl;
              std::cout << "Frames Captured: " << d_frame_counter << '\n';
              //Adds tag to stream. Useful if File Meta Sink is attached to output
              insert_tag(nitems_written(0), d_frame_counter, nitems_read(0) + i, 0);
              break;
            }
          } else {
            d_plateau = 0;
          }
        }

        consume_each(i);
        consume(1, i*(d_samp_fact -1));
        consume(2, i*(d_samp_fact -1));
        return 0;
      }

      case COPY: {

        int o = 0;
        //(MAX_SAMPLES + d_buffer * 2) * d_samp_fact is the size of the captured frame
        //Other while conditions make sure we're not reading outside the buffers
        while( o < ninput && o < noutput && d_copied < (MAX_SAMPLES + d_buffer * 2)) {
          
          //Only sends 1st antenna buffer to the output. Can extend if needed for more antennas
          std::ofstream parsed_data(d_filename, std::ios::out | std::ios::app | std::ios::binary);
           for (int j = 0; j < d_samp_fact; j++){
             out[o * d_samp_fact + j] = in[o * d_samp_fact + j];
           }
          o++;
          d_copied++;
        }

        //If a whole frame has been copied, return to search
        if(d_copied == (MAX_SAMPLES + d_buffer * 2)) {
          d_state = SEARCH;
        }

        //Reports to GNURadio how many samples were used (consumed) from the input and made (produced) for the output
        consume_each(o);
        consume(1, o*(d_samp_fact-1));
        consume(2, o*(d_samp_fact-1));
        
        // produce(0, o);
        // produce(1, o*d_samp_fact);
        // produce(2, o*d_samp_fact);
        // o = 0;
        return o * d_samp_fact;
      }
	}
    }

  //add_item_tag(which port/stream to send, tag absolute offset(where in stream to place tag), key, value, srcid is usually used for debugging or as extra key)
  void lte_detector_impl::insert_tag(uint64_t item, int frame_counter, uint64_t input_item, int o) {
    const pmt::pmt_t key = pmt::string_to_symbol("lte_start");
    const pmt::pmt_t value = pmt::from_long(frame_counter);
    uint64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::
    now().time_since_epoch()).count();
    const pmt::pmt_t srcid = pmt::from_uint64(ns);
    add_item_tag(0, item, key, value, srcid);
}

//GNURadio has hard tiime with different data types on ports so this works
static std::vector<int> get_input_sizes(){
     return {
         sizeof(float),
         sizeof(gr_complex),
         sizeof(gr_complex),
     };
}
  } /* namespace NIJ */
} /* namespace gr */

