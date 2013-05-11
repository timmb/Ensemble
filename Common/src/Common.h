//
//  Common.h
//  ciEnsemble
//
//  Created by Tim Murray-Browne on 22/01/2013.
//
//
#pragma once

#include <iostream>
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

std::string toString(ci::osc::Message const& m);
