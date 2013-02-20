//
//
//  Created by Tim Murray-Browne on 19/02/2013.
//
//


#pragma once
#include "cinder/gl/TextureFont.h"
#include <string>
#include <vector>


class Hud
{
public:
	Hud(ci::gl::TextureFontRef font);
	
	void display(std::string const& message, std::string const& origin="");
	virtual void draw();
	
private:
	ci::gl::TextureFontRef mFont;
	std::deque<std::string> mMessages;
};
