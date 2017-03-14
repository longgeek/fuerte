#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>


from fuerte import app
from flask_restful import Resource
from flask_restful import reqparse
from .config import load_api, API_ACTIONS

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("action", type=str, location="json", required=True)
parser.add_argument("params", type=dict, location="json", required=True)


class APIView(Resource):
    def post(self):
        """API router.

        Accept method "POST" only,
        """

        args = parser.parse_args()
        action = args["action"]
        params = args["params"]

        if "Message" not in action:
            app.logger.debug("Action = " + action)

        # Check Action
        try:
            api_key, api_action = action.split(":", 1)
            if api_key not in API_ACTIONS or \
               api_action not in API_ACTIONS[api_key]:
                raise KeyError
        except KeyError as e:
            return {"Error": "API does not exist[Action is invalid]!" +
                             " [Exception]" + str(e)}, 500
        except Exception as e:
            return {"Error": "API action in exception!" +
                    " [Error]" + str(e)}, 500

        # Load api
        s, m, load_action = load_api(api_key, api_action)
        if s != 0:
            if s == -1:
                return {"Error": "Load API in failure!" +
                        " [Error]" + m}, 500
            else:
                return {"Warning": m, "inner_code": s}, 500

        # Exec action
        try:
            s, m, r = load_action(**params)
        except TypeError as e:
            return {"Error": "The parameters invalid! <%s>" % e.message}, 500

        if s == 0 or s == 200 or s == 204:
            api_return = {"Message": m, "data": r}, 200
        else:
            api_return = {"Error": m}, 500
        return api_return
