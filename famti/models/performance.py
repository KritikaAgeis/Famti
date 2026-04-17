from pip._internal import req

from odoo import models, fields, api, _

class EmployeePerformance(models.Model):
    _name = 'employee.performance'
    _description = 'Employee Performance Evaluation'

    employee_id = fields.Many2one('hr.employee', required=True)
    manager_id = fields.Many2one('hr.employee',related='employee_id.parent_id')
    department_id = fields.Many2one('hr.department',related='employee_id.department_id')

    date_from = fields.Date(string='Date From',required=True)
    date_to = fields.Date(string='Date To',required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('done', 'Done')
    ], default='draft')

    line_ids = fields.One2many('employee.performance.line', 'performance_id')

    total_score = fields.Float(compute="_compute_score", store=True)

    @api.depends('line_ids.rating', 'line_ids.criteria_id.weight')
    def _compute_score(self):
        for rec in self:
            total = 0
            for line in rec.line_ids:
                total += line.rating * line.criteria_id.weight
            rec.total_score = total

    def send_for_review_performance(self):
        for rec in self:
            rec.state = 'in_review'

    def approve_performance(self):
        for rec in self:
            rec.state = 'done'


class EmployeePerformanceLine(models.Model):
    _name = 'employee.performance.line'

    performance_id = fields.Many2one('employee.performance')

    criteria_id = fields.Many2one('performance.criteria') # e.g. Communication, Coding, Punctuality
    rating = fields.Integer()  # 1-5
    remarks = fields.Text()

class PerformanceCriteria(models.Model):
    _name = 'performance.criteria'

    name = fields.Char()
    weight = fields.Float()