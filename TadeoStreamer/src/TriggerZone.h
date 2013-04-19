//
//  TriggerZone.h
//  TadeoStreamer
//
//  Created by Tim Murray-Browne on 19/04/2013.
//
//

#pragma once

#include "Common.h"
#include "cinder/Cinder.h"

#include "Kinect.h"

class TriggerZone
{
public:
	static const int INSIDE = 1;
	static const int BORDERLINE = 0;
	static const int OUTSIDE = -1;
	typedef int PointStatus;
	
	TriggerZone(Settings& settings, Kinect const& kinect, std::string const& name);
	virtual void setup();
	virtual void update(float dt, float elapsedTime) {}
	virtual void scene() {}
	
	void apply(PointCloud const& p);
	
	void trigger();
	void endTrigger();
	
	float mAlpha;
	int mNumIntersectionsToTrigger;
	
protected:
	virtual PointStatus isInside(ci::Vec3f p) const = 0;

	
	Settings& mSettings;
	Kinect const& mKinect;
	std::string mName;
	std::string path() const;

	bool mIsCurrentlyTriggered;

};


class CylinderTriggerZone : public TriggerZone
{
public:
	CylinderTriggerZone(Settings& settings, Kinect const& kinect, std::string const& name);
	virtual void setup();
	virtual void scene();
	virtual void update(float dt, float elapsedTime);
	
protected:
	PointStatus isInside(ci::Vec3f p) const;

private:
	ci::Vec3f mMidpoint;
	// axis is normalized
	ci::Vec3f mAxis;
	float mRadius;
	float mBorderThickness;
	float mLength;
};