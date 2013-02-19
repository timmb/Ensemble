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

static const bool NO_KINECT = false;

extern ci::gl::TextureFontRef gFont;

inline void drawCenteredString(std::string const& s)
{
	ci::gl::pushModelView();
	ci::gl::scale(1,-1,1);
	ci::Vec2f offset = gFont->measureString(s);
	gFont->drawString(s, -offset/2);
	ci::gl::popModelView();
}
