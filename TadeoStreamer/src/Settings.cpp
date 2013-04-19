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
#include <boost/tokenizer.hpp>
#include <ctime>

using namespace std;
using namespace ci;

bool Settings::load(string const& filename)
{
	mJsonFile = filename;
	
	
	ifstream in(filename.c_str(), ifstream::in);
	bool success = true;
	try {
		in >> mRoot;
	}
	catch (std::runtime_error& e)
	{
		err("Error parsing json file "+filename, "Settings");
		success = false;
	}
	if (success)
	{
		app::console() << "successful parse" << endl;;
		Json::Value ip = mRoot["ip"];
		Json::Value port = mRoot["port"];
		Json::Value deviceId = mRoot["deviceId"];
		Json::Value deviceName = mRoot["deviceName"];
		success = ip.isString() && port.isIntegral() && deviceId.isIntegral() && deviceName.isString();
		if (success)
		{
			this->ip = ip.asString();
			this->port = port.asInt();
			this->deviceId = deviceId.asInt();
			this->deviceName = deviceName.asString();
		}
		for (int i=0; i<mParameters.size(); ++i)
		{
			mParameters[i]->readJson(mRoot);
		}
		hud().displayUntilFurtherNotice("Successfully loaded "+filename, "JSON");
	}
	if (!success)
	{
		hud().displayUntilFurtherNotice("Problem with json file.", "JSON");
	}
	return success;
}

void Settings::save()
{
	save(mJsonFile);
}


void Settings::snapshot()
{
	// get date string
	time_t t = time(0);   // get time now
    struct tm * now = localtime( & t );
	char buf[128];
	strftime(buf, sizeof(buf), "%Y-%m-%d", now);
	
	save(mJsonFile+buf+".json");
}

void Settings::save(string const& filename)
{
	for (auto it=mParameters.begin(); it!=mParameters.end(); ++it)
	{
		(**it).writeJson(mRoot);
	}
	
	ofstream out(filename.c_str(), ofstream::out);
	try
	{
		out << mRoot;
	}
	catch (...)
	{
		err("Error saving JSON settings file "+filename, "Settings");
		if (out.bad()) {
			err("Problem with writing file", "Settings");
		}
	}
}


void Settings::setup()
{
	mParams = params::InterfaceGl("TadeoStreamer", Vec2i(400,600));
	mParams.addButton("Save", std::bind((void (Settings::*)())&Settings::save, this));
	mParams.addButton("Save snapshot", std::bind(&Settings::snapshot, this));
	for (auto it=mParameters.begin(); it!=mParameters.end(); ++it)
	{
		(**it).setup(mParams);
	}
}

void Settings::update(float dt, float elapsed)
{

}

Json::Value Settings::get(string const& path) const
{
	Json::Value v = mRoot;
	typedef boost::tokenizer<boost::char_separator<char> >
    tokenizer;
	boost::char_separator<char> sep("/");
	tokenizer tokens(path, sep);
	string prevToken = "/";
	for (tokenizer::iterator tok_iter = tokens.begin();
		 tok_iter != tokens.end(); ++tok_iter)
	{
		v = v[*tok_iter];
		if (v.isNull())
		{
			string err = "Unable to find key "+*tok_iter+" in "+prevToken+".";
			hud().displayUntilFurtherNotice(err, "Json file "+path);
			break;
		}
	}
	return v;
}

float Settings::getFloat(string const& path, float defaultValue) const
{
	Json::Value v = get(path);
	if (v.isNull())
		return defaultValue;
	if (!v.isConvertibleTo(Json::realValue))
	{
		hud().displayUntilFurtherNotice("Unable to convert to real number", "Setting "+path);
		return defaultValue;
	}
	return v.asFloat();
}


string Settings::getString(string const& path, string const& defaultValue) const
{
	Json::Value v = get(path);
	if (v.isNull())
		return defaultValue;
	if (!v.isConvertibleTo(Json::stringValue))
	{
		hud().displayUntilFurtherNotice("Unable to convert to string", "Setting "+path);
		return defaultValue;
	}
	return v.asString();
}


Vec3f Settings::getVec3f(string const& path, Vec3f const& defaultValue) const
{
	Json::Value x = get(path+"/x");
	Json::Value y = get(path+"/y");
	Json::Value z = get(path+"/z");
	Json::Value values[3] = {x,y,z};
	string valueNames[3] = {"x","y","z"};
	for (int i=0; i<3; ++i)
	{
		if (values[i].isNull())
			return defaultValue;
		if (!values[i].isConvertibleTo(Json::realValue))
		{
			hud().displayUntilFurtherNotice("Unable to convert to real", "Setting "+path+"/"+valueNames[i]);
			return defaultValue;
		}
	}
	return Vec3f(x.asFloat(), y.asFloat(), z.asFloat());
}


void Settings::addParam(std::shared_ptr<Parameter> parameter)
{
	mParameters.push_back(parameter);
}


void Settings::draw()
{
	mParams.draw();
}




/////////

ParameterFloat::ParameterFloat(float* value, std::string const& name, std::string const& path)
: Parameter(name, path)
, value(value)
{}

void ParameterFloat::setup(params::InterfaceGl& params)
{
	params.addParam(name, value, "group="+path);
}

void ParameterFloat::toJson(Json::Value& root) const
{
	root = *value;
}

bool ParameterFloat::fromJson(Json::Value& root)
{
	if (root.isConvertibleTo(Json::realValue))
	{
		*value = root.asFloat();
		return true;
	}
	else
	{
		return false;
	}
}


ParameterVec3f::ParameterVec3f(Vec3f* value, std::string const& name, std::string const& path)
: Parameter(name, path)
, value(value)
{}

void ParameterVec3f::setup(params::InterfaceGl& params){
	params.addParam(name, value, "group="+path);
}

void ParameterVec3f::toJson(Json::Value& root) const
{
	root["x"] = value->x;
	root["y"] = value->y;
	root["z"] = value->z;
}

	bool ParameterVec3f::fromJson(Json::Value& root)
{
	if (root["x"].isConvertibleTo(Json::realValue)
		&& root["y"].isConvertibleTo(Json::realValue)
		&& root["z"].isConvertibleTo(Json::realValue))
	{
		value->x = root["x"].asFloat();
		value->y = root["y"].asFloat();
		value->z = root["z"].asFloat();
		return true;
	}
	return false;
}


Json::Value Parameter::getChild(Json::Value& root) const
{
	Json::Value child = root;
	typedef boost::tokenizer<boost::char_separator<char> >
    tokenizer;
	boost::char_separator<char> sep("/");
	tokenizer tokens(path+"/"+name, sep);
	string prevToken = "/";
	for (tokenizer::iterator tok_iter = tokens.begin();
		 tok_iter != tokens.end(); ++tok_iter)
	{
		child = child[*tok_iter];
	}
	return child;
}

void Parameter::writeJson(Json::Value& root) const
{
	Json::Value child = getChild(root);
	toJson(child);
}


bool Parameter::readJson(Json::Value& root)
{
	Json::Value child = getChild(root);
	return fromJson(child);
}


