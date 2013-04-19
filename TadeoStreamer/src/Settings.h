//
//  JsonLoader.h
//  KinectStreamer
//
//  Created by Tim Murray-Browne on 20/02/2013.
//
//

#pragma once

#include "json/json.h"
#include "cinder/params/Params.h"

class Settings
{
public:
	bool load(std::string const& jsonFile);
	void reload();
	void save(std::string const& jsonFile);
	void draw();
	
	std::string ip;
	int port;
	int deviceId;
	std::string deviceName;

	Settings()
	: ip("127.0.0.1")
	, port(37000)
	, deviceId(0)
	{}

private:
	ci::params::InterfaceGl mParams;
	std::string mJsonFile;
};