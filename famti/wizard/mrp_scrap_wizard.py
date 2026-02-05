from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MrpProductionScrapWizard(models.TransientModel):
    _name = 'mrp.production.scrap.wizard'
    _description = 'MO Scrap Wizard'

    production_id = fields.Many2one('mrp.production', required=True )

    product_id = fields.Many2one('product.product')
    scrap_reason_tag_ids = fields.Many2many( comodel_name='stock.scrap.reason.tag',
        string='Scrap Reason',
    )
    location_id = fields.Many2one('stock.location', string='Source Location')
    scrap_location_id = fields.Many2one('stock.location',
        domain=[('scrap_location', '=', True)]
    )
    date = fields.Datetime(default=fields.Datetime.now)
    company_id = fields.Many2one('res.company')

    line_ids = fields.One2many('mrp.production.scrap.wizard.line','wizard_id',
        string="Scrap Lines"
    )


    def action_confirm_scrap(self):
        scrap_lines_vals = []

        for line in self.line_ids:
            if line.scrap_qty <= 0:
                continue
            if line.scrap_qty > line.available_qty:
                raise ValidationError(
                    _("Scrap quantity cannot exceed available quantity for serial %s")
                    % (line.serial_line_id.serial_number)
                )

            scrap_lines_vals.append({
                'production_scrap_id': self.production_id.id,
                'location_id': self.scrap_location_id.id,
                'serial_number': line.serial_line_id.serial_number,
                'quantity': line.scrap_qty,
                'uom_id': line.uom_id.id,
            })

        if scrap_lines_vals:
            self.env['mrp.production.scrap.line'].create(scrap_lines_vals)

        return {'type': 'ir.actions.act_window_close'}


class MrpProductionScrapWizardLine(models.TransientModel):
    _name = 'mrp.production.scrap.wizard.line'
    _description = 'MO Scrap Wizard Line'

    wizard_id = fields.Many2one(
        'mrp.production.scrap.wizard',
        required=True,
        ondelete='cascade'
    )

    serial_line_id = fields.Many2one(
        'mrp.production.serial.line',
        string="Serial Line"
    )

    serial_number = fields.Char(readonly=True,store=True)
    available_qty = fields.Float(readonly=True,store=True)
    scrap_qty = fields.Float(string="Scrap Qty")
    uom_id = fields.Many2one('uom.uom', readonly=True,store=True)
    location_id = fields.Many2one('stock.location', readonly=True,store=True)