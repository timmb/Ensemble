KinectStreamer
==============

Small Cinder project to use OpenNI Skeleton tracking on users and send the
data out via OSC.


Dependencies
============

This is built against Cinder 0.84. It is dependent upon
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
Feb-Apr 2013

http://timmb.com
