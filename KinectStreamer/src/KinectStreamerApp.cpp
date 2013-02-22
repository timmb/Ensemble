#include "cinder/app/AppNative.h"
#include "cinder/gl/gl.h"
#include "json/json.h"

#include "Kinect.h"
#include "OscBroadcaster.h"

#include <fstream>
#include <iostream>

using namespace ci;
using namespace ci::app;
using namespace std;

class KinectStreamerApp : public AppNative {
  public:
	KinectStreamerApp();
	void setup();
	void mouseDown( MouseEvent event );
	void keyDown(KeyEvent event);
	void update();
	void draw();
	
	
private:
	void loadJson();
	Kinect mKinect;
	OscBroadcaster mOscBroadcaster;
	double mElapsedTime;
	int mDeviceId;
};

KinectStreamerApp::KinectStreamerApp()
: mElapsedTime(-.1)
, mDeviceId(-42)
{}

void KinectStreamerApp::setup()
{
	setupFont();
	loadJson();
	mKinect.setup(mDeviceId);
	mOscBroadcaster.setup(&mKinect);
//	mOscBroadcaster.setDestination("127.0.0.1", 37000);
}

void KinectStreamerApp::loadJson()
{
	std::string filename = getAssetPath("kinectStreamerSettings.json").string();
	Json::Value root;
	ifstream(filename, ifstream::in) >> root;
	bool success = true;
	if (success)
	{
		console() << "successful parse";
		Json::Value ip = root["ip"];
		Json::Value port = root["port"];
		Json::Value deviceId = root["deviceId"];
		success = ip.isString() && port.isIntegral() && deviceId.isIntegral();
		if (success)
		{
			mOscBroadcaster.setDestination(ip.asString(), port.asInt());
			mDeviceId = deviceId.asInt();
			hud().displayUntilFurtherNotice("Successfully loaded "+filename, "JSON");
		}
	}
	if (!success)
	{
		hud().displayUntilFurtherNotice("Unable to load json file.", "JSON");
	}
}

void KinectStreamerApp::keyDown(KeyEvent event)
{
	if (event.getChar()==' ')
	{
		loadJson();
	}
}

void KinectStreamerApp::mouseDown( MouseEvent event )
{
}

void KinectStreamerApp::update()
{
	double elapsedTime = getElapsedSeconds();
	double dt = elapsedTime - mElapsedTime;
	mElapsedTime = elapsedTime;
	
	mKinect.update(dt, mElapsedTime);
	mOscBroadcaster.update(dt, mElapsedTime);
}

void KinectStreamerApp::draw()
{
	// clear out the window with black
	gl::clear( Color( 0, 0, 0 ) );
	mKinect.draw();
	hud().draw();
}

CINDER_APP_NATIVE( KinectStreamerApp, RendererGl )
