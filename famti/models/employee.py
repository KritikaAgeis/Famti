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


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    document_ids = fields.One2many(
        related="employee_id.document_ids",
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
