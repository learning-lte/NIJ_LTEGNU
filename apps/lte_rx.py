#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Lte Rx
# GNU Radio version: 3.7.14.0
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from PyQt4.QtCore import QObject, pyqtSlot
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import NIJ
import ieee802_11
import sip
import sys
import time
from gnuradio import qtgui


class lte_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lte Rx")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lte Rx")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "lte_rx")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 7.68e6
        self.samp_fact = samp_fact = int(samp_rate/(7.68e6))
        self.window_size = window_size = 512
        self.plat = plat = 2
        self.lo_offset = lo_offset = 0
        self.gain = gain = 0.96
        self.freq = freq = 1715e6
        self.file_suffix = file_suffix = "3.35_1.98_3_3"
        self.corr_threshold = corr_threshold = 0.34
        self.buffer_size = buffer_size = 500*samp_fact
        self.amp_threshold = amp_threshold = 0.051

        ##################################################
        # Blocks
        ##################################################
        self._samp_rate_options = [5e6, 10e6, 15e6, 19e6, 20e6, 21e6, 25e6, 40e6, 50e6, 56e6, 60e6, 7.68e6]
        self._samp_rate_labels = ["5 MHz", "10 MHz", "15 MHz", "19 MHz", "20 MHz", "21MHz", "25MHz","40 MHz", "50 MHz", "56 MHz"]
        self._samp_rate_tool_bar = Qt.QToolBar(self)
        self._samp_rate_tool_bar.addWidget(Qt.QLabel("samp_rate"+": "))
        self._samp_rate_combo_box = Qt.QComboBox()
        self._samp_rate_tool_bar.addWidget(self._samp_rate_combo_box)
        for label in self._samp_rate_labels: self._samp_rate_combo_box.addItem(label)
        self._samp_rate_callback = lambda i: Qt.QMetaObject.invokeMethod(self._samp_rate_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._samp_rate_options.index(i)))
        self._samp_rate_callback(self.samp_rate)
        self._samp_rate_combo_box.currentIndexChanged.connect(
        	lambda i: self.set_samp_rate(self._samp_rate_options[i]))
        self.top_grid_layout.addWidget(self._samp_rate_tool_bar)
        self._lo_offset_options = (0, 6e6, 11e6, )
        self._lo_offset_labels = (str(self._lo_offset_options[0]), str(self._lo_offset_options[1]), str(self._lo_offset_options[2]), )
        self._lo_offset_tool_bar = Qt.QToolBar(self)
        self._lo_offset_tool_bar.addWidget(Qt.QLabel("lo_offset"+": "))
        self._lo_offset_combo_box = Qt.QComboBox()
        self._lo_offset_tool_bar.addWidget(self._lo_offset_combo_box)
        for label in self._lo_offset_labels: self._lo_offset_combo_box.addItem(label)
        self._lo_offset_callback = lambda i: Qt.QMetaObject.invokeMethod(self._lo_offset_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._lo_offset_options.index(i)))
        self._lo_offset_callback(self.lo_offset)
        self._lo_offset_combo_box.currentIndexChanged.connect(
        	lambda i: self.set_lo_offset(self._lo_offset_options[i]))
        self.top_grid_layout.addWidget(self._lo_offset_tool_bar)
        self._gain_range = Range(0, 1, 0.01, 0.96, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, "gain", "counter_slider", float)
        self.top_grid_layout.addWidget(self._gain_win)
        self._freq_range = Range(900e6, 2.6e9, 1e6, 1715e6, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "freq", "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_win)
        self._corr_threshold_range = Range(0, 1, .0001, 0.34, 200)
        self._corr_threshold_win = RangeWidget(self._corr_threshold_range, self.set_corr_threshold, "corr_threshold", "counter_slider", float)
        self.top_grid_layout.addWidget(self._corr_threshold_win)
        self._amp_threshold_range = Range(0, 1, .0001, 0.051, 200)
        self._amp_threshold_win = RangeWidget(self._amp_threshold_range, self.set_amp_threshold, "amp_threshold", "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_threshold_win)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(('', "name=SDR4")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_clock_source('external', 0)
        self.uhd_usrp_source_0.set_time_source('external', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(freq, rf_freq = freq - lo_offset, rf_freq_policy=uhd.tune_request.POLICY_MANUAL), 0)
        self.uhd_usrp_source_0.set_normalized_gain(gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_auto_dc_offset(True, 0)
        self.uhd_usrp_source_0.set_auto_iq_balance(True, 0)
        self.qtgui_time_sink_x_0_1 = qtgui.time_sink_c(
        	7680*2, #size
        	samp_rate, #samp_rate
        	"Graph Output", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1.set_y_label('a[n]/p[n]', "")

        self.qtgui_time_sink_x_0_1.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, amp_threshold, 0, 0, '')
        self.qtgui_time_sink_x_0_1.enable_autoscale(False)
        self.qtgui_time_sink_x_0_1.enable_grid(True)
        self.qtgui_time_sink_x_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1.enable_control_panel(True)
        self.qtgui_time_sink_x_0_1.enable_stem_plot(False)

        if not False:
          self.qtgui_time_sink_x_0_1.disable_legend()

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(2):
            if len(labels[i]) == 0:
                if(i % 2 == 0):
                    self.qtgui_time_sink_x_0_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_1_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_c(
        	7680*2, #size
        	samp_rate, #samp_rate
        	"Raw time Sink", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('', "")

        self.qtgui_time_sink_x_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, amp_threshold, 0, 0, '')
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)

        if not False:
          self.qtgui_time_sink_x_0_0.disable_legend()

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(2):
            if len(labels[i]) == 0:
                if(i % 2 == 0):
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	7680*2, #size
        	samp_rate, #samp_rate
        	"Normalized Autocorrelation Coefficient of a Frame", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('a[n]/p[n]', "")

        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, corr_threshold, 0, 0, '')
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)

        if not False:
          self.qtgui_time_sink_x_0.disable_legend()

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.ieee802_11_moving_average_xx_1 = ieee802_11.moving_average_ff(window_size + 36)
        self.ieee802_11_moving_average_xx_0 = ieee802_11.moving_average_cc(window_size)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, 36)
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.NIJ_lte_detector_0 = NIJ.lte_detector(corr_threshold, amp_threshold, buffer_size, samp_fact, False, plat, "/home/nij/GNU/RawData/lteframepos" + file_suffix)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.NIJ_lte_detector_0, 0), (self.qtgui_time_sink_x_0_1, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.ieee802_11_moving_average_xx_1, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_delay_0_0, 0), (self.NIJ_lte_detector_0, 1))
        self.connect((self.blocks_delay_0_0, 0), (self.NIJ_lte_detector_0, 2))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.NIJ_lte_detector_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.ieee802_11_moving_average_xx_0, 0))
        self.connect((self.ieee802_11_moving_average_xx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.ieee802_11_moving_average_xx_1, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_time_sink_x_0_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lte_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self._samp_rate_callback(self.samp_rate)
        self.set_samp_fact(int(self.samp_rate/(7.68e6)))
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_samp_fact(self):
        return self.samp_fact

    def set_samp_fact(self, samp_fact):
        self.samp_fact = samp_fact
        self.set_buffer_size(500*self.samp_fact)

    def get_window_size(self):
        return self.window_size

    def set_window_size(self, window_size):
        self.window_size = window_size
        self.ieee802_11_moving_average_xx_1.set_length(self.window_size + 36)
        self.ieee802_11_moving_average_xx_0.set_length(self.window_size)

    def get_plat(self):
        return self.plat

    def set_plat(self, plat):
        self.plat = plat

    def get_lo_offset(self):
        return self.lo_offset

    def set_lo_offset(self, lo_offset):
        self.lo_offset = lo_offset
        self._lo_offset_callback(self.lo_offset)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq, rf_freq = self.freq - self.lo_offset, rf_freq_policy=uhd.tune_request.POLICY_MANUAL), 0)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq, rf_freq = self.freq - self.lo_offset, rf_freq_policy=uhd.tune_request.POLICY_MANUAL), 1)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0.set_normalized_gain(self.gain, 0)

        self.uhd_usrp_source_0.set_normalized_gain(self.gain, 1)


    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq, rf_freq = self.freq - self.lo_offset, rf_freq_policy=uhd.tune_request.POLICY_MANUAL), 0)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq, rf_freq = self.freq - self.lo_offset, rf_freq_policy=uhd.tune_request.POLICY_MANUAL), 1)

    def get_file_suffix(self):
        return self.file_suffix

    def set_file_suffix(self, file_suffix):
        self.file_suffix = file_suffix
        self.NIJ_lte_detector_0.open("/home/nij/GNU/RawData/lteframepos" + self.file_suffix)

    def get_corr_threshold(self):
        return self.corr_threshold

    def set_corr_threshold(self, corr_threshold):
        self.corr_threshold = corr_threshold
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, self.corr_threshold, 0, 0, '')

    def get_buffer_size(self):
        return self.buffer_size

    def set_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size

    def get_amp_threshold(self):
        return self.amp_threshold

    def set_amp_threshold(self, amp_threshold):
        self.amp_threshold = amp_threshold
        self.qtgui_time_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, self.amp_threshold, 0, 0, '')
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, self.amp_threshold, 0, 0, '')


def main(top_block_cls=lte_rx, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
