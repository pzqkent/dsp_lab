# demo_08_record_and_play.py
# Record audio from microphone and play to speaker using callback

# This program defines the block to be 1 frame. 
# Assignment: Modify to allow longer blocksize. Do this by changing frames_per_buffer

import pyaudio
import wave
import time
import struct
from myfunctions import clip16

filename = 'test_02.wav'

CHANNELS = 1
RATE = 16000    # Sampling rate
WIDTH = 2       # Bytes of each sample
GAIN = 1.0      # Gain of amplification

# Define callback function for recording audio
def callback_record(input_string, block_size, time_info, status):
    data = struct.unpack('h', input_string)
    sample = clip16( GAIN * data[0] )
    output_data.append(sample)
    return (None, pyaudio.paContinue)

p1 = pyaudio.PyAudio()
stream1 = p1.open(format = p1.get_format_from_width(WIDTH),
                channels = CHANNELS,
                rate = RATE,
                input = True,
                output = False,
                frames_per_buffer = 1,
                stream_callback = callback_record)

# Record to the wave file

output_data = []

stream1.start_stream()
print('* Start recording')

time.sleep(4.0)

stream1.stop_stream()
print('* Finish recording')

stream1.close()
p1.terminate()

# Convert output signal to binary string
output_string = struct.pack('h'*len(output_data), *output_data)

# write data to wave file
wf = wave.open(filename, 'w')
wf.setnchannels(CHANNELS)
wf.setsampwidth(WIDTH)
wf.setframerate(RATE)
wf.writeframes(output_string)
wf.close()

print('* Audio saved to file: ' + filename)

time.sleep(0.1)

# Now play from the wave file

wf = wave.open(filename, 'rb')

# Define callback function for playing audio
def callback_play(input_string, block_size, time_info, status):
    output_string = wf.readframes(block_size)
    return (output_string, pyaudio.paContinue)

p2 = pyaudio.PyAudio()
stream2 = p2.open(format = p2.get_format_from_width(WIDTH),
                channels = CHANNELS,
                rate = RATE,
                input = False,
                output = True,
                stream_callback = callback_play)

print('* Playing wave file ' + filename)
stream2.start_stream()

while stream2.is_active():
    time.sleep(0.1)

stream2.stop_stream()
print('* Finished')

stream2.close()
p2.terminate()


