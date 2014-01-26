Wobblegram
==========

This Python module creates a wigglegram, which is a sort of steeographic image where the 3D-ness is encoded in time, through animation, rather than via, say, red/green filters. The input is an MPO file, which is a JPEG-like format supported by some newer cameras when in "3D" mode. The camera takes two images from slightly different perspectives, somehow.

A simple two-frame wobblegram could be made by just pasting two images together. Or you could add intermediate frames by fading between the images. But from a "3D photo" the differences in the images is very slight, and a fade will not produce a great transition.

Inspired by "Eulerian Video Magnification" (Wu, Rubinstein, Shih, Guttag, Durand, and Freeman 2012; http://people.csail.mit.edu/mrub/vidmag/), I thought to attept to *magnify* the difference between the two images to make for a more interesting wigglegram. In their work, the frequency domain of each pixel in a *video* is amplified. This has the surprising effect of amplifying motion. But with an MPO file we have just two frames, which means there isn't enough data to look at the frequency domain of each pixel.

Instead, `wobblegram` computes the 2D fourier transform over each of the two images (actually over each of the red, green, blue components of each image). Then it does linear interpolation in the frequency domain (on the complex FFT values themselves, though interpolating power and phase separately is similar), inverts the interpolated FFT to get back a new image, and then saves a sequence of images at different interpolation values to an animated GIF.

To create the amplication, the linear interpolation is computed outside of the range of the two frames. Say frame 1 is time 0 and frame 2 is time 1, the animation ranges from time -alpha to +alpha, where alpha is a magnification factor. With alpha > 4, the image starts to have problems. In my test, it loses a lot of contrast. 

See: http://en.wikipedia.org/wiki/Wiggle_stereoscopy