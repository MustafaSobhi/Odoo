from email.policy import default
from re import search

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PropertyHistory(models.Model):
    _name = "property.history"
    _description = "Property History"
    ref = fields.Char(default="ref")
    user_id = fields.Many2one("res.users")
    property_id = fields.Many2one("property")
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()
    line_ids = fields.One2many("property.history.line", "history_id")

    class PropertyHistoryLine(models.Model):
        _name = "property.history.line"
        history_id = fields.Many2one("property.history")
        description = fields.Text()
        area = fields.Float()
