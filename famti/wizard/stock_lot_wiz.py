from odoo import models, fields, api
from odoo.exceptions import UserError

class StockLotWizard(models.TransientModel):
    _name = 'stock.lot.wizard'
    _description = 'Stock Lot Wizard'

    lot_ids = fields.Many2many(
        'stock.lot',
        string='Lot / Serial Number',
        required=True
    )

    location_id = fields.Many2one('stock.location',string='Source Location',required=True)
    dest_location_id = fields.Many2one('stock.location',string='Destination Location',required=True)

    partner_id = fields.Many2one('res.partner',string='Reciever Name',required=True)


    note = fields.Text(string='Notes')



    def action_confirm(self):
        qc_passed = list(set(self.lot_ids.mapped('qc_status')))
        print("=============",qc_passed)
        if len(qc_passed)>1:
            raise UserError("Please select only those rolls whose Certificate of Analysis has been verified.")
        if qc_passed[0]=='pending':
            raise UserError("Those rolls who has not been verified, can not move to any other location.")

        products = self.lot_ids.mapped('product_id')
        if len(products) > 1:
            raise UserError("Select lots of the same product only.")

        product = products[0]

        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal')], limit=1
        )
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.dest_location_id.id,
            'origin': self.note,
        })

        # ONE MOVE with total quantity
        move = self.env['stock.move'].create({
            'name': f'Move {product.display_name}',
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': len(self.lot_ids),
            'picking_id': picking.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.dest_location_id.id,
        })
        picking.action_confirm()
        picking.button_validate()

        return {'type': 'ir.actions.act_window_close'}


class COAFailedWiz(models.TransientModel):
    _name = 'coa.failed.wizard'
    _description = 'COA Failed Wizard'

    lot_ids = fields.Many2many(
        'stock.lot',
        string='Lot / Serial Number',
        required=True
    )
    failure_reasons = fields.Selection([('physical_damage', 'Physical Damage'),
                                        ('qlty_fail', 'Quality / Specification Failure'),
                                        ('manuf_defect', 'Manufacturing Defects'),
                                        ('others', 'Others')],
                                       string="Failure Reasons",required=True)
    reason = fields.Text(string="Reason")



    def action_failed_coa_rolls(self):
        rolls = self.lot_ids.filtered(lambda r: r.qc_status == 'pending' and r.company_id == self.env.user.company_id)
        if not rolls:
            return True
        rolls.write({'qc_status': 'failed', 'qc_remark': self.reason if self.reason else ''})
        return True



