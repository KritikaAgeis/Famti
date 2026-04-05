from odoo import models, fields, api


class HrResignation(models.Model):
    _name = 'hr.resignation'
    _description = 'Employee Resignation'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)

    department_id = fields.Many2one('hr.department', string="Department")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    joining_date = fields.Date(string="Joining Date")

    resignation_date = fields.Date(string="Resignation Date")
    approved_last_date = fields.Date(string="Approved Last Working Day")
    notice_period = fields.Integer(string="Notice Period (Days)")

    resignation_type = fields.Selection([
        ('normal', 'Normal Resignation'),
        ('terminated', 'Terminated / Fired')
    ], default='normal')

    manager_id = fields.Many2one('hr.employee', string="Manager")

    reason = fields.Text(string="Reason")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')

    @api.onchange('employee_id')
    def _onchange_employee(self):
        for rec in self:
            emp = rec.employee_id

            if emp:
                rec.department_id = emp.department_id
                rec.manager_id = emp.parent_id
                rec.joining_date = emp.joining_date

                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', emp.id), ('state', '=', 'open')],
                    limit=1
                )
                rec.contract_id = contract
            else:
                rec.department_id = False
                rec.manager_id = False
                rec.contract_id = False
                rec.joining_date = False

    def action_submit(self):
        self.state = 'waiting_for_approval'

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'