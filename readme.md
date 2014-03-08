Ensemble
==============

Common code used for the interactive sound installation The Cave of Sounds (http://caveofsounds.com). This includes
* KinectStreamer - A cinder app to read skeletal information of a user from a Kinect (using OpenNI), extract musical parameters and send these via OSC. This was used on the instruments Wind and Campanology.
* TadeoStreamer - A variation of KinectStreamer with Trigger zones, created for Tadeo's Generative Net Sampler instrument.
* The Stabilizer - The central software coordinating communication and cohesion between the instruments of the installation, written in Python against PySide and TwistedOsc.
* The Visualization - A particle system visualising relationships between the instruments, written in C++ against Cinder/OpenGL/GLSL.

Dependencies
============

Cinder projects are built against Cinder 0.84. The Kinect-based programs are dependent upon
BlockOpenNI which is forked here: https://github.com/timmb/BlockOpenNI available here: 

It is set up for the following folder structure

.../cinder_0.8.4 (as downloaded from http://libcinder.org)
   . / blocks
   . . / BlockOpenNI (from https://github.com/timmb/BlockOpenNI, multidevices branch)
   . / boost (version 1.48, might need to be downloaded separately from http://www.boost.org/users/history/version_1_48_0.html )

.../Ensemble
   . / KinectStreamer
   . / readme.md (this file)


Tim Murray-Browne
Feb-Apr 2013, Mar 2014

http://timmb.com
