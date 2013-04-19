//
//  TriggerZoneManager.cpp
//  TadeoStreamer
//
//  Created by Tim Murray-Browne on 19/04/2013.
//
//

#include "TriggerZoneManager.h"
#include "Kinect.h"
#include "Json/json.h"
#include <boost/algorithm/string.hpp>
#include <set>

using namespace std;
using namespace ci;

TriggerZoneManager::TriggerZoneManager(Settings& settings, Kinect& kinect)
: mSettings(settings)
, mKinect(kinect)
{}

void TriggerZoneManager::setup()
{
	Json::Value triggers = mSettings.get("triggers");
	set<string> names;
	for (auto it=triggers.begin(); it!=triggers.end(); ++it)
	{
		string name = it.key().asString();
		if (names.count(name)>0)
		{
			err("Duplicate trigger: "+name, "TriggerZoneManager");
			continue;
		}
		names.insert(name);
		
		string type = (*it)["type"].asString();
		// case insensitive compare
		if (boost::iequals(type, "cylinder"))
		{
			mTriggers.push_back(std::shared_ptr<TriggerZone>(new CylinderTriggerZone(mSettings, mKinect, name)));
			mTriggers.back()->setup();
		}
		else
		{
			err("Unknown trigger type "+type+" for trigger "+name, "TriggerZoneManager");
		}
	}
}

void TriggerZoneManager::update(float dt, float elapsedTime)
{
	for (auto trig_it=mTriggers.begin(); trig_it!=mTriggers.end(); ++trig_it)
	{
		TriggerZone& trigger = **trig_it;
		trigger.update(dt, elapsedTime);
		trigger.apply(mKinect.pointCloud());
	}
}

void TriggerZoneManager::scene()
{
	for (auto it=mTriggers.begin(); it!=mTriggers.end(); ++it)
	{
		(**it).scene();
	}
}