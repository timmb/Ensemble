//
//  Common.h
//  ciEnsemble
//
//  Created by Tim Murray-Browne on 22/01/2013.
//
//
#pragma once

#include <iostream>
#include <string>
#include <vector>
#include "cinder/gl/TextureFont.h"
#include "cinder/gl/gl.h"
#include "Hud.h"
#include "Settings.h"
#include "OscMessage.h"

static const bool NO_KINECT = false;

/// Needs to be called in the main app's setup() function
void setupFont();
ci::gl::TextureFontRef& statusFont();
Hud& hud();

void drawCenteredString(std::string const& s);

void err(std::string const& errorMessage, std::string const& origin);

extern bool sIsShiftDown;
extern float gMouseX;
extern float gMouseY;

std::string toString(ci::osc::Message const& m);

struct JointParameters
{
	float expressionDecay;
	int velocitySmoothing;
	
	JointParameters()
	: expressionDecay(0.5f)
	, velocitySmoothing(0)
	{}
	
	void registerParams(Settings& settings)
	{
		settings.addParam(new Parameter<float>(&expressionDecay, "Expression decay", "", "min=0 max=1 step=0.001"));
		settings.addParam(new Parameter<int>(&velocitySmoothing, "Velocity smoothing", "", "min=0 max=400"));
	}
};

std::vector<std::string> split(std::string const& str, std::string const& delimiters);
