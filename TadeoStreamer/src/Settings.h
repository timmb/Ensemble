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

class Parameter
{
public:
	// path is slash separated
	// e.g. "" or "triggers" or "triggers/my_trigger/part 1"
	Parameter(std::string const& name, std::string const& path="")
	: path(path)
	, name(name)
	{}

	virtual void setup(ci::params::InterfaceGl& params) = 0;
	virtual void writeJson(Json::Value& root) const;
	virtual bool readJson(Json::Value const& root);
	
	std::string path;
	std::string name;
	
protected:
	template <typename JsonOrConstJson>
	JsonOrConstJson& getChild(JsonOrConstJson& root) const;
	virtual void toJson(Json::Value& child) const = 0;
	virtual bool fromJson(Json::Value const& child) = 0;
};

class ParameterFloat : public Parameter
{
public:
	ParameterFloat(float* value, std::string const& name, std::string const& path="");
	virtual void setup(ci::params::InterfaceGl& params);
protected:
	
	virtual void toJson(Json::Value& root) const;
	virtual bool fromJson(Json::Value const& root);
	
	float* value;
};

class ParameterVec3f : public Parameter
{
public:
	ParameterVec3f(ci::Vec3f* value, std::string const& name, std::string const& path="");
	virtual void setup(ci::params::InterfaceGl& params);
	virtual void toJson(Json::Value& root) const;
	virtual bool fromJson(Json::Value const& root);
	
	ci::Vec3f* value;
};


class Settings
{
public:
	bool load(std::string const& jsonFile);
	void setup();
	void save();
	void save(std::string const& filename);
	void snapshot();
	void update(float dt, float elapsedTime);
	void draw();
	
	void addParam(std::shared_ptr<Parameter> parameter);
	
	void addParam(float* value, std::string name, std::string path) {
		addParam(std::shared_ptr<Parameter>(new ParameterFloat(value, name, path)));
	}
	
	void addParam(ci::Vec3f* value, std::string name, std::string path) {
		addParam(std::shared_ptr<Parameter>(new ParameterVec3f(value, name, path)));
	}
	
	std::string ip;
	int port;
	int deviceId;
	std::string deviceName;
	
	/// path is slash separated list of key names, e.g.
	/// "/key1/key2". Will return null value and print
	/// error if value can't be found
	Json::Value get(std::string const& path) const;
	float getFloat(std::string const& path, float defaultValue=0) const;
	std::string getString(std::string const& path, std::string const& defaultValue="") const;
	ci::Vec3f getVec3f(std::string const& path, ci::Vec3f const& defaultValue=ci::Vec3f()) const;

	Settings()
	: ip("127.0.0.1")
	, port(37000)
	, deviceId(0)
	{}

private:
	ci::params::InterfaceGl mParams;
	std::string mJsonFile;
	Json::Value mRoot;
	
	std::vector<std::shared_ptr<Parameter> > mParameters;
};