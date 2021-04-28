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

#ifndef INCLUDED_NIJ_LTE_DETECTOR_IMPL_H
#define INCLUDED_NIJ_LTE_DETECTOR_IMPL_H

#include <NIJ/lte_detector.h>

namespace gr {
  namespace NIJ {

    class lte_detector_impl : public lte_detector
    {
     private:
      bool d_debug;
      double d_corr_thresh;
      double d_amp_thresh;
      int d_samp_fact;
      int d_buffer;
      int d_plateau;
      enum {SEARCH, COPY} d_state;
      int d_copied;
      int d_frame_counter;
      const unsigned int MIN_PLATEAU;
      const std::string d_filename;
      std::ofstream parsed_data;

     public:
      lte_detector_impl(double cor_thresh, double amp_thresh, int buffer, int samp_fact, bool debug, int plateau, const std::string& filename);
      ~lte_detector_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

      void insert_tag(uint64_t item, int frame_counter, uint64_t input_item, int o);
    };

    static std::vector<int> get_input_sizes();

  } // namespace NIJ
} // namespace gr

#endif /* INCLUDED_NIJ_LTE_DETECTOR_IMPL_H */

