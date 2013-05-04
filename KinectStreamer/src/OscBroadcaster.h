//
//  OscBroadcaster.h
//  KinectStreamer
//
//  Created by Tim Murray-Browne on 20/02/2013.
//
//

#pragma once
#include "cinder/Cinder.h"
#include "OscSender.h"
#include <set>

class Kinect;

class OscBroadcaster
{
public:
	OscBroadcaster();
	void setup(Kinect* kinect);
	void setKinectName(std::string const& kinectName);
	void setDestination(std::string destinationIp, int destinationPort);
	void update(double dt, double elapsedTime);
	
private:
	/// e.g. "joint/head" -> "/kinect/kinect-name/joint/head"
	std::string makeAddress(std::string const& suffix) const;
	
	ci::osc::Sender mSender;
	Kinect* mKinect;
	std::string mKinectName;
	std::string mDestinationIp;
	int mDestinationPort;
	std::set<int> mPreviousUserIds;
};