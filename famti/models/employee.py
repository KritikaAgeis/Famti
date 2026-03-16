from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many(
        'hr.employee.document',
        'employee_id',
        string="Related Documents"
    )

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