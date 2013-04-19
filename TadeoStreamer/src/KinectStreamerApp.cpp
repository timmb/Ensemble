#include "cinder/app/AppNative.h"
#include "cinder/gl/gl.h"

#include "Kinect.h"
#include "OscBroadcaster.h"
#include "Settings.h"


using namespace ci;
using namespace ci::app;
using namespace std;

class KinectStreamerApp : public AppNative {
  public:
	KinectStreamerApp();
	void setup();
	void mouseDown( MouseEvent event );
	void mouseDrag(MouseEvent event);
	void keyDown(KeyEvent event);
	void update();
	void draw();
	
	
private:
	void loadJson();

	::Settings mSettings;
	Kinect mKinect;
	OscBroadcaster mOscBroadcaster;
	double mElapsedTime;
	int mDeviceId;
};

KinectStreamerApp::KinectStreamerApp()
: mElapsedTime(-.1)
, mDeviceId(-42)
, mKinect(mSettings)
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
	if (filename=="")
	{
		console() << "Error: Could not load kinectStreamerSettings.json from assets folder." << endl;
		return;
	}
	mSettings.load(filename);
	mOscBroadcaster.setDestination(mSettings.ip, mSettings.port);
	mOscBroadcaster.setKinectName(mSettings.deviceName);
}

void KinectStreamerApp::keyDown(KeyEvent event)
{
	if (event.getChar()==' ')
	{
		loadJson();
	}
	sIsShiftDown = event.isShiftDown();
}

void KinectStreamerApp::mouseDown( MouseEvent event )
{
	mKinect.mouseDown(event);
}

void KinectStreamerApp::mouseDrag(MouseEvent event)
{
	mKinect.mouseDrag(event);
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
