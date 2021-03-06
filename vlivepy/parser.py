# -*- coding: utf-8 -*-
from .exception import auto_raise, APIJSONParesError
from collections import namedtuple
from bs4 import BeautifulSoup

UpcomingVideo = namedtuple("UpcomingVideo", "seq time cseq cname ctype name type product")


def parseVideoSeqFromPostInfo(info, silent=False):
    """ Parse `videoSeq` item from PostInfo

    :param info: postInfo data from api.getPostInfo
    :type info: dict
    :param silent: Return `None` instead of Exception
    :return: `videoSeq` string
    :rtype: str
    """

    # Case <LIVE, VOD>
    if 'officialVideo' in info:
        return info['officialVideo']['videoSeq']

    # Case <Fanship Live, VOD, Post>
    elif 'data' in info:
        # Case <Fanship Live, VOD>
        if 'officialVideo' in info['data']:
            return info['data']['officialVideo']['videoSeq']
        # Case <Post (Exception)>
        else:
            return auto_raise(APIJSONParesError("post-%s is not video" % info['data']['postId']), silent)

    # Case <Connection failed (Exception)>
    else:
        auto_raise(APIJSONParesError("Cannot find any video"), silent)

    return None


def parseUpcomingFromPage(html):
    upcoming = []

    soup = BeautifulSoup(html, 'html.parser')
    soup_upcoming_list = soup.find("ul", {"class": "upcoming_list"})
    for item in soup_upcoming_list.find_all("li"):
        item_type_vod = False

        # find replay class in <li> tag
        soup_item_class_tag = item.get("class")
        if soup_item_class_tag is not None:
            if soup_item_class_tag[0] == "replay":
                item_type_vod = True

        soup_time = item.find("span", {"class": "time"})
        release_time = soup_time.get_text()

        # get title <a> tag
        soup_info_tag = item.find("a", {"class": "_title"})

        # parse upcoming data
        ga_name = soup_info_tag.get("data-ga-name")
        ga_type = soup_info_tag.get("data-ga-type")
        ga_seq = soup_info_tag.get("data-ga-seq")
        ga_cseq = soup_info_tag.get("data-ga-cseq")
        ga_cname = soup_info_tag.get("data-ga-cname")
        ga_ctype = soup_info_tag.get("data-ga-ctype")
        ga_product = soup_info_tag.get("data-ga-product")
        if ga_type == "UPCOMING":
            if item_type_vod:
                ga_type += "_VOD"
            else:
                ga_type += "_LIVE"

        # create item and append
        upcoming.append(UpcomingVideo(seq=ga_seq, time=release_time, cseq=ga_cseq, cname=ga_cname,
                                      ctype=ga_ctype, name=ga_name, product=ga_product, type=ga_type))

    return upcoming


def sessionUserCheck(session):
    r"""

    :param session: session to evaluate
    :type session: reqWrapper.requests.Session
    :return: bool `isUser`
    :rtype: bool
    """
    if 'NEO_SES' in session.cookies.keys():
        return True
    else:
        return False


def parseVodIdFromOffcialVideoPost(post, silent=False):
    r"""

    :param post: OfficialVideoPost data from api.getOfficialVideoPost
    :type post: dict
    :param silent: Return `None` instead of Exception
    :return: VOD id of post
    :rtype: str0
    """

    # Normalize paid content data
    if 'data' in post:
        data = post['data']
    else:
        data = post

    if 'officialVideo' in data:
        if 'vodId' in data['officialVideo']:
            return data['officialVideo']['vodId']
        else:
            auto_raise(APIJSONParesError("Given data is live data"), silent=silent)
    else:
        auto_raise(APIJSONParesError("Given data is post data"), silent=silent)

    return None
