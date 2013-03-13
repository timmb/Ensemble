//
//  User.cpp
//  Ensemble
//
//  Created by Tim Murray-Browne on 03/01/2013.
//
//

#include "User.h"
#include "cinder/gl/gl.h"
#include <boost/algorithm/string.hpp>
#include <boost/assign.hpp>
//#include "tmb/Utilities.h"
#include "cinder/Utilities.h"
//#include <XnTypes.h>

using namespace ci;
using namespace std;

//const int ____num_joints = 24;
//Joint ____joints[24] = {XN_SKEL_HEAD,  XN_SKEL_NECK,  XN_SKEL_TORSO,  XN_SKEL_WAIST,  XN_SKEL_LEFT_COLLAR,  XN_SKEL_LEFT_SHOULDER,  XN_SKEL_LEFT_ELBOW,  XN_SKEL_LEFT_WRIST,  XN_SKEL_LEFT_HAND,  XN_SKEL_LEFT_FINGERTIP,  XN_SKEL_RIGHT_COLLAR,  XN_SKEL_RIGHT_SHOULDER,  XN_SKEL_RIGHT_ELBOW,  XN_SKEL_RIGHT_WRIST,  XN_SKEL_RIGHT_HAND,  XN_SKEL_RIGHT_FINGERTIP,  XN_SKEL_LEFT_HIP,  XN_SKEL_LEFT_KNEE,  XN_SKEL_LEFT_ANKLE,  XN_SKEL_LEFT_FOOT,  XN_SKEL_RIGHT_HIP,  XN_SKEL_RIGHT_KNEE,  XN_SKEL_RIGHT_ANKLE,  XN_SKEL_RIGHT_FOOT };

const int NUM_JOINTS = 15;

namespace {
	// Redefine OpenNI joint enumeration as integers
	const int XN_SKEL_HEAD			= 1;
	const int XN_SKEL_NECK			= 2;
	const int XN_SKEL_TORSO			= 3;
	const int XN_SKEL_WAIST			= 4;
	const int XN_SKEL_LEFT_COLLAR		= 5;
	const int XN_SKEL_LEFT_SHOULDER	= 6;
	const int XN_SKEL_LEFT_ELBOW		= 7;
	const int XN_SKEL_LEFT_WRIST		= 8;
	const int XN_SKEL_LEFT_HAND		= 9;
	const int XN_SKEL_LEFT_FINGERTIP	=10;
	const int XN_SKEL_RIGHT_COLLAR	=11;
	const int XN_SKEL_RIGHT_SHOULDER	=12;
	const int XN_SKEL_RIGHT_ELBOW		=13;
	const int XN_SKEL_RIGHT_WRIST		=14;
	const int XN_SKEL_RIGHT_HAND		=15;
	const int XN_SKEL_RIGHT_FINGERTIP	=16;
	const int XN_SKEL_LEFT_HIP		=17;
	const int XN_SKEL_LEFT_KNEE		=18;
	const int XN_SKEL_LEFT_ANKLE		=19;
	const int XN_SKEL_LEFT_FOOT		=20;
	const int XN_SKEL_RIGHT_HIP		=21;
	const int XN_SKEL_RIGHT_KNEE		=22;
	const int XN_SKEL_RIGHT_ANKLE		=23;
	const int XN_SKEL_RIGHT_FOOT		=24;
	
	XnSkeletonJointId ____activeJoints[NUM_JOINTS] = { XN_SKEL_HEAD, XN_SKEL_NECK, XN_SKEL_TORSO, XN_SKEL_LEFT_SHOULDER, XN_SKEL_LEFT_ELBOW, XN_SKEL_LEFT_HAND, XN_SKEL_RIGHT_SHOULDER, XN_SKEL_RIGHT_ELBOW, XN_SKEL_RIGHT_HAND, XN_SKEL_LEFT_HIP, XN_SKEL_LEFT_KNEE, XN_SKEL_LEFT_FOOT, XN_SKEL_RIGHT_HIP, XN_SKEL_RIGHT_KNEE, XN_SKEL_RIGHT_FOOT };
	std::string ____activeJointNames[NUM_JOINTS] = { "head", "neck", "torso", "left_shoulder", "left_elbow", "left_hand", "right_shoulder", "right_elbow", "right_hand", "left_hip", "left_knee", "left_foot", "right_hip", "right_knee", "right_foot" };
	bool ____isRight[NUM_JOINTS] = { 0,0,0,0,0,0,1,1,1,0,0,0,1,1,1 };
	bool ____isLeft[NUM_JOINTS] = { 0,0,0,1,1,1,0,0,0,1,1,1,0,0,0 };


}
	
const vector<XnSkeletonJointId> JOINT_IDS(____activeJoints, ____activeJoints + NUM_JOINTS);
const vector<std::string> JOINT_NAMES(____activeJointNames, ____activeJointNames+NUM_JOINTS);
const vector<bool> IS_LEFT(____isLeft, ____isLeft+NUM_JOINTS);
const vector<bool> IS_RIGHT(____isRight, ____isRight+NUM_JOINTS);
const map<string, int> STRING_TO_JOINT_INDEX = boost::assign::map_list_of
	("head",0)
	("neck",1)
	("torso",2)
	("left_shoulder",3)
	("left_elbow",4)
	("left_hand",5)
	("right_shoulder",6)
	("right_elbow",7)
	("right_hand",8)
	("left_hip",9)
	("left_knee",10)
	("left_foot",11)
	("right_hip",12)
	("right_knee",13)
	("right_foot",14);

Joint::Joint(int index)
: mIndex(index)
, mConfidence(0)
{
	
}

int Joint::jointIndexFromName(std::string const& name)
{
	try
	{
		return STRING_TO_JOINT_INDEX.at(name);
	}
	catch (std::out_of_range& e)
	{
		assert(false);
		return -1;
	}
}


void Joint::update(float dt, ci::Vec3f newPos, float newConfidence, ci::Vec3f const& userPos)
{
	Vec3f prevPos = mPos;
	mPos = newPos;
	mRelPos = userPos - mPos;
	mConfidence = newConfidence;
	Vec3f newVel = (mPos - prevPos) / dt;
	if (mVel==mVel)
	{
		mVel += .5f * (newVel - mVel);
	}
	else
	{
		mVel = newVel;
	}
}




void Joint::draw()
{
	gl::color(.5*mConfidence + .4*isRight(), .86*mConfidence, .44*mConfidence + .4*isLeft());
	gl::drawSphere(mPos, 20);
}

User::User()
: age(-42)
, id(-42)
, confidence(-42)
, isNull(true)
{}


User::User(float elapsedTime)
: creationTime(elapsedTime)
, age(0)
, id(-42)
, confidence(0)
, isNull(false)
{
	for (int i=0; i<NUM_JOINTS; ++i)
	{
		joints.push_back(Joint(i));
	}
}


void User::draw()
{
	gl::disable(GL_TEXTURE_2D);
	for (auto it = joints.begin(); it!=joints.end(); ++it)
	{
		it->draw();
	}
}

Joint User::getJoint(XnSkeletonJointId id) const
{
	for (auto it=joints.begin();it!=joints.end();++it)
	{
		if (it->id() == id)
			return *it;
	}
	std::cerr << "ERROR: Invalid joint index"+toString(id) << std::endl;
	return joints[0];
}