from odoo import models, fields, api
import base64

class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    def write(self, vals):
        old_stage_map = {rec.id: rec.stage_id.id for rec in self}
        res = super().write(vals)

        if 'stage_id' in vals:
            hired_stage = self.env['hr.recruitment.stage'].search(
                [('name', '=', 'Selected')], limit=1
            )

            for rec in self:
                old_stage = old_stage_map.get(rec.id)
                if rec.stage_id.id == hired_stage.id and old_stage != hired_stage.id:
                    rec.send_offer_letter()

        return res

    def send_offer_letter(self):
        self.ensure_one()

        template = self.env.ref('famti.email_template_offer_letter')

        pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'famti.offer_letter_report',
            [self.id]
        )

        attachment = self.env['ir.attachment'].create({
            'name': f'Offer Letter - {self.partner_name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf),
            'res_model': 'hr.applicant',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        subject = f"Offer Letter for the Position of {self.job_id.name or ''}"
        email_to = self.email_from or ''

        body = template._render_field('body_html', [self.id])[self.id]

        self.env['mail.mail'].create({
            'subject': subject,
            'body_html': body,
            'email_to': email_to,
            'attachment_ids': [(4, attachment.id)],
        }).send()

        self.message_post(
            body=body,
            subject=subject,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
            attachment_ids=[attachment.id],
        )
