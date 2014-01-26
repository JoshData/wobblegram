#!/usr/bin/python3
#
# Creates a wobblegram from a .MPO "3D photo" file, which is supported
# by some newer digital cameras.
#
# A MPO file is a sort of JPEG file that has multiple images inside it.
# The images are taken from slightly different perspectives, which allows
# them to be re-assembled in a stereographic way.
#
# This script uses an interesting technique based on the Fast Fourier
# Transform to magnify the differences between the two files. It then
# makes an animated GIF of the magnification.
#
# Usage;
#
# python3 wobblegram.py input_file.mpo numframes magnification output.gif
#
# Specifying 9 frames and a magnification value of 4 works well.

from PIL import Image
import sys, colorsys
import numpy as np
from images2gif import writeGif as save_animated_gif

def split_mpo(file):
	# A hack to read the left & right images from an MPO file.
	# based on https://github.com/enjalot/pys3d/blob/master/mpo.py
	# A MPO file can contain multiple images, and it may contain a
	# thumbnail image besides the main left & right images. Assume
	# the first image is one of the main images and then look for
	# the first other image that has the same dimensions.
    import io
    bytes = open(file, "rb").read()
    jpeg_start_marker = b'\xff\xd8\xff\xe1'
    images = bytes.split(jpeg_start_marker)[1:]
    image1 = Image.open(io.BytesIO(jpeg_start_marker + images[0]))
    for im in images[1:]:
	    image2 = Image.open(io.BytesIO(jpeg_start_marker + im))
	    if image1.size == image2.size: break # skip embedded thumbnails
    return image1, image2

def get_fft(filename):
	# load the image file and compute the 2D FFT over each band separately,
	# returning a tuple of a list of the FFTs by band, and the image size.
	# filename can be a string or a file-like object if the file is already read.
	if not isinstance(filename, Image.Image):
		img = Image.open(filename)
	else:
		img = filename

	# resize to prevent huge images from taking forever
	img.thumbnail((640, 480), Image.ANTIALIAS)

	# ensure RGB
	img = img.convert('RGB')

	# compute the FFT on each band
	bands = []
	for i in range(3):
		bands.append( np.ravel(np.fft.fft2(np.asarray(img.getdata(i)).reshape(img.size))) )

	return bands, img.size

def to_complex(power, angle):
	return power * (np.cos(angle) + np.sin(angle) * 1j)

def mutate(fft1, fft2, alpha, band_index):
	# linearly interpolate complex FFT value at each frequency
	return fft1 * (1 - alpha) + fft2 * alpha

	# note that that's different from interpolating the power and phase components,
	# and interpolating power and phase comes out worse.
	#power1 = np.abs(fft1)
	#power2 = np.abs(fft2)
	#phase1 = np.angle(fft1)
	#phase2 = np.angle(fft2)
	#return to_complex(power1*(1-alpha) + power2*alpha, phase1*(1-alpha) + phase2*alpha)

def mutate_bands(fft1, fft2, alpha):
	bands = [mutate(fft1[i], fft2[i], alpha, i) for i in range(len(fft1))]
	return bands

def to_image(fft_bands, size):
	bands = []
	for fft in fft_bands:
		# inverse transform to get a new image
		# convert the flattened (1D) FFT back to a 2D array, then apply inverse
		# FFT, get the magnitude at each element, and flatten the 2D array back
		# out to a 1D array.
		img_flattened = np.ravel(np.abs(np.fft.ifft2(fft.reshape(size))))
		img = Image.new("L", size)
		fft = np.asarray(img_flattened, int)
		img.putdata(fft)
		bands.append(img)

	img = Image.merge("RGB", bands)

	return img

if len(sys.argv) < 5:
	print ("python3 wobblegram.py input_file.mpo numframes magnification output.gif")
	print ()
	print ("9 frames and a magnification value of 4 works well.")
	sys.exit(1)

# load the left and right images
im1, im2 = split_mpo(sys.argv[1])

# compute FFTs on each channel of each image
fft1, size1 = get_fft(im1)
fft2, size2 = get_fft(im2)

# recompose
nframes = int(sys.argv[2])
alpha = float(sys.argv[3])
def omega(t): return np.cos(2*np.pi * t)
frames = [to_image(mutate_bands(fft1, fft2, omega(float(frame)/nframes) * alpha), size1)
		 for frame in range(0, nframes+1)]

# save animated gif
save_animated_gif(
	sys.argv[4],
	frames,
	0.05,
	True,
	)
