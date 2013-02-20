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
#include "tmbUtils.h"

using namespace ci;
using namespace std;

//const int ____num_joints = 24;
//Joint ____joints[24] = {XN_SKEL_HEAD,  XN_SKEL_NECK,  XN_SKEL_TORSO,  XN_SKEL_WAIST,  XN_SKEL_LEFT_COLLAR,  XN_SKEL_LEFT_SHOULDER,  XN_SKEL_LEFT_ELBOW,  XN_SKEL_LEFT_WRIST,  XN_SKEL_LEFT_HAND,  XN_SKEL_LEFT_FINGERTIP,  XN_SKEL_RIGHT_COLLAR,  XN_SKEL_RIGHT_SHOULDER,  XN_SKEL_RIGHT_ELBOW,  XN_SKEL_RIGHT_WRIST,  XN_SKEL_RIGHT_HAND,  XN_SKEL_RIGHT_FINGERTIP,  XN_SKEL_LEFT_HIP,  XN_SKEL_LEFT_KNEE,  XN_SKEL_LEFT_ANKLE,  XN_SKEL_LEFT_FOOT,  XN_SKEL_RIGHT_HIP,  XN_SKEL_RIGHT_KNEE,  XN_SKEL_RIGHT_ANKLE,  XN_SKEL_RIGHT_FOOT };

const int NUM_JOINTS = 15;

namespace {
	XnSkeletonJoint ____activeJoints[NUM_JOINTS] = { XN_SKEL_HEAD, XN_SKEL_NECK, XN_SKEL_TORSO, XN_SKEL_LEFT_SHOULDER, XN_SKEL_LEFT_ELBOW, XN_SKEL_LEFT_HAND, XN_SKEL_RIGHT_SHOULDER, XN_SKEL_RIGHT_ELBOW, XN_SKEL_RIGHT_HAND, XN_SKEL_LEFT_HIP, XN_SKEL_LEFT_KNEE, XN_SKEL_LEFT_FOOT, XN_SKEL_RIGHT_HIP, XN_SKEL_RIGHT_KNEE, XN_SKEL_RIGHT_FOOT };
	std::string ____activeJointNames[NUM_JOINTS] = { "head", "neck", "torso", "left_shoulder", "left_elbow", "left_hand", "right_shoulder", "right_elbow", "right_hand", "left_hip", "left_knee", "left_foot", "right_hip", "right_knee", "right_foot" };
	bool ____isRight[NUM_JOINTS] = { 0,0,0,0,0,0,1,1,1,0,0,0,1,1,1 };
	bool ____isLeft[NUM_JOINTS] = { 0,0,0,1,1,1,0,0,0,1,1,1,0,0,0 };
}
	
const vector<XnSkeletonJoint> JOINT_IDS(____activeJoints, ____activeJoints + NUM_JOINTS);
const vector<std::string> JOINT_NAMES(____activeJointNames, ____activeJointNames+NUM_JOINTS);
const vector<bool> IS_LEFT(____isLeft, ____isLeft+NUM_JOINTS);
const vector<bool> IS_RIGHT(____isRight, ____isRight+NUM_JOINTS);



Joint::Joint(int index)
: mIndex(index)
, mConfidence(0)
{
	
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


User::User(float elapsedTime)
: creationTime(elapsedTime)
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

Joint User::getJoint(XnSkeletonJoint id) const
{
	for (auto it=joints.begin();it!=joints.end();++it)
	{
		if (it->id() == id)
			return *it;
	}
	ERR("Invalid joint index"+tmb::toString(id));
	return joints[0];
}