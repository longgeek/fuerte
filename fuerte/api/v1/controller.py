#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>


from fuerte import app
from flask_restful import Resource
from flask_restful import reqparse
from .config import load_workflow, API_ACTIONS

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

        # Load workflow
        s, m, workflow = load_workflow(api_key, api_action)
        if s != 0:
            if s == -1:
                return {"Error": "Load API in failure!" +
                        " [Error]" + m}, 500
            else:
                return {"Warning": m, "inner_code": s}, 500

        # Exec workflow
        try:
            s, m, r = workflow(**params)
        except TypeError as e:
            return {"Error": "The parameters invalid! <%s>" % e.message}, 500

        if s == 0:
            api_return = {"Message": m, "data": r}, 200
        elif s == -1:
            api_return = {"Error": "API Server Error!" +
                          " [Error] %s" % m}, 500
        else:
            api_return = {"inner_code": s,
                          "Warning": m}, 200
        return api_return
