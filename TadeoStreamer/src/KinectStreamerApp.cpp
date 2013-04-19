#include "cinder/app/AppNative.h"
#include "cinder/gl/gl.h"

#include "Kinect.h"
#include "OscBroadcaster.h"
#include "Settings.h"
#include "TriggerZoneManager.h"
#include "cinder/MayaCamUI.h"

using namespace ci;
using namespace ci::app;
using namespace std;

class KinectStreamerApp : public AppNative {
  public:
	KinectStreamerApp();
	void prepareSettings(Settings* settings);
	void resize(ResizeEvent event);
	void setup();
	void mouseDown( MouseEvent event );
	void mouseDrag(MouseEvent event);
	void keyDown(KeyEvent event);
	void update();
	void draw();
	
	void resetCamera();
	
private:
	void loadJson();

	::Settings mSettings;
	Kinect mKinect;
	OscBroadcaster mOscBroadcaster;
	TriggerZoneManager mTriggers;
	double mElapsedTime;
	ci::MayaCamUI mCamera;
	
	std::string mIp;
	int mPort;
	int mDeviceId;
	std::string mDeviceName;

};

KinectStreamerApp::KinectStreamerApp()
: mElapsedTime(-.1)
, mDeviceId(-42)
, mPort(37000)
, mDeviceName("Kinect")
, mIp("127.0.0.1")
, mKinect(mSettings)
, mTriggers(mSettings, mKinect)
{
	mSettings.addParam(new Parameter<string>(&mIp, "ip", ""));
	mSettings.addParam(new Parameter<int>(&mPort, "port", ""));
	mSettings.addParam(new Parameter<int>(&mDeviceId, "device id", ""));
	mSettings.addParam(new Parameter<string>(&mDeviceName, "device name", ""));
}

void KinectStreamerApp::prepareSettings(Settings* settings)
{
	settings->setWindowSize(900, 600);
}

void KinectStreamerApp::resize(ResizeEvent event)
{
	CameraPersp cam = mCamera.getCamera();
	cam.setPerspective(cam.getFov(), event.getAspectRatio(), cam.getNearClip(), cam.getFarClip());
	mCamera.setCurrentCam(cam);
}

void KinectStreamerApp::setup()
{
	setupFont();
	loadJson();
	mKinect.setup(mDeviceId);
	mTriggers.setup();
	mOscBroadcaster.setup(&mKinect);
//	mOscBroadcaster.setDestination("127.0.0.1", 37000);
	resetCamera();
	mSettings.setup();
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

void KinectStreamerApp::resetCamera()
{
	
	CameraPersp cam(app::getWindowWidth(), app::getWindowHeight(), 60, 0.01, 100000);
	cam.setEyePoint(Vec3f(0,0,0));
	cam.setCenterOfInterestPoint(Vec3f(0,0,3000));
	//	cam.setEyePoint(Vec3f(0,0,1));
	//	cam.lookAt(Vec3f());
	mCamera.setCurrentCam(cam);
}

void KinectStreamerApp::mouseDown( MouseEvent event )
{
	mCamera.mouseDown(event.getPos());
}

void KinectStreamerApp::mouseDrag(MouseEvent event)
{
	mCamera.mouseDrag(event.getPos(), event.isLeftDown(), event.isMiddleDown()||sIsShiftDown, event.isRightDown());
}

void KinectStreamerApp::update()
{
	double elapsedTime = getElapsedSeconds();
	double dt = elapsedTime - mElapsedTime;
	mElapsedTime = elapsedTime;
	
	mKinect.update(dt, mElapsedTime);
	mTriggers.update(dt, mElapsedTime);
	mOscBroadcaster.update(dt, mElapsedTime);
	hud().update(dt, mElapsedTime);
}

void KinectStreamerApp::draw()
{
	// clear out the window with black
	gl::clear( Color( 0, 0, 0 ) );
	glEnable(GL_DEPTH_TEST);
	gl::pushMatrices();
	{
		gl::setMatricesWindow(app::getWindowSize());
		gl::setMatrices(mCamera.getCamera());
		gl::color(1,1,1, 1);
		mKinect.scene();
		gl::color(1,1,1, 1);
		mTriggers.scene();
	}
	gl::popMatrices();
	glDisable(GL_DEPTH_TEST);
	hud().draw();
	mSettings.draw();
}

CINDER_APP_NATIVE( KinectStreamerApp, RendererGl )
