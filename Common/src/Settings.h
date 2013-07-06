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
#include "cinder/Cinder.h"
#include <boost/tokenizer.hpp>


// To avoid having to specialise the Parameter class
static bool operator>>(Json::Value const& child, float& value)
{
	if (!child.isConvertibleTo(Json::realValue))
		return false;
	value = child.asFloat();
	return true;
}

static bool operator>>(Json::Value const& child, int& value)
{
	if (!child.isConvertibleTo(Json::intValue))
		return false;
	value = child.asInt();
	return true;
}

static bool operator>>(Json::Value const& child, bool& value)
{
	if (!child.isConvertibleTo(Json::booleanValue))
		return false;
	value = child.asBool();
	return true;
}

static bool operator>>(Json::Value const& child, ci::Vec3f& value)
{
	if (child["x"].isConvertibleTo(Json::realValue)
		&& child["y"].isConvertibleTo(Json::realValue)
		&& child["z"].isConvertibleTo(Json::realValue))
	{
		value.x = child["x"].asFloat();
		value.y = child["y"].asFloat();
		value.z = child["z"].asFloat();
		return true;
	}
	return false;
}

static bool operator>>(Json::Value const& child, std::string& value)
{
	if (!child.isConvertibleTo(Json::stringValue))
		return false;
	value = child.asString();
	return true;
}

template <typename T>
Json::Value& operator<<(Json::Value& lhs, T const& rhs)
{
	lhs = rhs;
	return lhs;
}

static 
Json::Value& operator<<(Json::Value& lhs, ci::Vec3f const& rhs)
{
	lhs["x"] = rhs.x;
	lhs["y"] = rhs.y;
	lhs["z"] = rhs.z;
	return lhs;
}



class BaseParameter
{
public:
	// path is slash separated
	// e.g. "" or "triggers" or "triggers/my_trigger/part 1"
	BaseParameter(std::string const& name, std::string const& path, std::string const& options, bool loadFromJson, bool writeToJson)
	: path(path)
	, name(name)
	, options(options)
	, loadFromJson(loadFromJson)
	, writeToJson(writeToJson)
	{}

	virtual void setup(ci::params::InterfaceGl& params) = 0;
	virtual void writeJson(Json::Value& root) const;
	virtual bool readJson(Json::Value const& root);
	
	std::string path;
	std::string name;
	std::string options;
	bool loadFromJson;
	bool writeToJson;
	
protected:
	template <typename JsonOrConstJson>
	JsonOrConstJson& getChild(JsonOrConstJson& root) const;
	virtual void toJson(Json::Value& child) const = 0;
	virtual bool fromJson(Json::Value const& child) = 0;
};

// Main class to represent parameters
template <typename T>
class Parameter : public BaseParameter
{
public:
	Parameter(T* value, std::string const& name, std::string const& path="", std::string const& options="", bool loadFromJson=true, bool writeToJson=true)
	: BaseParameter(name, path, options, loadFromJson, writeToJson)
	, value(value)
	{}
	
	virtual void setup(ci::params::InterfaceGl& params)
	{
		params.addParam(path+" "+name, value, options+(path==""?"":" group="+path));
	}
	
protected:
	virtual void toJson(Json::Value& child) const
	{
		child << *value;
	}
	
	virtual bool fromJson(Json::Value const& child)
	{
		T tempValue;
		if (child >> tempValue)
		{
			child >> *value;
			return true;
		}
		else
			return false;
	}
	
	T* value;
};




class Settings
{
public:
	bool load(std::string const& jsonFile);
	bool reload();
	void setup();
	void save();
	void save(std::string const& filename);
	void snapshot();
	void update(float dt, float elapsedTime);
	void draw();
	
	void addParam(std::shared_ptr<BaseParameter> parameter);
	/// Takes ownership of \p parameter
	void addParam(BaseParameter* parameter)
	{
		addParam(std::shared_ptr<BaseParameter>(parameter));
	}
	
	/// path is slash separated list of key names, e.g.
	/// "/key1/key2".
	Json::Value get(std::string const& basepath) const;
//	float getFloat(std::string const& path, float defaultValue=0) const;
//	std::string getString(std::string const& path, std::string const& defaultValue="") const;
//	ci::Vec3f getVec3f(std::string const& path, ci::Vec3f const& defaultValue=ci::Vec3f()) const;

	ci::params::InterfaceGl& antTweakBar() { return mParams; }
private:
	ci::params::InterfaceGl mParams;
	std::string mJsonFile;
	Json::Value mRoot;
	
	std::vector<std::shared_ptr<BaseParameter> > mParameters;
};



template <typename T>
T& BaseParameter::getChild(T& root) const
{
	if (path=="")
		return root[name];
	else
		return root[path][name];
//	T* child = &root;
//	typedef boost::tokenizer<boost::char_separator<char> >
//    tokenizer;
//	boost::char_separator<char> sep("/");
//	tokenizer tokens(path+"/"+name, sep);
//	std::string prevToken = "/";
//	for (tokenizer::iterator tok_iter = tokens.begin();
//		 tok_iter != tokens.end(); ++tok_iter)
//	{
//		child = &(*child)[*tok_iter];
//	}
//	return *child;
}


