from odoo import models, fields, api
import base64

class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    def write(self, vals):
        res = super().write(vals)

        if 'stage_id' in vals:
            hired_stage = self.env['hr.recruitment.stage'].search([('name','=','Contract Signed')], limit=1)

            for rec in self:
                if rec.stage_id.id == hired_stage.id:
                    rec.send_offer_letter()

        return res


    def send_offer_letter(self):

        template = self.env.ref('famti.email_template_offer_letter')
        report = self.env.ref('famti.action_offer_letter_report')

        for rec in self:
            pdf, _ = report._render_qweb_pdf('famti.action_offer_letter_report', [rec.id])
            attachment = self.env['ir.attachment'].create({
                'name': 'Offer Letter.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf),
                'res_model': 'hr.applicant',
                'res_id': rec.id,
                'mimetype': 'application/pdf',
            })
            template.attachment_ids = [(4, attachment.id)]
            template.send_mail(rec.id, force_send=True)