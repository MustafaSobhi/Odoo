from email.policy import default

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Task'
    name = fields.Char('Task Name', default="New", translate=True)
    due_date=fields.Date()
    ref=fields.Char(default="Ref",readonly=1)
    description=fields.Char()
    assign_to=fields.Many2one('res.partner')
    task_line_ids=fields.One2many('task.line','task_id')
    state=fields.Selection([
        ('new','New'),
        ('in_progress','In Progress'),
        ('completed','Completed'),
        ('closed','Closed')
    ],default='new')
    estimate_time=fields.Float(' Estimate Time (Hours)', default=1.0)
    total_duration = fields.Float('Total Duration (Hours)', compute='_compute_total_duration', store=True)
    active = fields.Boolean(default=True)
    is_late = fields.Boolean()
    _sql_constraints = [("unique_name", 'unique("name")', "this name is exist!")]
    def action_open_related_user(self):
        if self.assign_to:
            # Get the action for res.partner
            action = self.env.ref('base.action_partner_form')
            if action:
                action = action.read()[0]
                action['domain'] = [('id', '=', self.assign_to.id)]
                return action
        return {'type': 'ir.actions.act_window_close'}

    def write(self, vals):
        # Get the current user's group
        user_groups = self.env.user.groups_id.mapped('id')
        todo_user_group_id = self.env.ref('todo_app.todo_user_group').id

        if todo_user_group_id in user_groups:
            # Only allow updating the 'state' field for users in 'todo_user_group'
            if any(key != 'state' for key in vals):
                raise models.ValidationError("You can only edit the 'state' field.")

        return super(TodoTask, self).write(vals)

    @api.model_create_multi
    def create(self, vals):
        res = super(TodoTask, self).create(vals)
        if res.ref == "Ref":
            res.ref = self.env["ir.sequence"].next_by_code("todo_seq")
        return res

    @api.depends('task_line_ids.duration')
    def _compute_total_duration(self):
        for task in self:
            task.total_duration = sum(line.duration for line in task.task_line_ids)


    @api.constrains('total_duration', 'estimate_time')
    def _check_duration(self):
        for task in self:
            if task.total_duration > task.estimate_time:
                raise ValidationError("Total duration cannot exceed estimate time!")


    def action_new(self):
        for rec in self:
            rec.state = 'new'

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'

    def action_closed(self):
        for rec in self:
            rec.state = 'closed'

    def check_expected_date(self):
        task_ids = self.search([])
        for rec in task_ids:
            if rec.due_date and rec.due_date < fields.Date.today():
                rec.is_late = True
class TaskLine(models.Model):
    _name='task.line'

    date=fields.Date()
    description=fields.Text()
    duration = fields.Float('Duration (Hours)', default=0.0 )
    task_id=fields.Many2one('todo.task',readonly=1)
