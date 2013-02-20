//
//  Kinect.cpp
//  Ensemble
//
//  Created by Tim Murray-Browne on 03/01/2013.
//
//

#include "Kinect.h"
#include "tmbUtils.h"
#include "cinder/app/AppBasic.h"
#include "cinder/ImageIo.h"
#include <boost/algorithm/string/join.hpp>
#include <boost/foreach.hpp>
#include <limits>

using namespace tmb;
using namespace ci;
using namespace ci::app;
using namespace std;
using namespace V;

#define CHECK(xn_result) if (xn_result!=XN_STATUS_OK) ERR(xnGetStatusString(xn_result));

typedef boost::shared_lock<boost::shared_mutex> ReadLock;
typedef boost::unique_lock<boost::shared_mutex> WriteLock;


Kinect::~Kinect()
{
}



void Kinect::setup()
{
	mFont = gl::TextureFont::create(Font("Helvetica", 16));
	mDepthSize = Vec2i(640, 480);
	mColorSize = Vec2i(640, 480);
	OpenNIDeviceManager::USE_THREAD = false;
	mOpenNI = OpenNIDeviceManager::InstancePtr();
	if (!NO_KINECT)
	{
		mOpenNI->createDevices(1, NODE_TYPE_IMAGE | NODE_TYPE_DEPTH | NODE_TYPE_SCENE | NODE_TYPE_USER);
		mDevice = mOpenNI->getDevice(0);
		assert(mDevice);
		mDevice->setDepthShiftMul(3);
	}
	mColor = Surface8u(mColorSize.x, mColorSize.y, false);
	mDepth = Channel16u(mDepthSize.x, mDepthSize.y);
	
	mOpenNI->SetPrimaryBuffer(0, NODE_TYPE_USER);
}


void Kinect::update(float dt)
{
	double t = app::App::get()->getElapsedSeconds();
	mOpenNI->update();
	double dur = app::App::get()->getElapsedSeconds() - t;
//	cout << dur << endl;
	hud().display("OpenNI update: "+toString(dur)+"ms");
	
	if (!NO_KINECT)
	{
		if ( mDevice->_isImageOn && mDevice->getImageGenerator()->IsValid() && mDevice->isImageDataNew() )
		{
			uint8_t *pixels = mDevice->getColorMap();
			memcpy(mColor.getData(), pixels, mColor.getRowBytes()*mColor.getHeight());
		}
		if ( mDevice->_isDepthOn && mDevice->getDepthGenerator()->IsValid() && mDevice->isDepthDataNew() )
		{
			uint16_t *pixels = mDevice->getDepthMap();
			memcpy(mDepth.getData(), pixels, mDepth.getRowBytes()*mDepth.getHeight());
		}
		if (!mDevice->_isUserOn)
		{
			mUsers.clear();
		}
		else if (mDevice->isUserDataNew())
		{
			OpenNIUserList users = mOpenNI->getUserList();
			// first eliminate dead users
			for (auto it=mUsers.begin(); it!=mUsers.end();)
			{
				auto jit = users.begin();
				while (jit!=users.end())
				{
					if (it->id == (**jit).getId())
						break;
					++jit;
				}
				if (jit==users.end())
				{
					// user not found in openni list
					it = mUsers.erase(it);
				}
				else
				{
					++it;
				}
			}
			// make new users
			std::list<int> newIdsToAdd;
			BOOST_FOREACH(OpenNIUserRef& user, users)
			{
				auto it = mUsers.begin();
				while (it!=mUsers.end())
				{
					if (it->id == user->getId())
						break;
					++it;
				}
				if (it==mUsers.end())
				{
					newIdsToAdd.push_back(user->getId());
				}
			}
			BOOST_FOREACH(int id, newIdsToAdd)
			{
				mUsers.push_back(User());
				mUsers.back().id = id;
			}
			assert(mUsers.size() == users.size());
			// now update all the users
			
			BOOST_FOREACH(OpenNIUserRef &user, users)
			{
				int id = user->getId();
				BOOST_FOREACH(User& myUser, mUsers)
				{
					if (myUser.id == id)
					{
						{
							float* pos =user->getBone(SKEL_TORSO)->position;
							myUser.pos.set(pos[0], pos[1], pos[2]);
							myUser.confidence = user->getBone(SKEL_TORSO)->positionConfidence;
						}
						// Copy all active joints
						for (int i = 0; i<myUser.joints.size(); ++i)
						{
							OpenNIBone const& bone = *user->getBone(JOINT_IDS[i]);
							myUser.joints[i].update(dt, getPosition(bone), bone.positionConfidence, myUser.pos);
						}
						break;
					}
				}
			}
		} // end of user update
	}
	hud().display("Number of tracked users: " + toString(mUsers.size()));
}


void Kinect::draw()
{
	
	// Our rendering - place origin at centre
//	gl::translate(app::getWindowSize()/2);
	BOOST_FOREACH(User& user, mUsers)
	{
		user.draw();
	}
//	mKinect.drawDepth(Rectf(0,0,640,480));
//	mKinect.drawColor(Rectf(640,0,2*640,480));
//	mKinect.drawSkeletons(Rectf(0,0,640,480));

	// 2D drawing
	gl::pushMatrices();
	{
		gl::setMatricesWindow(app::getWindowSize());
		gl::enableAdditiveBlending();
		gl::color(1,1,1, .3);
		gl::draw(mColor);
		gl::draw(Surface(mDepth));
		OpenNIUserList users = mOpenNI->getUserList();
		for (OpenNIUserRef &user: users)
		{
			user->renderJoints(mDepthSize.x, mDepthSize.y, 0);
		}
		
	}
	gl::popMatrices();
	
}


bool Kinect::hasUser() const
{
	ReadLock lock(mUsersMutex);
	return !mUsers.empty();
}


bool Kinect::getUser(User* dest) const
{
	ReadLock lock(mUsersMutex);
	float nearest = numeric_limits<float>::max();
	for (auto it=mUsers.begin(); it!=mUsers.end(); ++it)
	{
		float dist = it->pos.lengthSquared();
		if (dist < nearest)
		{
			nearest = dist;
			*dest = *it;
		}
	}
	return nearest != numeric_limits<float>::max();
}


//void Kinect::print(xn::EnumerationErrors& errors)
//{
//	for(xn::EnumerationErrors::Iterator it = errors.Begin(); it != errors.End(); ++it)
//	{
//		XnChar desc[512];
//		xnProductionNodeDescriptionToString(&it.Description(), desc,512);
//		printf("%s failed: %s\n", desc, xnGetStatusString(it.Error()));
//	}
//}


//XnStatus Kinect::getNode(xn::ProductionNode& node, XnProductionNodeType type)
//{
//	XnStatus result = XN_STATUS_OK;
//	xn::NodeInfoList nodeList;
//	result = mContext.EnumerateExistingNodes(nodeList, type);
//	if (result!=XN_STATUS_OK)
//		return result;
//	int i(0);
//	xn::NodeInfoList::Iterator it(nodeList.Begin());
//	if (it==nodeList.End()) {
//		cout << "Error: Node " << i << " of type " << type << " does not exist in Context.\n";
//		return XN_STATUS_NO_NODE_PRESENT;
//	}
//	xn::NodeInfo info = *it;
//	result = info.GetInstance(node);
//	return result;
//}


ci::Vec3f Kinect::getPosition(V::OpenNIBone const& joint)
{
	return Vec3f(joint.position[0], joint.position[1], joint.position[2]);
}

