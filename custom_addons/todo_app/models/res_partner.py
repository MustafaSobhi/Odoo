from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    task_ids = fields.One2many("todo.task",'assign_to')  # Correctly indented within the class