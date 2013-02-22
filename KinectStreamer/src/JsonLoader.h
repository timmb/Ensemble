//
//  JsonLoader.h
//  KinectStreamer
//
//  Created by Tim Murray-Browne on 20/02/2013.
//
//

#pragma once

#include "json/json.h"

class JsonLoader
{
public:
	JsonLoader();
	void setup(std::string const& jsonFile);
	void reload();
	
	
private:
	std::string mJsonFile;
};