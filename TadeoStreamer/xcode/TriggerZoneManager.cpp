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
#include "OscBroadcaster.h"

using namespace std;
using namespace ci;

TriggerZoneManager::TriggerZoneManager(Settings& settings, Kinect& kinect, OscBroadcaster& osc)
: mSettings(settings)
, mKinect(kinect)
, mOsc(osc)
{}

void TriggerZoneManager::setup()
{
//	Json::Value triggers = mSettings.get("triggers");
//	set<string> names;
//	for (auto it=triggers.begin(); it!=triggers.end(); ++it)
//	{
//		string name = it.key().asString();
//		if (names.count(name)>0)
//		{
//			err("Duplicate trigger: "+name, "TriggerZoneManager");
//			continue;
//		}
//		names.insert(name);
//		
//		auto& typeJson = (*it)["type"];
//		string type = typeJson.asString();
//		// case insensitive compare
//		if (!boost::iequals(type, "cylinder"))
//		{
//			err("Unknown trigger type "+type+" for trigger "+name, "TriggerZoneManager. Defaulting to cylinder.");
//			typeJson = type = "cylinder";
//		}
//		{
//			mTriggers.push_back(std::shared_ptr<TriggerZone>(new CylinderTriggerZone(mSettings, mKinect, name)));
	//			mTriggers.back()->setup();
	//		}
	//	}
	string names[] = { "left_trigger", "middle_trigger", "right_trigger" };
	for (int i=0; i<3; ++i)
	{
		mTriggers.push_back(std::shared_ptr<TriggerZone>(new CylinderTriggerZone(mSettings, mKinect, names[i])));
		mTriggers.back()->setup();
	}
}

void TriggerZoneManager::update(float dt, float elapsedTime)
{
	for (auto trig_it=mTriggers.begin(); trig_it!=mTriggers.end(); ++trig_it)
	{
		TriggerZone& trigger = **trig_it;
		trigger.update(dt, elapsedTime);
		bool newValue = trigger.apply(mKinect.pointCloud());
		if (newValue)
		{
			mOsc.sendTrigger(trigger.name(), trigger.isTriggered());
		}
	}
}

void TriggerZoneManager::scene()
{
	for (auto it=mTriggers.begin(); it!=mTriggers.end(); ++it)
	{
		(**it).scene();
	}
}