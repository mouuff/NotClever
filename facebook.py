#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import cgi
import hashlib
import time
import urllib

# Find a JSON parser
try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)


class GraphAPI(object):
    """A client for the Facebook Graph API.

    The Graph API is made up of the objects in Facebook (e.g., people, pages,
    events, photos) and the connections between them (e.g., friends,
    photo tags, and event RSVPs). This client provides access to those
    primitive types in a generic way. For example, given an OAuth access
    token, this will fetch the profile of the active user and the list
    of the user's friends::

       graph = facebook.GraphAPI(access_token)
       user = graph.get_object("me")
       friends = graph.get_connections(user["id"], "friends")

    """
    def __init__(self, access_token=None):
        self.access_token = access_token

    def get_object(self, id, **args):
        """Fetchs the given object from the graph.
    For example, 
        
        * To get information about active user::

        >>> graph_api.get_object("me")
            {
            u'first_name': u'John', 
            u'last_name': u'Gump', 
            u'name': u'John Gump', 
            u'locale': u'en_US',
            u'gender': u'male',
            u'email': u'x.y@gmail.com',
            u'id': u'100000791214254'
            }
        
    
        * To get information about user with facebook id 1232343::

        graph_api.get_object("1232343")

    """
        return self.request(id, args)

    def get_objects(self, ids, **args):
        """Fetchs all of the given object from the graph.

        We return a map from ID to object. If any of the IDs are invalid,
        we raise an exception.
        """
        args["ids"] = ",".join(ids)
        return self.request("", args)

    def get_connections(self, id, connection_name, **args):
        """Fetchs the connections for given object. 
    Some examples, 

        * To get friends of active user::
        
        >>graph_api.get_connections("me", "friends")
            {
            u'data': [
                    {
                    u'name': u'Friend 1 Name',
                    u'id': u'100000474717542'
                    },
                    {
                    u'name': u'Friend 2 Name',
                    u'id': u'100000790755652'
                    },
                    {
                    u'name': u'Third Friend Name',
                    u'id': u'100000795766141'
                    }
                    ........
                    ........
                   ]
            }

        * To get facebook pages of active users::
        
        >>graph_api.get_connections("me", "accounts")
            {
            u'data': [
                    {
                    u'category': u'Local business',
                    u'name': u'VishwaKalyan',
                    u'id': u'121390277930969'
                    }, 
                    {
                    u'category': u'Author', 
                    u'name': u'Sonal', 
                    u'id': u'168888549793211'
                    }, 
                    {
                    u'category': u'Cars',
                    u'name': u'Demo merchant 333',
                    u'id': u'151252671563842'
                    }
                    ....
                ]
            }
        
        * To get feeds post of active user::

        graph_api.get_connection("me", "feed")

    """
        return self.request(id + "/" + connection_name, args)

    def put_object(self, parent_object, connection_name, **data):
        """Writes the given object to the graph, connected to the given parent.

    For example,::

            graph.put_object("me", "feed", message="Hello, world")

        writes "Hello, world" to the active user's wall. Likewise, this
    will comment on a the first post of the active user's feed::

            feed = graph.get_connections("me", "feed")
            post = feed["data"][0]
            graph.put_object(post["id"], "comments", message="First!")

        See `Publishing docs <http://developers.facebook.com/docs/api#publishing>`_ for all of
        the supported writeable objects.

        Most write operations require extended permissions. For example,
        publishing wall posts requires the "publish_stream" permission. See `Authentication Documents 
    <http://developers.facebook.com/docs/authentication/>`_ for details about
        extended permissions.
        """
        assert self.access_token, "Write operations require an access token"
        return self.request(parent_object + "/" + connection_name, post_args=data)

    def put_wall_post(self, message, attachment={}, profile_id="me"):
        return self.put_object(profile_id, "feed", message=message, **attachment)

    def put_comment(self, object_id, message):
        """Writes the given comment on the given post."""
        return self.put_object(object_id, "comments", message=message)

    def put_like(self, object_id):
        """Likes the given post."""
        return self.put_object(object_id, "likes")

    def delete_object(self, id):
        """Deletes the object with the given ID from the graph."""
        self.request(id, post_args={"method": "delete"})

    def request(self, path, args=None, post_args=None):
        """Fetches the given path in the Graph API.

        We translate args to a valid query string. If post_args is given,
        we send a POST request to the given path with the given arguments.
        """
        if not args: args = {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)
        file = urllib.urlopen("https://graph.facebook.com/" + path + "?" +
                              urllib.urlencode(args), post_data)
        try:
            response = _parse_json(file.read())
        finally:
            file.close()
        if response.get("error"):
            raise GraphAPIError(response["error"]["type"],
                                response["error"]["message"])
        return response


class GraphAPIError(Exception):
    def __init__(self, type, message):
        Exception.__init__(self, message)
        self.type = type


def get_user_from_cookie(cookies, app_id, app_secret):
    """Parses the cookie set by the official Facebook JavaScript SDK.

    cookies should be a dictionary-like object mapping cookie names to
    cookie values.

    If the user is logged in via Facebook, we return a dictionary with the
    keys "uid" and "access_token". The former is the user's Facebook ID,
    and the latter can be used to make authenticated requests to the Graph API.
    If the user is not logged in, we return None.

    For example, ::

    result = {
        "uid": '12324454333',
        "access_token"
    }

    For Facebook Canvas applications, please visit this blog entry `Parsing Signed Request Parameter <http://sunilarora.org/parsing-signedrequest-parameter-in-python-bas>`_

    Download the official Facebook JavaScript SDK at `javascript library docs <http://github.com/facebook/connect-js/>`_.
    Read more about Facebook authentication at `authentication documents <http://developers.facebook.com/docs/authentication/>`_.
    """
    cookie = cookies.get("fbs_" + app_id, "")
    if not cookie: return None
    args = dict((k, v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items())
    payload = "".join(k + "=" + args[k] for k in sorted(args.keys())
                      if k != "sig")
    sig = hashlib.md5(payload + app_secret).hexdigest()
    expires = int(args["expires"])
    if sig == args.get("sig") and (expires == 0 or time.time() < expires):
        return args
    else:
        return None
