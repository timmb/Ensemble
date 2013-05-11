//
//  Kinect.h
//  Ensemble
//
//  Created by Tim Murray-Browne on 03/01/2013.
//
//

#ifndef __Ensemble__Kinect__
#define __Ensemble__Kinect__

#include <iostream>

#include "User.h"
#include "Common.h"
#include "Settings.h"
//#include "HardwareDriver.h"

#include "cinder/Surface.h"

#include "XnOpenNI.h"
#include "XnCodecIDs.h"
#include "XnCppWrapper.h"
#include "XnLog.h"

#include "VOpenNIHeaders.h"

#include <boost/thread.hpp>

//static const int MAX_DEVICES = 1;


class Kinect
{
public:
	Kinect();
	virtual ~Kinect();
	
	void setup();
	void update(float dt, float elapsedTime, JointParameters const& jointParameters);
	void draw();
	
	/// Was user data updated in the last update() call?
	bool isUserDataNew() const;
	bool hasUser() const;
	/// Gets the dominant user (which at the moment means the closest)
	/// \return The User, or a NULL user if there are no users.
	User getUser() const;
	std::vector<User> users() const;
	
	static ci::Vec3f getPosition(V::OpenNIBone const& joint);
	static ci::Vec3f worldToProjective(ci::Vec3f const& worldPos);
	
	static Kinect* instance() { return sInstance; }
	
private:
	/// If successful then mDevice!=NULL
	void openKinect();
	
	ci::gl::TextureFontRef mFont;
	
	ci::Surface8u mColor;
	ci::Channel16u mDepth;
	ci::Vec2i mDepthSize;
	ci::Vec2i mColorSize;
	
	ci::gl::Texture mDepthTex;
	ci::gl::Texture mColorTex;
	
//	void print(xn::EnumerationErrors& errors);
	
	V::OpenNIDeviceManager* mOpenNI;
	V::OpenNIDevice::Ref mDevice;
	
//	V::OpenNIDevice::Ref tmpDevices[2];
	
	mutable boost::shared_mutex mUsersMutex;
	std::vector<User> mUsers;
	
	bool mIsUserDataNew;
	
	static Kinect* sInstance;
};



#endif /* defined(__Ensemble__Kinect__) */
