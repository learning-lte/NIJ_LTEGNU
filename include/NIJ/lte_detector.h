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


#ifndef INCLUDED_NIJ_LTE_DETECTOR_H
#define INCLUDED_NIJ_LTE_DETECTOR_H

#include <NIJ/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace NIJ {

    /*!
     * \brief <+description of block+>
     * \ingroup NIJ
     *
     */
    class NIJ_API lte_detector : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<lte_detector> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of NIJ::lte_detector.
       *
       * To avoid accidental use of raw pointers, NIJ::lte_detector's
       * constructor is in a private implementation
       * class. NIJ::lte_detector::make is the public interface for
       * creating new instances.
       */
      static sptr make(double cor_thresh, double amp_thresh, int buffer, int samp_fact, bool debug, int plateau, const std::string& filename);
    };

  } // namespace NIJ
} // namespace gr

#endif /* INCLUDED_NIJ_LTE_DETECTOR_H */

