//
//
//  Created by Tim Murray-Browne on 24/01/2013.
//
//

#include "Hud.h"
#include <boost/algorithm/string.hpp>
#include <iostream>
#include <ostream>

using namespace ci;
using namespace ci::gl;
using namespace std;

namespace {
	const int kMaxNumberOfMessages = 10;
}

Hud::Hud(TextureFontRef font)
: mFont(font)
, mDumpToConsole(false)
{}

void Hud::display(string const& message, string const& origin)
{
	mMessages.push_back(origin + ": " + message);
	while (mMessages.size() > kMaxNumberOfMessages)
	{
		mMessages.pop_front();
	}
	if (mDumpToConsole)
		cout << origin << ": "<<message<<endl;
}


void Hud::displayUntilFurtherNotice(const std::string &message, const std::string &origin)
{
	if (mDumpToConsole && mPermanentMessages.count(origin)>0 && mPermanentMessages.at(origin)!=message)
	{
		cout << origin << ": "<<message<<endl;
	}
	if (message=="" && mPermanentMessages.count(origin)>0)
	{
		mPermanentMessages.erase(origin);
	}
	else
	{
		mPermanentMessages[origin] = message;
	}
}


void Hud::update(float dt, float elapsedTime)
{
	mCurrentTime = elapsedTime;
	const float kTimestampedMessageDuration = 20;
	const int kMaxTimestampedMessages = 100;
	while (mMessagesToDisplayForAWhile.size() > kMaxTimestampedMessages
		   || (!mMessagesToDisplayForAWhile.empty()
			   && mMessagesToDisplayForAWhile.front().timestamp < mCurrentTime - kTimestampedMessageDuration))
	{
		mMessagesToDisplayForAWhile.pop_front();
	}
}


void Hud::displayForAWhile(std::string const& message, std::string const& origin)
{
	TimestampedMessage t ={ mCurrentTime, message, origin };
	mMessagesToDisplayForAWhile.push_back(t);
	if (mDumpToConsole)
		cout << origin << ": "<<message<<endl;
}


void Hud::draw()
{
	gl::enableAlphaBlending();
	gl::color(1,1,1,.8);
	string message = boost::algorithm::join(mMessages, "\n");
	message += '\n';
	for (auto& originMessage: mPermanentMessages)
	{
		message += originMessage.first+": "+originMessage.second+"\n";
	}
	for (auto& timestampedMessage: mMessagesToDisplayForAWhile)
	{
		message += "> "+timestampedMessage.origin+": "+timestampedMessage.message+"\n";
	}
	mFont->drawString(message, Vec2f(20, 20));
	gl::disableAlphaBlending();
	mMessages.clear();
}