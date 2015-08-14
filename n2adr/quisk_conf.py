# This is the config file from my shack, which controls various hardware.
# The files to control my 2010 transceiver and for the improved version HiQSDR
# are in the package directory HiQSDR.

#from quisk_conf_defaults import *
import sys
from n2adr import quisk_hardware
from n2adr import quisk_widgets

if sys.platform == "win32":
  n2adr_sound_pc_capt = 'Line In (Realtek High Definition Audio)'
  n2adr_sound_pc_play = 'Speakers (Realtek High Definition Audio)'
  n2adr_sound_usb_play = 'Primary'
  n2adr_sound_usb_mic = 'Primary'
  latency_millisecs = 150
  data_poll_usec = 20000
  favorites_file_path = "C:/pub/quisk_favorites.txt"
elif 0:		# portaudio devices
  name_of_sound_play = 'portaudio:CODEC USB'
  microphone_name = "portaudio:AK5370"
  latency_millisecs = 150
  data_poll_usec = 5000
  favorites_file_path = "/home/jim/pub/quisk_favorites.txt"
elif 0:		# pulseaudio devices
  n2adr_sound_pc_capt = 'pulse:Built-in'
  n2adr_sound_pc_play = 'pulse:Built-in'
  n2adr_sound_usb_play = 'pulse:USB Sound Device'
  n2adr_sound_usb_mic = 'pulse:USB Sound Device'
  latency_millisecs = 150
  data_poll_usec = 5000
  favorites_file_path = "/home/jim/pub/quisk_favorites.txt"
else:		# alsa devices
  n2adr_sound_pc_capt = 'alsa:ALC888-VD'
  n2adr_sound_pc_play = 'alsa:ALC888-VD'
  n2adr_sound_usb_play = 'alsa:USB Sound Device'
  n2adr_sound_usb_mic = 'alsa:USB Sound Device'
  latency_millisecs = 150
  data_poll_usec = 5000
  favorites_file_path = "/home/jim/pub/quisk_favorites.txt"

name_of_sound_capt = ""
name_of_sound_play = n2adr_sound_usb_play
microphone_name = n2adr_sound_usb_mic

mic_sample_rate = 48000
playback_rate = 48000
agc_off_gain = 80
tx_level = {None:100, '60':100, '40':110, '30':100, '20':90, '15':150, '12':170, '10':130}
digital_tx_level = 300
do_repeater_offset = True
#bandTransverterOffset = {'10' : 300000}
#spot_button_keys_tx = True
#graph_width = 1.0

default_screen = 'WFall'
waterfall_y_scale = 80
waterfall_y_zero  = 40
waterfall_graph_y_scale = 40
waterfall_graph_y_zero = 90
waterfall_graph_size = 160

#radio_sound_ip = "192.168.1.196"		# IP address of play device
#radio_sound_port = 12345				# port number for audio
#radio_sound_nsamples = 360				# number of samples for each block; maximum 367
#name_of_sound_play = ''					# do not send audio to a soundcard (optional)

station_display_lines = 1
# DX cluster telent login data, thanks to DJ4CM.
dxClHost = ''
#dxClHost = 'dxc.w8wts.net'
dxClPort = 7373
user_call_sign = 'n2adr'

add_imd_button = 1
add_fdx_button = 1
use_sidetone = 1

use_rx_udp = 1				# Get ADC samples from UDP
rx_udp_ip = "192.168.1.196"		# Sample source IP address
rx_udp_port = 0xBC77			# Sample source UDP port
rx_udp_clock = 122880000  		# ADC sample rate in Hertz
rx_udp_decimation = 8 * 8 * 8		# Decimation from clock to UDP sample rate
sample_rate = int(float(rx_udp_clock) / rx_udp_decimation + 0.5)	# Don't change this
data_poll_usec = 10000
display_fraction = 1.00
tx_ip = "192.168.1.196"
tx_audio_port = 0xBC79
mic_out_volume = 0.8
freedv_tx_msg = "N2ADR Jim\n"

mixer_settings = [		# These are for CM106 like sound device
    (microphone_name, 16, 1),		# PCM capture from line
    (microphone_name, 14, 0),		# PCM capture switch
    (microphone_name, 11, 1),		# line capture switch
    (microphone_name, 12, 0.70),	# line capture volume
    (microphone_name,  3, 0),		# mic playback switch
    (microphone_name,  9, 0),		# mic capture switch
  ]
