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
#include "OscMessage.h"

static const bool NO_KINECT = false;

/// Needs to be called in the main app's setup() function
void setupFont();
ci::gl::TextureFontRef& statusFont();
Hud& hud();

void drawCenteredString(std::string const& s);


std::string toString(ci::osc::Message const& m);

