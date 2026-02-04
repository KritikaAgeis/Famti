from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    serial_line_ids = fields.One2many('mrp.production.serial.line', 'production_id',
        string='Serial Details'
    )
    

    def action_open_split_lots_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Lots',
            'res_model': 'mrp.batch.produce',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_production_id': self.id,
            }
        }


    @api.constrains('serial_line_ids')
    def _check_lot_quantity(self):
        for mo in self:
            if not mo.serial_line_ids:
                continue
            total = sum(mo.serial_line_ids.mapped('quantity'))
            if float_compare(
                total,
                mo.product_qty,
                precision_rounding=mo.product_uom_id.rounding
            ) != 0:
                raise ValidationError(
                    "Total lot quantities must equal Manufacturing Order quantity."
                )

    def button_mark_done(self):
        for mo in self:
            if mo.product_id.tracking == 'lot' and mo.serial_line_ids:
                mo._create_lots_and_move_lines()
        return super().button_mark_done()

    def _create_lots_and_move_lines(self):
        StockLot = self.env['stock.lot']
        StockMoveLine = self.env['stock.move.line']

        move = self.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_id
        )[:1]

        if not move:
            return

        move.move_line_ids.filtered(lambda l: l.state != 'done').unlink()

        for line in self.serial_line_ids:
            if not line.serial_number:
                raise ValidationError("Serial/Lot name is required.")

            lot = StockLot.search([
                ('name', '=', line.serial_number),
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
            ], limit=1)

            if not lot:
                lot = StockLot.create({
                    'name': line.serial_number,
                    'product_id': self.product_id.id,
                    'company_id': self.company_id.id,
                })

            StockMoveLine.create({
                'move_id': move.id,
                'product_id': self.product_id.id,
                'lot_id': lot.id,
                'quantity': line.quantity,   
                'product_uom_id': line.uom_id.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
            })





class MrpProductionSerialLine(models.Model):
    _name = 'mrp.production.serial.line'
    _description = 'MRP Production Serial Line'

    production_id = fields.Many2one( 'mrp.production', string='Manufacturing Order',
        ondelete='cascade', required=True
    )
    serial_number = fields.Char(string='Serial Number')
    location_id = fields.Many2one('stock.location', string='Location', domain="[('usage', '=', 'internal')]")
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')