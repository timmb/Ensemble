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
using namespace ci;
using namespace std;
using namespace ci::osc;


class UserMessage : public osc::Message
{
public:
	UserMessage(string const& kinectId, User const& user)
	{
		address = "/kinect/user";
		args = {
			new ArgString(kinectId),
			new ArgInt32(user.id),
			new ArgFloat(user.confidence),
			new ArgFloat(user.getJoint(XN_SKEL_TORSO).mPos.length()),
			new ArgFloat(user.age)
		};
	}
};


class JointMessage : public osc::Message
{
public:
	JointMessage(string const& kinectId, int32_t userId, Joint const& joint)
	{
		address = "/kinect/joint";
		args = {
			new ArgString(kinectId),
			new ArgInt32(userId),
			new ArgString(joint.name()),
			new ArgFloat(joint.mConfidence),
			new ArgFloat(joint.mPos.x),
			new ArgFloat(joint.mPos.y),
			new ArgFloat(joint.mPos.z),
			new ArgFloat(joint.mVel.x),
			new ArgFloat(joint.mVel.y),
			new ArgFloat(joint.mVel.z)
		};
	}
};




OscBroadcaster::OscBroadcaster()
: mKinect(NULL)
, mDestinationPort(0)
{
	
}

void OscBroadcaster::setup(Kinect* kinect, string const& kinectName)
{
	assert(kinect!=NULL);
	mKinect = kinect;
	mKinectName = kinectName;
}

void OscBroadcaster::setDestination(std::string destinationIp, int destinationPort)
{
	mDestinationIp = destinationIp;
	mDestinationPort = destinationPort;
	mSender.setup(mDestinationIp, mDestinationPort);
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
		vector<User> users = mKinect->users();
		// protocol:
		// Each update has a set of messages, one for the user and one for each of the joints
		// Messages are as follows:
		// /kinect/number_of_users <string kinect id> <int number of currently tracked users>
		// /kinect/user: <string kinect id> <int user id> <float user confidence (between 0 and 1)> <float user distance (metres)> <float duration user has been tracked (seconds)>
		// /kinect/joint: <string kinect id> <int user id> <string joint name> <float confidence> <float x> <float y> <float z> <float x velocity> <float y velocity> <float z velocity>
		Message message;
		message.setAddress("/kinect/number_of_users");
		message.addStringArg("mKinectName");
		message.addIntArg(users.size());
		for (User const& user: users)
		{
			mSender.sendMessage(UserMessage(mKinectName, user));
			for (Joint const& joint: user.joints)
			{
				mSender.sendMessage(JointMessage(mKinectName, user.id, joint));
			}
		}
	}
	

}

