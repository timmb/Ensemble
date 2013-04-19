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
#include "cinder/app/App.h"

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
	settings.addParam(new Parameter<float>(&mRadius, "radius", path()));
	settings.addParam(new Parameter<float>(&mLength, "length", path()));
	settings.addParam(new Parameter<Vec3f>(&mMidpoint, "midpoint", path()));
	settings.addParam(new Parameter<Vec3f>(&mAxis, "axis", path()));
	settings.addParam(new Parameter<float>(&mBorderThickness, "border thickness", path()));
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
	gl::enableAdditiveBlending();
	ColorA col = mIsCurrentlyTriggered
		? ColorA(1,1,1,mAlpha)
		: ColorA(1,0,0,mAlpha);
	gl::color(col);
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

void TriggerZone::apply(PointCloud const& pointCloud)
{
	int numInside = 0;
	int numInsideOrBorderline =0;
	for (auto it=pointCloud.begin(); it!=pointCloud.end(); ++it)
	{
		int in = isInside(*it);
		if (in==TriggerZone::INSIDE)
			numInside++;
		if (in>TriggerZone::BORDERLINE)
			numInsideOrBorderline++;
		
		if (mIsCurrentlyTriggered && numInsideOrBorderline >= mNumIntersectionsToTrigger)
		{
			// already playing. stay playing
			return;
		}
		if (!mIsCurrentlyTriggered && numInside >= mNumIntersectionsToTrigger)
		{
			// not play. start playing
			trigger();
			return;
		}
	}
	// if we get here then not enough points inside to carry on playing
	if (mIsCurrentlyTriggered && numInsideOrBorderline < mNumIntersectionsToTrigger)
	{
		endTrigger();
	}
	app::console() << mName << " intersections: "<<numInside << "/"<<numInsideOrBorderline<<endl;
}


void TriggerZone::trigger()
{
	mIsCurrentlyTriggered = true;
	app::console() << mName << " triggered"<<endl;
}

void TriggerZone::endTrigger()
{
	mIsCurrentlyTriggered = false;
	app::console() << mName << " trigger ended" << endl;
}