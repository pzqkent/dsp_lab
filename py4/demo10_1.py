
# (Sinusoidal time-varying delay)
# This implementation uses a circular buffer with two buffer indices.
# Uses linear interpolation

import pyaudio
import wave
import struct
import math
from myfunctions import clip16

# TRY BOTH WAVE FILES
wavfile = 'author.wav'
# wavfile = 'decay_cosine_mono.wav'
# wavfile = 'sin01_mono.wav'

# wavfile = 'Trumpet.wav'

print('Play the wave file: {0:s}.'.format(wavfile))

# Open wave file
wf = wave.open( wavfile, 'rb')

# Read wave file properties
RATE        = wf.getframerate()     # Frame rate (frames/second)
WIDTH       = wf.getsampwidth()     # Number of bytes per sample
LEN         = wf.getnframes()       # Signal length
CHANNELS    = wf.getnchannels()     # Number of channels

print('The file has %d channel(s).'         % CHANNELS)
print('The file has %d frames/second.'      % RATE)
print('The file has %d frames.'             % LEN)
print('The file has %d bytes per sample.'   % WIDTH)

# Vibrato parameters
# f0 = 2
# W = 0.2
g = 1


f0 = 1.6
W = 5
# W = 0 # for no effct

# f0 = 10
# W = 0.2

# OR
# f0 = 20
# ratio = 1.06
# W = (ratio - 1.0) / (2 * math.pi * f0 )
# print W

# Create a buffer (delay line) for past values
buffer_MAX =  1024                          # Buffer length
buffer = [0.0 for i in range(buffer_MAX)]   # Initialize to zero

# Buffer (delay line) indices
kr = 0  # read index
kw = int(0.5 * buffer_MAX)  # write index (initialize to middle of buffer)
kw = buffer_MAX/2

# print('The delay of {0:.3f} seconds is {1:d} samples.'.format(delay_sec, delay_samples))
print('The buffer is {0:d} samples long.'.format(buffer_MAX))

# Open an output audio stream
p = pyaudio.PyAudio()
stream = p.open(format      = pyaudio.paInt16,
                channels    = 1,
                rate        = RATE,
                input       = False,
                output      = True )

# output_all = ''            # output signal in all (string)
output_all = bytes([])            # output signal in all (string)

print ('* Playing...')

# Loop through wave file
for n in range(0, LEN):

    # Get sample from wave file
    input_string = wf.readframes(1)

    # Convert string to number
    input_value = struct.unpack('h', input_string)[0]

    # Get previous and next buffer values (since kr is fractional)
    kr_prev = int(math.floor(kr))
    kr_next = kr_prev + 1
    frac = kr - kr_prev    # 0 <= frac < 1
    if kr_next >= buffer_MAX:
        kr_next = kr_next - buffer_MAX

    # Compute output value using interpolation
    output_value =( (1-frac) * buffer[kr_prev] + frac * buffer[kr_next] ) * g + input_value

    # Update buffer (pure delay)
    buffer[int(kw)] = input_value

    # Increment read index
    # kr = kr + 1 + W * math.sin( 2 * math.pi * f0 * n / RATE )
    kr = kr + W * (1 + math.sin( 2 * math.pi * f0 * n / RATE ))

    # print kr


    # kr = kr + 1 + W * math.sin(2 * math.pi * f0 * n / RATE)
    # Note: kr is fractional (not integer!)

    # Ensure that 0 <= kr < buffer_MAX
    if kr >= buffer_MAX:
        # End of buffer. Circle back to front.
        kr = 0

    # Increment write index
    kw = kw + 1
    if kw == buffer_MAX:
        # End of buffer. Circle back to front.
        kw = 0
    print output_value

    # Clip and convert output value to binary string
    output_string = struct.pack('h', int(clip16(output_value)))
    # output_string = struct.pack('h', int((output_value)))


    # print output_value

    # Write output to audio stream
    stream.write(output_string)

    output_all = output_all + output_string     # append new to total

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
wf.close()

# output_wavefile = wavfile[:-4] + '_vibrato.wav'
# print('Writing to wave file', output_wavefile)
# wf = wave.open(output_wavefile, 'w')      # wave file
# wf.setnchannels(1)      # one channel (mono)
# wf.setsampwidth(2)      # two bytes per sample
# wf.setframerate(RATE)   # samples per second
# wf.writeframes(output_all)
# wf.close()
# print('* Finished')
#
output_wavefile = wavfile[:-4] + 'flanger.wav'
print('Writing to wave file', output_wavefile)
wf = wave.open(output_wavefile, 'w')      # wave file
wf.setnchannels(1)      # one channel (mono)
wf.setsampwidth(2)      # two bytes per sample
wf.setframerate(RATE)   # samples per second
wf.writeframes(output_all)
wf.close()
print('* Finished')