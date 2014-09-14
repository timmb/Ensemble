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

#include "Common.h"
//#include "HardwareDriver.h"

#include "cinder/Surface.h"

#include "XnOpenNI.h"
#include "XnCodecIDs.h"
#include "XnCppWrapper.h"
#include "XnLog.h"

#include "VOpenNIHeaders.h"

//#include <boost/thread.hpp>

#include "Settings.h"

#include "cinder/app/MouseEvent.h"

//static const int MAX_DEVICES = 1;

typedef std::vector<ci::Vec3f> PointCloud;


class Kinect
{
public:
	Kinect(Settings const& settings);
	virtual ~Kinect();
	
	void setup(int deviceId);
	void update(float dt, float elapsedTime);
	void scene();
	
	PointCloud const& pointCloud() const { return mPointCloud; }
	
	/// Was data updated in the last update() call?
	bool isDataNew() const;
		
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
	
	std::vector<ci::Vec3f> mPointCloud;
	
	V::OpenNIDeviceManager* mOpenNI;
	V::OpenNIDevice::Ref mDevice;
	
	bool mIsDataNew;
	int mDeviceId;

	
	Settings const& mSettings;
	
};



#endif /* defined(__Ensemble__Kinect__) */
