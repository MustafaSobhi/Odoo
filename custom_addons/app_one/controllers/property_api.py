import json
import math
from urllib.parse import parse_qs
from PIL.ImageChops import offset
from docutils.nodes import status

from addons.portal.controllers.portal import pager
from odoo import http
from odoo.http import request


def valid_response(data, status, pagination_info):
    response_body = {"data": data}
    if pagination_info:
        response_body["pagination_info"] = pagination_info
    return request.make_json_response(response_body, status=status)


def invalid_response(error, status):
    response_body = {"Error": error}
    return request.make_json_response(response_body, status=status)


class PropertyApi(http.Controller):
    @http.route("/v1/property", methods=["POST"], type="http", auth="none", csrf=False)
    def post_property(self):
        args = request.httprequest.data.decode()  # Decoding the incoming data
        vals = json.loads(args)
        columns=', '.join(vals.keys())
        print(columns)
        values=', '.join(['%s'] * len(vals))
        print(values)
        print(args)# Parsing JSON data
        if not vals.get("name"):
            return request.make_json_response({"message": "Name required!"}, status=400)
        try:
            cr=request.env.cr
            query=f"""INSERT INTO property ({columns}) VALUES ({values}) RETURNING id,name,postcode"""
            cr.execute(query,tuple(vals.values()))
            res=cr.fetchone()
            print(res)
            if res:
                return request.make_json_response({"name": res[1], "id": res[0]})
        except Exception as error:
            return request.make_json_response({"message": error}, status=400)

    @http.route(
        "/v1/property/json", methods=["POST"], type="json", auth="none", csrf=False
    )
    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env["property"].sudo().create(vals)

    @http.route(
        "/v1/property/<int:property_id>",
        methods=["PUT"],
        type="http",
        auth="none",
        csrf=False,
    )
    def update_property(self, property_id):
        try:
            property_id = (
                request.env["property"].sudo().search([("id", "=", property_id)])
            )
            if not property_id:
                return request.make_json_response(
                    {"message": "Id not exist!"}, status=400
                )

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            property_id.write(vals)
        except Exception as error:
            return request.make_json_response({"message": error}, status=400)

    @http.route(
        "/v1/property/<int:property_id>",
        methods=["GET"],
        type="http",
        auth="none",
        csrf=False,
    )
    def get_property(self, property_id):
        try:
            # Search for the property by ID
            property_record = (
                request.env["property"].sudo().search([("id", "=", property_id)])
            )

            # Check if the property exists
            if not property_record:
                return invalid_response({"message": "Id not exist!"}, status=400)

            # Return property data as JSON
            return valid_response(
                {
                    "id": property_record.id,
                    "name": property_record.name,
                },
                status=200,
            )

        except Exception as error:
            # Handle errors and return a JSON response with error message
            return request.make_json_response({"message": str(error)}, status=400)

    @http.route(
        "/v1/property/<int:property_id>",
        methods=["DELETE"],
        type="http",
        auth="none",
        csrf=False,
    )
    def delete_property(self, property_id):
        try:
            # Search for the property by ID
            property_record = (
                request.env["property"].sudo().search([("id", "=", property_id)])
            )
            if not property_record:
                return request.make_json_response(
                    {"message": "ID not exist!"}, status=400
                )
            property_record.sudo().unlink()
            return request.make_json_response(
                {
                    "message": "IThe record deleted successfully",
                    "name": property_record.id,
                },
                status=200,
            )
        except Exception as error:
            # Handle errors and return a JSON response with error message
            return request.make_json_response({"message": str(error)}, status=400)

    @http.route(
        "/v1/properties",
        methods=["GET"],
        type="http",
        auth="none",
        csrf=False,
    )
    def get_property_list(self):
        try:
            params = parse_qs(request.httprequest.query_string.decode("utf-8"))
            print(params)
            property_domain = []
            page = offset = None
            limit = 2
            if params.get("limit"):
                limit = int(params.get("limit")[0])
            if params.get("page"):
                page = int(params.get("page")[0])
            if page:
                offset = (page * limit) - limit

            if params.get("state"):
                property_domain += [("state", "=", params.get("state")[0])]
            property_records = (
                request.env["property"]
                .sudo()
                .search(property_domain, offset=offset, limit=limit, order="id desc")
            )
            property_count = (
                request.env["property"].sudo().search_count(property_domain)
            )
            if not property_records:
                return request.make_json_response(
                    {"message": "There are no any properties"}, status=400
                )

            # Return property data as JSON
            return valid_response(
                [
                    {
                        "id": property_records.id,
                        "name": property_records.name,
                        "ref": property_records.ref,
                        "postcode": property_records.postcode,
                        "description": property_records.description,
                        "bedrooms": property_records.bedrooms,
                        "garden_area": property_records.garden_area,
                    }
                    for property_records in property_records
                ],
                pagination_info={
                    "page": math.ceil(property_count / limit) if limit else 1,
                    "limit": limit,
                    "count": property_count,
                },
                status=200,
            )

        except Exception as error:
            # Handle errors and return a JSON response with error message
            return valid_response({"message": str(error)}, status=400)