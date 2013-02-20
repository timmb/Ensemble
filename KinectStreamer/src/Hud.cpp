//
//
//  Created by Tim Murray-Browne on 24/01/2013.
//
//

#include "Hud.h"
#include <boost/algorithm/string.hpp>

using namespace ci;
using namespace ci::gl;
using namespace std;

namespace {
	const int kMaxNumberOfMessages = 10;
}

Hud::Hud(TextureFontRef font)
: mFont(font)
{}

void Hud::display(string const& message)
{
	mMessages.push_back(message);
	while (mMessages.size() > kMaxNumberOfMessages)
	{
		mMessages.pop_front();
	}
}


void Hud::draw()
{
	gl::enableAlphaBlending();
	gl::color(1,1,1,.8);
	mFont->drawString(boost::algorithm::join(mMessages, "\n"), Vec2f(20, 20));
	gl::disableAlphaBlending();
	mMessages.clear();
}