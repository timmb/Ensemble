#include "cinder/app/AppNative.h"
#include "cinder/gl/gl.h"
#include "json/json.h"

#include "Kinect.h"
#include "OscBroadcaster.h"
#include "Settings.h"

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
	::Settings mSettings; // keep before other objects that depend on it
	Kinect mKinect;
	OscBroadcaster mOscBroadcaster;
	double mElapsedTime;
};

KinectStreamerApp::KinectStreamerApp()
: mElapsedTime(-.1)
{}

void KinectStreamerApp::setup()
{
	setupFont();
	mOscBroadcaster.registerParams(mSettings);
	mSettings.load(getAssetPath("kinectStreamerSettings.json").string());
	mSettings.setup();
	mKinect.setup();
	mOscBroadcaster.setup(&mKinect);
//	mOscBroadcaster.setDestination("127.0.0.1", 37000);
}


void KinectStreamerApp::keyDown(KeyEvent event)
{
	if (event.getChar()==' ')
	{
		mSettings.reload();
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
	hud().update(dt, mElapsedTime);
}

void KinectStreamerApp::draw()
{
	// clear out the window with black
	gl::clear( Color( 0, 0, 0 ) );
	mKinect.draw();
	hud().draw();
}

CINDER_APP_NATIVE( KinectStreamerApp, RendererGl )
