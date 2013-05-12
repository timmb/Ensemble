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
#include <ctime>

using namespace std;
using namespace ci;

bool Settings::reload()
{
	if (mJsonFile=="")
		return false;
	return load(mJsonFile);
}

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
	Json::Value root;
	for (auto it=mParameters.begin(); it!=mParameters.end(); ++it)
	{
		(**it).writeJson(root);
	}
	
	ofstream out(filename.c_str(), ofstream::out);
	try
	{
		out << root;
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
	mParams = params::InterfaceGl("Settings", Vec2i(250,400));
	mParams.addButton("Save", std::bind((void (Settings::*)())&Settings::save, this));
	mParams.addButton("Save snapshot", std::bind(&Settings::snapshot, this));
	for (int i=0; i<mParameters.size(); ++i)
	{
		mParameters[i]->readJson(mRoot);
	}
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
	// for now, find final /
	int s = path.find_last_of('/');
	if (s==string::npos)
		s = 0;
	string base = path.substr(0, s);
	string name = path.substr(s);
	if (base!="")
		return mRoot[base][name];
	else
		return mRoot[name];
//	
//	Json::Value v = mRoot;
//	typedef boost::tokenizer<boost::char_separator<char> >
//    tokenizer;
//	boost::char_separator<char> sep("/");
//	tokenizer tokens(path, sep);
//	string prevToken = "/";
//	for (tokenizer::iterator tok_iter = tokens.begin();
//		 tok_iter != tokens.end(); ++tok_iter)
//	{
//		v = v[*tok_iter];
//		if (v.isNull())
//		{
//			string err = "Unable to find key "+*tok_iter+" in "+prevToken+".";
//			hud().displayUntilFurtherNotice(err, "Json file "+path);
//			break;
//		}
//	}
//	return v;
}

//float Settings::getFloat(string const& path, float defaultValue) const
//{
//	Json::Value v = get(path);
//	if (v.isNull())
//		return defaultValue;
//	if (!v.isConvertibleTo(Json::realValue))
//	{
//		hud().displayUntilFurtherNotice("Unable to convert to real number", "Setting "+path);
//		return defaultValue;
//	}
//	return v.asFloat();
//}
//
//
//string Settings::getString(string const& path, string const& defaultValue) const
//{
//	Json::Value v = get(path);
//	if (v.isNull())
//		return defaultValue;
//	if (!v.isConvertibleTo(Json::stringValue))
//	{
//		hud().displayUntilFurtherNotice("Unable to convert to string", "Setting "+path);
//		return defaultValue;
//	}
//	return v.asString();
//}
//
//
//Vec3f Settings::getVec3f(string const& path, Vec3f const& defaultValue) const
//{
//	Json::Value x = get(path+"/x");
//	Json::Value y = get(path+"/y");
//	Json::Value z = get(path+"/z");
//	Json::Value values[3] = {x,y,z};
//	string valueNames[3] = {"x","y","z"};
//	for (int i=0; i<3; ++i)
//	{
//		if (values[i].isNull())
//			return defaultValue;
//		if (!values[i].isConvertibleTo(Json::realValue))
//		{
//			hud().displayUntilFurtherNotice("Unable to convert to real", "Setting "+path+"/"+valueNames[i]);
//			return defaultValue;
//		}
//	}
//	return Vec3f(x.asFloat(), y.asFloat(), z.asFloat());
//}


void Settings::addParam(std::shared_ptr<BaseParameter> parameter)
{
	mParameters.push_back(parameter);
}


void Settings::draw()
{
	mParams.draw();
}




////////


void BaseParameter::writeJson(Json::Value& root) const
{
	if (writeToJson)
	{
		Json::Value& child = getChild(root);
		toJson(child);
	}
}


bool BaseParameter::readJson(Json::Value const& root)
{
	if (loadFromJson)
	{
		Json::Value const& child = getChild(root);
		return fromJson(child);
	}
}


