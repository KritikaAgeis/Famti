from odoo import models, fields, api

class WsibCaseWizard(models.TransientModel):
    _name = 'wsib.case.wizard'
    _description = 'WSIB Case Wizard'

    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
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



    def action_create_case(self):
        self.ensure_one()
        self.state = 'submitted'
        case = self.env['wsib.case'].create({
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id,
            'job_id': self.job_id.id,
            'manager_id': self.manager_id.id,
            'coach_id': self.coach_id.id,
            'incident_date': self.incident_date,
            'description': self.description,
            'report_type': self.report_type,
            'state': self.state,  
            'report_type': self.report_type,
            'report_document': self.report_document,
        })

        self.env['ir.attachment'].create({
            'name': self.report_filename or 'WSIB Report',
            'datas': self.report_document,
            'res_model': 'wsib.case',
            'res_id': case.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'res_id': self.employee_id.id,
        }