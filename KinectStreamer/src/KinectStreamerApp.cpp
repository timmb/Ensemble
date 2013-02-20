#include "cinder/app/AppNative.h"
#include "cinder/gl/gl.h"

#include "Kinect.h"

using namespace ci;
using namespace ci::app;
using namespace std;

class KinectStreamerApp : public AppNative {
  public:
	KinectStreamerApp();
	void setup();
	void mouseDown( MouseEvent event );	
	void update();
	void draw();
	
private:
	Kinect mKinect;
	double mElapsedTime;
};

KinectStreamerApp::KinectStreamerApp()
: mElapsedTime(-.1)
{}

void KinectStreamerApp::setup()
{
	setupFont();
	mKinect.setup();
}

void KinectStreamerApp::mouseDown( MouseEvent event )
{
}

void KinectStreamerApp::update()
{
	double elapsedTime = getElapsedSeconds();
	double dt = elapsedTime - mElapsedTime;
	mElapsedTime = elapsedTime;
	
	mKinect.update(dt);
}

void KinectStreamerApp::draw()
{
	// clear out the window with black
	gl::clear( Color( 0, 0, 0 ) );
	mKinect.draw();
	hud().draw();
}

CINDER_APP_NATIVE( KinectStreamerApp, RendererGl )
