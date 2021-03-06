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
	~KinectStreamerApp();
	void prepareSettings(Settings* settings);
	void resize();
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

    bool mEnableDrawPointCloud;
    bool mEnableDrawTriggers;
};

KinectStreamerApp::KinectStreamerApp()
: mElapsedTime(-.1)
, mDeviceId(-42)
, mPort(37000)
, mDeviceName("Kinect")
, mIp("127.0.0.1")
, mKinect(mSettings)
, mTriggers(mSettings, mKinect, mOscBroadcaster)
, mEnableDrawPointCloud(true)
, mEnableDrawTriggers(true)
{
	mSettings.addParam(new Parameter<string>(&mIp, "ip", ""));
	mSettings.addParam(new Parameter<int>(&mPort, "port", ""));
	mSettings.addParam(new Parameter<int>(&mDeviceId, "device id", ""));
	mSettings.addParam(new Parameter<string>(&mDeviceName, "device name", ""));
    mSettings.addParam(new Parameter<bool>(&mEnableDrawPointCloud, "Draw point cloud", ""));
    mSettings.addParam(new Parameter<bool>(&mEnableDrawTriggers, "Draw triggers", ""));
}

KinectStreamerApp::~KinectStreamerApp()
{
	mSettings.save();
}

void KinectStreamerApp::prepareSettings(Settings* settings)
{
	settings->setWindowSize(900, 600);
}

void KinectStreamerApp::resize()
{
	CameraPersp cam = mCamera.getCamera();
	cam.setPerspective(cam.getFov(), getWindowAspectRatio(), cam.getNearClip(), cam.getFarClip());
	mCamera.setCurrentCam(cam);
}

void KinectStreamerApp::setup()
{
	setupFont();
	loadJson();
	mKinect.setup(mDeviceId);
	mTriggers.setup();
	mOscBroadcaster.setup(&mKinect);
	mOscBroadcaster.setDestination(mIp, mPort);
	mSettings.setup();
	resetCamera();
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
	mOscBroadcaster.setDestination(mIp, mPort);
	mOscBroadcaster.setKinectName(mDeviceName);
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
    if (mEnableDrawTriggers || mEnableDrawPointCloud)
    {
        glEnable(GL_DEPTH_TEST);
        gl::pushMatrices();
        {
            gl::setMatricesWindow(app::getWindowSize());
            gl::setMatrices(mCamera.getCamera());
            if (mEnableDrawPointCloud)
            {
                gl::color(1,1,1, 1);
                mKinect.scene();
            }
            if (mEnableDrawTriggers)
            {
                gl::color(1,1,1, 1);
                mTriggers.scene();
            }
        }
        gl::popMatrices();
        glDisable(GL_DEPTH_TEST);
    }
	hud().draw();
	mSettings.draw();
}

CINDER_APP_NATIVE( KinectStreamerApp, RendererGl )
