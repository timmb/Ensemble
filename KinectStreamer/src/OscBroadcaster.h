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
#include "Settings.h"

class Kinect;

class OscBroadcaster
{
public:
	OscBroadcaster();
	void registerParams(Settings& settings);
	/// Should be called after registerParams
	void setup(Kinect* kinect);
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
	float mMaxUserDepth;
	float mMinUserX;
	float mMaxUserX;
};