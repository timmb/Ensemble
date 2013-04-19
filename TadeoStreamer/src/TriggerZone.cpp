//
//  TriggerZone.cpp
//  TadeoStreamer
//
//  Created by Tim Murray-Browne on 19/04/2013.
//
//

#include "TriggerZone.h"
#include "cinder/gl/gl.h"
#include "cinder/Quaternion.h"
#include "Kinect.h"

using namespace ci;
using namespace std;

TriggerZone::TriggerZone(Settings& settings, Kinect const& kinect, std::string const& name)
: mSettings(settings)
, mName(name)
, mAlpha(0.5)
, mKinect(kinect)
{}

void TriggerZone::setup()
{
	mAlpha = mSettings.getFloat("triggerZoneAlpha");
}

string TriggerZone::path() const
{
	return "triggers/"+mName;
}


CylinderTriggerZone::CylinderTriggerZone(Settings& settings, Kinect const& kinect, std::string const& name)
: TriggerZone(settings, kinect, name)
, mRadius(10)
, mLength(50)
, mBorderThickness(2)
, mAxis(1,0,0)
{
	settings.addParam(&mRadius, "radius", path());
	settings.addParam(&mLength, "length", path());
	settings.addParam(&mMidpoint, "midpoint", path());
	settings.addParam(&mAxis, "axis", path());
	settings.addParam(&mBorderThickness, "border thickness", path());	
}

void CylinderTriggerZone::setup()
{
	TriggerZone::setup();
	mAxis = mAxis.safeNormalized();
	if (mAxis == Vec3f())
		mAxis = Vec3f(1,0,0);
}

void CylinderTriggerZone::scene()
{
	glEnable(GL_DEPTH_TEST);
	glColor4f(1,0,0,1);
	gl::pushModelView();
	gl::translate(mMidpoint);
	gl::rotate(Quatf(Vec3f::yAxis(), mAxis));
	gl::drawCylinder(mRadius, mRadius, mLength, 10, 15);
	gl::popModelView();
}


void CylinderTriggerZone::update(float dt, float elapsedTime)
{
	
}


TriggerZone::PointStatus CylinderTriggerZone::isInside(ci::Vec3f p) const
{
	// translate cylinder to origin
	p -= mMidpoint;
	// project onto axis of cylinder
	Vec3f proj = mAxis * p.dot(mAxis);
	
	float projDistSq = proj.lengthSquared();
	float outerProjRadiusSq = (mLength/2)*(mLength/2);
	float innerProjRadiusSq = (mLength/2-mBorderThickness)*(mLength/2-mBorderThickness);
	PointStatus projStatus =
		projDistSq > outerProjRadiusSq? OUTSIDE
	:   projDistSq > innerProjRadiusSq? BORDERLINE
	:   INSIDE;
	if (projStatus == OUTSIDE)
		return projStatus;
	
	// perpendicular to cylinder
	Vec3f perp = p - proj;
	float perpDistSq = perp.lengthSquared();
	float outerPerpDistSq =(mRadius/2)*(mRadius/2);
	float innerPerpDistSq = (mRadius/2 - mBorderThickness)*(mRadius/2 - mBorderThickness);
	PointStatus perpStatus =
		perpDistSq > outerPerpDistSq? OUTSIDE
	:   perpDistSq > innerPerpDistSq? BORDERLINE
	:   INSIDE;
	
	return std::min(projStatus, perpStatus);
}