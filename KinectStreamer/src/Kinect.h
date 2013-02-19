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
	virtual ~Kinect();
	
	void setup();
	void update(float dt);
	void draw();
	
	bool hasUser() const;
	/// Gets the dominant user (probably the closest)
	/// \return false if there are no users. In this case
	/// \p dest is left unaltered.
	bool getUser(User* dest) const;
	
	static ci::Vec3f getPosition(V::OpenNIBone const& joint);
	
private:
	ci::gl::TextureFontRef mFont;
	
	ci::Surface8u mColor;
	ci::Channel16u mDepth;
	ci::Vec2i mDepthSize;
	ci::Vec2i mColorSize;
	
	ci::gl::Texture mDepthTex;
	ci::gl::Texture mColorTex;
	
//	void print(xn::EnumerationErrors& errors);
	
	std::vector<std::string> mMessages;
	V::OpenNIDeviceManager* mOpenNI;
	V::OpenNIDevice::Ref mDevice;
	
	mutable boost::shared_mutex mUsersMutex;
	std::vector<User> mUsers;
};



#endif /* defined(__Ensemble__Kinect__) */
