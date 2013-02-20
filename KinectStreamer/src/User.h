////
////  User.h
////  Ensemble
////
////  Created by Tim Murray-Browne on 03/01/2013.
////
////
//
#pragma once

#include <iostream>
#include <vector>
#include "XnTypes.h"
//#include "VOpenNIBone.h"
#include "cinder/Vector.h"

typedef int JointIndex;


/// Active joints. Indexing of joints follows g_UsedBoneIndexArray[15], duplicated here
extern const std::vector<XnSkeletonJoint> JOINT_IDS;
/// Names of JOINTS elements
extern const std::vector<std::string> JOINT_NAMES;

/// Whether joint is on right side of body (i.e. not centre, not left)
extern const std::vector<bool> IS_RIGHT;
/// Whether joint is on right side of body (i.e. not centre, not left)
extern const std::vector<bool> IS_LEFT;
/// Size of all of these arrays
extern const int NUM_JOINTS;

class Joint
{
public:
	/// index is where the joint appears in our arrays (arrays exclude inactive joints. Not the same as XnSkeletonJoint value
	Joint(JointIndex index);
	void update(float dt, ci::Vec3f newPos, float newConfidence, ci::Vec3f const& userPos);
	void draw();

	// VARIABLES
	ci::Vec3f mPos;
	ci::Vec3f mVel;
	ci::Vec3f mRelPos; ///< relative to the user centre of mass
	float mConfidence;
	
	// const elements
	JointIndex mIndex;
	XnSkeletonJoint id() const { return JOINT_IDS.at(mIndex); }
	std::string name() const { return JOINT_NAMES.at(mIndex); }
	bool isLeft() const { return IS_LEFT.at(mIndex); }
	bool isRight() const { return IS_RIGHT.at(mIndex); }
	
private:

};

struct User
{
	ci::Vec3f pos;
	float confidence;
	/// ID as reported by OpenNIUser
	int id;
	/// World coordinates.
	std::vector<Joint> joints;
	
	/// Elapsed time in seconds that this user was created
	 float creationTime;
	/// Current age of user. Manually updated by Kinect
	float age;
	
//	User(User const& other) = default;
	User(float elapsedTime);
	void draw();
	/// Get joint by ID (nb not index). This throws exception
	/// if id is not in JOINT_IDS
	Joint getJoint(XnSkeletonJoint id) const;
};
