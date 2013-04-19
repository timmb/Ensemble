//
//  OscBroadcaster.cpp
//  KinectStreamer
//
//  Created by Tim Murray-Browne on 20/02/2013.
//
//

#include "OscBroadcaster.h"
#include "Common.h"
#include "cinder/Utilities.h"
#include "Kinect.h"
#include <boost/assign.hpp>
#include <algorithm>
#include <iterator>
#include <set>
using namespace ci;
using namespace std;
using namespace ci::osc;






OscBroadcaster::OscBroadcaster()
: mKinect(NULL)
, mDestinationPort(0)
{
	
}

void OscBroadcaster::setup(Kinect* kinect)
{
	assert(kinect!=NULL);
	mKinect = kinect;
}

void OscBroadcaster::setDestination(std::string destinationIp, int destinationPort)
{
	mDestinationIp = destinationIp;
	mDestinationPort = destinationPort;
	mSender.setup(mDestinationIp, mDestinationPort);
}


void OscBroadcaster::setKinectName(std::string const& kinectName)
{
	mKinectName = kinectName;
}


void OscBroadcaster::update(double dt, double elapsedTime)
{

	
	if (mDestinationIp.empty())
	{
		hud().display("No destination IP has been set.", "OscBroadcaster");
	}
	else
	{
		hud().display("Kinect "+mKinectName+" sending to "+mDestinationIp+':'+toString(mDestinationPort), "OscBroadcaster");
	}
	

}

