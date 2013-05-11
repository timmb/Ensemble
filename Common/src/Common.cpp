//
//  Common.cpp
//  ciEnsemble
//
//  Created by Tim Murray-Browne on 22/01/2013.
//
//

#include "Common.h"
#include <sstream>

using namespace ci;
using namespace ci::gl;
using namespace std;

bool sIsShiftDown = false;
float gMouseX = 0.f;
float gMouseY = 0.f;

namespace {
	TextureFontRef fFont;
	Hud* fHud = NULL;
	bool fFontAndHudAreInitialized = false;
}

void setupFont()
{
	fFont = gl::TextureFont::create(Font("Helvetica", 16));
	fHud = new Hud(fFont);
	fFontAndHudAreInitialized = true;
}

TextureFontRef& statusFont()
{
	assert(fFontAndHudAreInitialized);
	return fFont;
}

Hud& hud()
{
	assert(fFontAndHudAreInitialized);
	return *fHud;
}

void drawCenteredString(std::string const& s)
{
	ci::gl::pushModelView();
	ci::gl::scale(1,-1,1);
	ci::Vec2f offset = statusFont()->measureString(s);
	statusFont()->drawString(s, -offset/2);
	ci::gl::popModelView();
}


void err(std::string const& errorMessage, std::string const& origin) {
	std::cout << origin << ": " << errorMessage << std::endl;
	hud().displayForAWhile(errorMessage, origin);
}

string toString(osc::Message const& m)
{
	stringstream s;
	s << '[' << m.getAddress() << ' ';
	for (int i=0; i<m.getNumArgs(); ++i)
	{
		s << m.getArgAsString(i, true);
	}
	s << ']';
	return s.str();
}


vector<string> split(string const& str, string const& delimiters)
{
	vector<string> l;
	int pos = 0;
	while (pos<str.size())
	{
		int tok = str.find_first_of(delimiters, pos);
		if (tok==string::npos)
			tok = str.size();
		int len = tok - pos;
		if (len>0)
			l.push_back(str.substr(pos, len));
		pos = tok+1;
	}
	return l;
}