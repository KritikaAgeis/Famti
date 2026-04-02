from odoo import models, fields, api
from datetime import timedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many(
        'hr.employee.document',
        'employee_id',
        string="Related Documents"
    )

    joining_date = fields.Date(string="Joining Date")

    training_start_date = fields.Date(string="Training Start Date")
    training_end_date = fields.Date(string="Training End Date")

    probation_start_date = fields.Date(string="Probation Start Date")
    probation_end_date = fields.Date(string="Probation End Date")

    wsib_case_ids = fields.One2many('wsib.case', 'employee_id',
        string="WSIB Cases"
    )
    wsib_case_count = fields.Integer(compute="_compute_wsib_case_count")

    def _compute_wsib_case_count(self):
        for rec in self:
            rec.wsib_case_count = len(rec.wsib_case_ids)

    def action_view_wsib_cases(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'WSIB Cases',
            'res_model': 'wsib.case',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
        }

    @api.onchange('joining_date')
    def _onchange_joining_date(self):
        if self.joining_date:
            self.probation_start_date = self.joining_date
            self.probation_end_date = self.joining_date + timedelta(days=90)

    @api.model
    def create(self, vals):
        if not vals.get('barcode'):
            while True:
                barcode = self.env['ir.sequence'].next_by_code('hr.employee.barcode')
                if not self.search([('barcode', '=', barcode)], limit=1):
                    vals['barcode'] = barcode
                    break
        return super().create(vals)

    def generate_random_barcode(self):
        for employee in self:
            if not employee.barcode:
                while True:
                    barcode = self.env['ir.sequence'].next_by_code('hr.employee.barcode')
                    if not self.search([('barcode', '=', barcode)], limit=1):
                        employee.barcode = barcode
                        break

    def action_open_wsib_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create WSIB Case',
            'res_model': 'wsib.case.wizard',
            'view_mode': 'form',
            'target': 'new', 
            'context': {
                'default_employee_id': self.id,
                'default_department_id': self.department_id.id,
                'default_job_id': self.job_id.id,
                'default_manager_id': self.parent_id.id,
                'default_coach_id': self.coach_id.id,
            }
        }


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    document_ids = fields.One2many(
        related="employee_id.document_ids",
        readonly=True
    )

    wsib_case_ids = fields.One2many(
        related="employee_id.wsib_case_ids",
        readonly=True
    )


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'Employee Related Documents'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    document_name = fields.Char(string="Document Name", required=True)
    document_file = fields.Binary(string="Upload Document")
    document_filename = fields.Char(string="File Name")
    uploaded_by = fields.Many2one('res.users', string="Uploaded By", default=lambda self: self.env.user)

class WsibCase(models.Model):
    _name = 'wsib.case'
    _description = 'WSIB Case'

    name = fields.Char(string="Reference", default="New", copy=False)

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    job_id = fields.Many2one('hr.job', string="Job Position", readonly=True)
    incident_date = fields.Datetime(string="Incident Date", required=True)
    description = fields.Text(string="Incident Description",placeholder="Explain the incident clearly (location, cause, and impact)...", required=True)
    manager_id = fields.Many2one('hr.employee', string="Manager", readonly=True)
    coach_id = fields.Many2one('hr.employee', string="Coach", readonly=True)
    report_type = fields.Selection([
        ('worker', 'Worker (Form 6)'),
        ('employer', 'Employer (Form 7)'),
        ('medical', 'Medical (Form 8)')
    ], string="Report Type", required=True)
    report_document = fields.Binary("Upload Document", required=True)
    report_filename = fields.Char("File Name")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ], string="Status", default='draft', tracking=True)

    def action_start_review(self):
        self.state = 'under_review'

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def action_close(self):
        self.state = 'closed'

    def action_open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'WSIB Case',
            'res_model': 'wsib.case',
            'view_mode': 'form',
            'view_id': self.env.ref('famti.view_wsib_case_form').id,
            'res_id': self.id,
            'target': 'current',
        }
