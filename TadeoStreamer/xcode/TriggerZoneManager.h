//
//  TriggerZoneManager.h
//  TadeoStreamer
//
//  Created by Tim Murray-Browne on 19/04/2013.
//
//

#pragma once

#include "Settings.h"
#include "Common.h"
#include "TriggerZone.h"
class Kinect;

class TriggerZoneManager
{
public:
	TriggerZoneManager(Settings& settings, Kinect& kinect);
	
	void setup();
	void update(float dt, float elapsedTime);
	void scene();
	
private:
	Settings& mSettings;
	Kinect& mKinect;
	
	std::vector<std::shared_ptr<TriggerZone> > mTriggers;
};