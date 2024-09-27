from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests


class Property(models.Model):
    _name = "property"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Property"
    ref = fields.Char(default="ref")
    active = fields.Boolean(default=True)
    name=fields.Char(default="New",required=1)
    description = fields.Text(tracking=1)
    postcode = fields.Char()
    date_availability = fields.Date(tracking=1)
    expected_selling_date = fields.Date()
    is_late = fields.Boolean()
    expected_price = fields.Float()
    selling_price = fields.Float(digits=(0, 5))
    diff = fields.Float(compute="_compute_diff", store=1, readonly=0)
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garen_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        default="north",
    )
    owner_id = fields.Many2one("owner")
    line_ids = fields.One2many("property.line", "property_id")
    tag_ids = fields.Many2many("tag")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("sold", "Sold"),
            ("closed", "Closed"),
        ],
        default="draft",
    )
    _sql_constraints = [("unique_name", 'unique("name")', "this name is exist!")]
    owner_address = fields.Char(related="owner_id.address", readonly=0)
    owner_phone = fields.Char(related="owner_id.phone", readonly=0)
    create_time = fields.Datetime(default=fields.Datetime.now())
    next_time = fields.Datetime(compute="_compute_next_time", store=1)

    def action_open_related_owner(self):
        action = self.env["ir.actions.actions"]._for_xml_id("app_one.owner_action")
        view_id = self.env.ref("app_one.owner_view_form").id
        action["res_id"] = self.owner_id.id
        action["views"] = [[view_id, "form"]]
        return action

    def action_open_change_state(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "app_one.change_state_wizard_action"
        )
        action["context"] = {"default_property_id": self.id}
        return action

    def check_expected_date(self):
        property_ids = self.search([])
        for rec in property_ids:
            if (
                    rec.expected_selling_date
                    and rec.expected_selling_date < fields.Date.today()
            ):
                rec.is_late = True

    @api.onchange("expected_price")
    def _onchange_expected_price(self):
        for rec in self:
            print(rec)
            print("inside _onchange_expected_price")
            return {
                "warning": {
                    "title": "warning",
                    "message": "Negative Value.",
                    "type": "notification",
                }
            }

    def action(self):
        print(
            self.env["property"].search(
                [("!"), ("name", "=", "Property1"), ("postcode", "!=", "2")]
            )
        )

    @api.depends("expected_price", "selling_price")
    def _compute_diff(self):
        for rec in self:
            rec.diff = rec.expected_price - rec.selling_price

    def create_property_history(self, old_state, new_state, reason=""):
        for rec in self:
            print("in")
            rec.env["property.history"].create(
                {
                    "user_id": rec.env.uid,
                    "property_id": rec.id,
                    "old_state": old_state,
                    "new_state": new_state,
                    "reason": reason or "",
                    "line_ids": [
                        (0, 0, {"description": line.description, "area": line.area})
                        for line in rec.line_ids
                    ],
                }
            )

    def action_sold(self):
        for rec in self:
            rec.create_property_history(rec.state, "sold")
            rec.state = "sold"

    def action_pend(self):
        for rec in self:
            rec.create_property_history(rec.state, "pending")
            rec.state = "pending"

    def action_draft(self):
        for rec in self:
            rec.create_property_history(rec.state, "draft")
            rec.state = "draft"

    def action_closed(self):
        for rec in self:
            rec.create_property_history(rec.state, "closed", "")
            rec.state = "closed"

    @api.model_create_multi
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == "ref":
            res.ref = self.env["ir.sequence"].next_by_code("property_seq")
        return res

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        res = super(Property, self)._search(
            domain, offset=0, limit=None, order=None, access_rights_uid=None
        )
        return res

    def write(self, vals):
        res = super(Property, self).write(vals)
        return res

    def unlink(self):
        res = super(Property, self).unlink()
        print("inside delete  method")
        return res

    @api.constrains("bedrooms")
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms == 0:
                raise ValidationError("Please enter valid value!")

    @api.depends("create_time")
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else:
                rec.next_time = False

    def get_properties(self):
        payload = dict({
            "message": "from body"
        })
        try:
            response = requests.get('http://127.0.0.1:8069/v1/properties', data=payload)
            if response.status_code == 200:
                print("Successful")
            else:
                print("Fail")
        except Exception as error:
            raise ValidationError(str(error))


class PropertyLine(models.Model):
    _name = "property.line"
    area = fields.Float()
    property_id = fields.Many2one("property")
    description = fields.Char()
