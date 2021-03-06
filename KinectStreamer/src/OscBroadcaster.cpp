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
#include "cinder/app/AppBasic.h"
using namespace ci;
using namespace std;
using namespace ci::osc;


class UserMessage : public osc::Message
{
public:
	UserMessage(string const& kinectId, User const& user)
	{
		address = "/kinect/"+kinectId+"/user";
		const int numArgs = 4;
		Arg* myArgs[numArgs] = {
			new ArgInt32(user.id),
			new ArgFloat(user.confidence),
			new ArgFloat(user.getJoint(XN_SKEL_TORSO).mPos.length()),
			new ArgFloat(user.age)
		};
		args.assign(myArgs, myArgs+numArgs);
	}
};


class JointMessage : public osc::Message
{
public:
	JointMessage(string const& kinectId, int32_t userId, Joint const& joint)
	{
		address = "/kinect/"+kinectId+"/joint/"+joint.name();
		const int numArgs = 8;
		Arg* myArgs[numArgs] = {
			new ArgInt32(userId),
			new ArgFloat(joint.mConfidence),
			new ArgFloat(joint.mPos.x),
			new ArgFloat(joint.mPos.y),
			new ArgFloat(joint.mPos.z),
			new ArgFloat(joint.mVel.x),
			new ArgFloat(joint.mVel.y),
			new ArgFloat(joint.mVel.z)
		};
		args.assign(myArgs, myArgs+numArgs);
	}
};




OscBroadcaster::OscBroadcaster()
: mKinect(NULL)
, mDestinationPort(0)
, mKinectName("Kinect0")
, mMaxUserDepth(4000)
, mMinUserX(-1000)
, mMaxUserX(1000)
{
	
}

void OscBroadcaster::registerParams(Settings& settings)
{
	settings.addParam(new Parameter<string>(&mDestinationIp, "ip", "osc"));
	settings.addParam(new Parameter<int>(&mDestinationPort, "port", "osc"));
	settings.addParam(new Parameter<string>(&mKinectName, "deviceName", "osc"));
	settings.addParam(new Parameter<float>(&mMaxUserDepth, "Depth cutoff distance", "limits"));
	settings.addParam(new Parameter<float>(&mMinUserX, "Left cutoff point", "limits"));
	settings.addParam(new Parameter<float>(&mMaxUserX, "Right cutoff point", "limits"));
}

void OscBroadcaster::setup(Kinect* kinect)
{
	assert(kinect!=NULL);
	mKinect = kinect;
	mSender.setup(mDestinationIp, mDestinationPort);
}



struct IsUserConfident {
	bool operator()(User const& user) { return user.confidence==1.f; }
};

std::string OscBroadcaster::makeAddress(std::string const& suffix) const
{
	return "/kinect/"+mKinectName+'/'+suffix;
}


void OscBroadcaster::update(double dt, double elapsedTime)
{
	// only take users with a confidence of 1 to prevent ghost users from being sent
	vector<User> users;
	for (User const& user: mKinect->users())
		if (user.confidence==1.f)
			users.push_back(user);
	
	std::set<int> currentUserIds;
	for (auto& user: users)
	{
		currentUserIds.insert(user.id);
	}
	std::set<int> newUserIds;
	set_difference(currentUserIds.begin(), currentUserIds.end(), mPreviousUserIds.begin(), mPreviousUserIds.end(), std::inserter(newUserIds, newUserIds.end()));
	std::set<int> missingUserIds;
	set_difference(mPreviousUserIds.begin(), mPreviousUserIds.end(), currentUserIds.begin(), currentUserIds.end(), std::inserter(missingUserIds, missingUserIds.end()));
	mPreviousUserIds = currentUserIds;
	
	if (mDestinationIp.empty())
	{
		hud().display("No destination IP has been set.", "OscBroadcaster");
	}
	else
	{
		hud().display("Kinect "+mKinectName+" sending to "+mDestinationIp+':'+toString(mDestinationPort), "OscBroadcaster");
		// protocol:
		// Each update has a set of messages, one for the user and one for each of the joints
		// Messages are as follows:
		/// /kinect/number_of_users <string kinect id> <int number of currently tracked users>
		/// /kinect/new_user <string kinect id> <int new user id> # will always be called before any user data arrives
		/// /kinect/lost_user <string kinect id> <int lost user id> # means there will never be any more data for that ID without a preceding new_user message.
		/// /kinect/user: <string kinect id> <int user id> <float user confidence (between 0 and 1)> <float user distance (metres)> <float duration user has been tracked (seconds)>
		/// /kinect/joint: <string kinect id> <int user id> <string joint name> <float confidence> <float x> <float y> <float z> <float x velocity> <float y velocity> <float z velocity>
		{
			Message message;
			message.setAddress(makeAddress("number_of_users"));
			message.addIntArg(users.size());
			mSender.sendMessage(message);
		}
		for (int id : newUserIds)
		{
			Message message;
			message.setAddress(makeAddress("new_user"));
			message.addIntArg(id);
			mSender.sendMessage(message);
		}
		for (int id : missingUserIds)
		{
			Message message;
			message.setAddress(makeAddress("lost_user"));
			message.addIntArg(id);
			mSender.sendMessage(message);
		}
		// find closest confident user
		User* closestUser = NULL;
		for (User& user: users)
		{
			Vec3f torso = user.getJoint(XN_SKEL_TORSO).mPos;
			Vec3f torsoProj = user.projectedPos;
			std::cout << torso << endl;
			if (mMinUserX > torsoProj.x
				|| torsoProj.x > mMaxUserX
				|| torsoProj.z > mMaxUserDepth
				|| user.confidence<0.8)
			{
				continue;
			}
			if (closestUser==NULL || torso.lengthSquared() < closestUser->getJoint(XN_SKEL_TORSO).mPos.lengthSquared())
			{
				closestUser = &user;
			}
		}
		if (closestUser!=NULL)
		{
			mKinect->setUserBeingBroadcast(closestUser->id);
			cout << "setting to true" << endl;
			std::cout << "tracking" << endl;
			UserMessage userMessage(mKinectName, *closestUser);
			mSender.sendMessage(userMessage);
			for (Joint const& joint: closestUser->joints)
			{
				JointMessage message(mKinectName, closestUser->id, joint);
				mSender.sendMessage(message);
			}
			for (int h=0; h<2; ++h)
			{
				{
					Message message;
					message.setAddress(makeAddress(string("expression/")+(h==0?"left_hand":"right_hand")));
					message.addIntArg(closestUser->id);
					message.addFloatArg(closestUser->handExpression[h]);
					mSender.sendMessage(message);
				}
				{
					Message message;
					message.setAddress(makeAddress(string("expression_slow/")+(h==0?"left_hand":"right_hand")));
					message.addIntArg(closestUser->id);
					message.addFloatArg(closestUser->handExpressionSlow[h]);
					mSender.sendMessage(message);
				}
			}
		}
		else
		{
			mKinect->setUserBeingBroadcast(-1);
		}
	}
	

}

void OscBroadcaster::draw()
{
	gl::pushMatrices();
	{
		gl::setMatricesWindow(app::getWindowSize());
		gl::enableAdditiveBlending();
		gl::color(ColorA(1., 0.3, 0.7, 0.5));
		glLineWidth(1.5);
		gl::drawLine(Vec2f(mMinUserX, 0), Vec2f(mMinUserX, app::getWindowHeight()));
		gl::drawLine(Vec2f(mMaxUserX ,0), Vec2f(mMaxUserX, app::getWindowHeight()));
	}
	gl::popMatrices();
}
