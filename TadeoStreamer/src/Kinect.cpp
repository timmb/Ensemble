//
//  Kinect.cpp
//  Ensemble
//
//  Created by Tim Murray-Browne on 03/01/2013.
//
//

#include "Kinect.h"
#include "cinder/app/AppBasic.h"
#include "cinder/ImageIo.h"
#include <boost/algorithm/string/join.hpp>
#include <boost/foreach.hpp>
//#include "cinder/Thread.h"
#include <limits>
#include "cinder/Utilities.h"

#include "cinder/Camera.h"

//using namespace tmb;
using namespace ci;
using namespace ci::app;
using namespace std;
using namespace V;

#define CHECK(xn_result) if (xn_result!=XN_STATUS_OK) ERR(xnGetStatusString(xn_result));

//typedef boost::shared_lock<boost::shared_mutex> ReadLock;
//typedef boost::unique_lock<boost::shared_mutex> WriteLock;

Kinect::Kinect(Settings const& settings)
: mDeviceId(0)
, mSettings(settings)
, mImageWidth(0)
{}


Kinect::~Kinect()
{
}



void Kinect::setup(int deviceId)
{
	mDeviceId = deviceId;
	mFont = gl::TextureFont::create(Font("Helvetica", 16));
	mDepthSize = Vec2i(640, 480);
	mColorSize = Vec2i(640, 480);
	OpenNIDeviceManager::USE_THREAD = false;
	mOpenNI = OpenNIDeviceManager::InstancePtr();
	openKinect();
	mColor = Surface8u(mColorSize.x, mColorSize.y, false);
	mDepth = Channel16u(mDepthSize.x, mDepthSize.y);
	mPointCloud.assign(mDepthSize.x*mDepthSize.y, Vec3f());
	mBufferForPointCloud.assign(mDepthSize.x*mDepthSize.y, XnPoint3D());
	
	mImageWidth = max(mColorSize.x, mDepthSize.x);
	
	mOpenNI->SetPrimaryBuffer(0, NODE_TYPE_DEPTH);
	resetCamera();
}

void Kinect::resetCamera()
{
	
	CameraPersp cam(app::getWindowWidth(), app::getWindowHeight(), 60, 0.00001, 1000000);
	cam.setEyePoint(Vec3f(0,0,0));
	cam.setCenterOfInterestPoint(Vec3f(0,0,3000));
//	cam.setEyePoint(Vec3f(0,0,1));
//	cam.lookAt(Vec3f());
	mCamera.setCurrentCam(cam);
}

void Kinect::mouseDown(MouseEvent event)
{
	Vec2i pos = event.getPos();
	pos.x -= mImageWidth;
	mCamera.mouseDown(event.getPos());
}

void Kinect::mouseDrag(MouseEvent event)
{
	Vec2i pos = event.getPos();
	pos.x -= mImageWidth;
	mCamera.mouseDrag(event.getPos(), event.isLeftDown(), event.isMiddleDown()||sIsShiftDown, event.isRightDown());
}


void Kinect::openKinect()
{
	if (!NO_KINECT)
	{
		mOpenNI->createDevices(1, NODE_TYPE_DEPTH | NODE_TYPE_IMAGE);
		mDevice = mOpenNI->getDevice(0);
		if (mDevice)
		{
			mDevice->setDepthShiftMul(3);
			xn::DepthGenerator* depthGen = mDevice->getDepthGenerator();
//			if (imageGen->IsCapabilitySupported(XN_CAPABILITY_ALTERNATIVE_VIEW_POINT))
			{
				auto a = depthGen->GetAlternativeViewPointCap();
				auto result = a.SetViewPoint(*mDevice->getImageGenerator());
				if (result!=0) {
					app::console() << "Failed to align cameras"<<endl;
				}
				
			}
//			else
//			{
//				hud().displayForAWhile("Alternative viewpoint for image generator not supported", "Kinect");
//			}
		}
	}
}


void Kinect::update(float dt, float elapsedTime)
{
	mIsDataNew = false;
	
	double t = app::App::get()->getElapsedSeconds();
	mOpenNI->update();
	double dur = app::App::get()->getElapsedSeconds() - t;
	std::stringstream dur_string;
	dur_string << std::fixed << dur;
	hud().display("OpenNI update: "+dur_string.str()+"s");
	
	if (mDevice == NULL)
	{
		hud().display("Unable to open Kinect", "Kinect");
		openKinect();
	}
	else
	{
		hud().display("Opened Kinect device "+toString(mDeviceId), "Kinect");
		if ( mDevice->_isImageOn && mDevice->getImageGenerator()->IsValid() && mDevice->isImageDataNew() )
		{
			uint8_t *pixels = mDevice->getColorMap();
			memcpy(mColor.getData(), pixels, mColor.getRowBytes()*mColor.getHeight());
		}
		if ( mDevice->_isDepthOn && mDevice->getDepthGenerator()->IsValid() && mDevice->isDepthDataNew() )
		{
			mIsDataNew = true;
			uint16_t *pixels = mDevice->getDepthMap();
			memcpy(mDepth.getData(), pixels, mDepth.getRowBytes()*mDepth.getHeight());
			mDevice->calcDepthImageRealWorld();
			XnPoint3D* pointCloud = mDevice->getDepthMapRealWorld();
			assert(mDepth.getWidth()*mDepth.getHeight()==mPointCloud.size());
			for (int i=0; i<mPointCloud.size(); ++i)
			{
				mPointCloud[i].x = pointCloud[i].X;
				mPointCloud[i].y = pointCloud[i].Y;
				mPointCloud[i].z = pointCloud[i].Z;
//				if (i%1000==0)
//					app::console() << mPointCloud[i] << endl;
			}
		}
	}
}


void Kinect::draw()
{
	gl::pushMatrices();
	{
		gl::setMatricesWindow(app::getWindowSize());
		gl::color(1,1,1, 1);
		//gl::draw(mColor);
		
		//gl::translate(0, mColor.getHeight());
		//gl::draw(Surface(mDepth));
		
//		gl::translate(max(mColor.getWidth(), mDepth.getWidth()), 0);
		// draw point cloud
//		glMatrixMode(GL_PROJECTION);
//		glLoadIdentity();
//		glMatrixMode(GL_MODELVIEW);
//		glLoadIdentity();
		gl::setMatrices(mCamera.getCamera());
		glBegin(GL_POINTS);
		for (int i=0; i<mPointCloud.size(); ++i)
		{
			ColorA color = mColor.getPixel(Vec2i(i%mColor.getWidth(), i/mColor.getWidth()));
			gl::color(color);
			gl::vertex(mPointCloud[i]);
		}
		glEnd();
		gl::drawCoordinateFrame();
	}
	gl::popMatrices();
	
}

