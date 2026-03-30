from odoo import models, fields, api

class HrResignation(models.Model):
    _name = 'hr.resignation'
    _description = 'Employee Resignation'

    employee_id = fields.Many2one('hr.employee',string="Employee", required=True)
    department_id = fields.Many2one('hr.department',string="Department",compute="_compute_employee_details", store=True)
    contract_id = fields.Many2one('hr.contract',string="Contract",compute="_compute_employee_details", store=True)
    joining_date = fields.Date(string="Joining Date",compute="_compute_employee_details", store=True)
    resignation_date = fields.Date(string="Resignation Date")
    approved_last_date = fields.Date(string="Approved Last Working Day")
    notice_period = fields.Integer(string="Notice Period (Days)")
    resignation_type = fields.Selection([
        ('normal', 'Normal Resignation'),
        ('terminated', 'Terminated / Fired')
    ], string="Resignation Type", default='normal')
    manager_id = fields.Many2one('hr.employee',string="Manager",compute="_compute_employee_details", store=True)
    reason = fields.Text(string="Reason")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', string="Status")

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.employee_id:
            rec.department_id = rec.employee_id.department_id
            rec.manager_id = rec.employee_id.parent_id
            rec.joining_date = rec.employee_id.joining_date

            contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')],
                limit=1
            )
            rec.contract_id = contract.id if contract else False

        return rec

    def write(self, vals):
        res = super().write(vals)
        if 'employee_id' in vals:
            for rec in self:
                if rec.employee_id:
                    rec.department_id = rec.employee_id.department_id
                    rec.manager_id = rec.employee_id.parent_id
                    rec.joining_date = rec.employee_id.joining_date

                    contract = self.env['hr.contract'].search(
                        [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')],
                        limit=1
                    )
                    rec.contract_id = contract.id if contract else False
                else:
                    rec.department_id = False
                    rec.manager_id = False
                    rec.contract_id = False
                    rec.joining_date = False

        return res

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id
                rec.manager_id = rec.employee_id.parent_id
                rec.joining_date = rec.employee_id.joining_date

                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')],
                    limit=1
                )
                rec.contract_id = contract.id if contract else False
            else:
                rec.department_id = False
                rec.manager_id = False
                rec.contract_id = False
                rec.joining_date = False

    def action_submit(self):
        for rec in self:
            rec.state = 'waiting_for_approval'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
