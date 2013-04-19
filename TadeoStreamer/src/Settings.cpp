//
//  JsonLoader.cpp
//  KinectStreamer
//
//  Created by Tim Murray-Browne on 20/02/2013.
//
//

#include "Settings.h"
#include "Hud.h"
#include "Common.h"
#include "cinder/app/AppBasic.h"
#include "json/json.h"
#include <fstream>
#include <iostream>

using namespace std;
using namespace ci;

bool Settings::load(string const& filename)
{
	Json::Value root;
	ifstream in(filename.c_str(), ifstream::in);
	in >> root;
	bool success = true;
	if (success)
	{
		app::console() << "successful parse";
		Json::Value ip = root["ip"];
		Json::Value port = root["port"];
		Json::Value deviceId = root["deviceId"];
		Json::Value deviceName = root["deviceName"];
		success = ip.isString() && port.isIntegral() && deviceId.isIntegral() && deviceName.isString();
		if (success)
		{
			this->ip = ip.asString();
			this->port = port.asInt();
			this->deviceId = deviceId.asInt();
			this->deviceName = deviceName.asString();
			hud().displayUntilFurtherNotice("Successfully loaded "+filename, "JSON");
		}
	}
	if (!success)
	{
		hud().displayUntilFurtherNotice("Unable to load json file.", "JSON");
	}
	return success;
}