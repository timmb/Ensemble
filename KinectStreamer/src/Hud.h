//
//
//  Created by Tim Murray-Browne on 19/02/2013.
//
//


#pragma once
#include "cinder/gl/TextureFont.h"
#include <string>
#include <vector>
#include <deque>


class Hud
{
public:
	Hud(ci::gl::TextureFontRef font);
	
	/// Displays just this frame
	void display(std::string const& message, std::string const& origin="");
	void displayUntilFurtherNotice(std::string const& message, std::string const& origin);
	void displayForAWhile(std::string const& message, std::string const& origin);
	void update(float dt, float elapsedTime);
	void draw();
	
	/// If true everything displayed is also dumpted to console
	bool mDumpToConsole;
	
private:
	float mCurrentTime;
	struct TimestampedMessage
	{
		float timestamp;
		std::string message;
		std::string origin;
	};
	ci::gl::TextureFontRef mFont;
	std::deque<TimestampedMessage> mMessagesToDisplayForAWhile;
	std::deque<std::string> mMessages;
	std::map<std::string,std::string> mPermanentMessages;
};
