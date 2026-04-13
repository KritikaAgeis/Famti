from odoo import models, fields

class HrJobRejectWizard(models.TransientModel):
    _name = 'hr.job.reject.wizard'
    _description = 'Reject Job Wizard'

    remarks = fields.Text(string="Remarks", required=True)
    job_id = fields.Many2one('hr.job')

    def action_confirm_reject(self):
        self.ensure_one()

        self.job_id.write({
            'state': 'rejected',
            'remarks': self.remarks
        })

class HrResignationRejectWizard(models.TransientModel):
    _name = 'hr.resignation.reject.wizard'
    _description = 'Reject Resignation Wizard'

    remarks = fields.Text(string="Rejection Remarks", required=True)
    resignation_id = fields.Many2one('hr.resignation')

    def action_confirm_reject(self):
        self.ensure_one()

        self.resignation_id.write({
            'state': 'rejected',
            'remarks': self.remarks
        })

        self.resignation_id.message_post(
            body=f"Resignation Rejected with remarks: {self.remarks}"
        )