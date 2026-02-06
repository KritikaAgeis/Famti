from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    serial_line_ids = fields.One2many('mrp.production.serial.line', 'production_id',
        string='Serial Details'
    )
    scrap_line_ids = fields.One2many('mrp.production.scrap.line','production_scrap_id', string='Scrap Details')

    mo_serial_no = fields.Boolean( related='product_id.product_tmpl_id.mo_serial_no',
        store=False
    )

    scrap_location_id = fields.Many2one('stock.location',string='Scrap Location',
        domain=[('scrap_location', '=', True)],
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
    

    def action_open_scrap_wizard(self):
        self.ensure_one()

        Wizard = self.env['mrp.production.scrap.wizard']
        WizardLine = self.env['mrp.production.scrap.wizard.line']

        wizard = Wizard.create({
            'production_id': self.id,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'date': fields.Datetime.now(),
            'location_id':self.location_dest_id.id,
            'scrap_location_id':self.scrap_location_id.id,
        })

        if self.lot_producing_id:
            lot = self.lot_producing_id
            WizardLine.create({
                'wizard_id': wizard.id,
                'serial_number_id': lot.id,
                'serial_number': lot.name,
                'available_qty': self.qty_producing,
                'uom_id': self.product_uom_id.id,
            })
        else:
            for move in self.serial_line_ids:
                WizardLine.create({
                    'wizard_id': wizard.id,
                    'serial_line_id': move.id,
                    'serial_number': move.serial_number,
                    'available_qty': move.quantity,
                    'uom_id': move.uom_id.id,
                    'location_id': move.location_id.id,
                })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap Before Production',
            'res_model': 'mrp.production.scrap.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
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
            if mo.scrap_line_ids:
                mo._create_stock_scrap_from_lines()
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

    def _create_stock_scrap_from_lines(self):
        StockScrap = self.env['stock.scrap']
        StockLot = self.env['stock.lot']

        for line in self.scrap_line_ids:
            if line.quantity <= 0:
                continue

            lot = StockLot.search([
                ('name', '=', line.serial_number),
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            if not lot and line.serial_number_id:
                lot = line.serial_number_id
            if not lot:
                raise ValidationError(
                    f"Lot/Serial {line.serial_number} not found for scrap."
                )

            scrap = StockScrap.create({
                'product_id': self.product_id.id,
                'scrap_qty': line.quantity,
                'product_uom_id': line.uom_id.id,
                'lot_id': lot.id,
                'location_id': line.source_location_id.id or self.location_src_id.id,
                'scrap_location_id': line.location_id.id or self.location_src_id.id,
                'company_id': self.company_id.id,
                'origin': self.name,
                'production_id': self.id,
                'scrap_reason_tag_ids': [(6, 0, line.scrap_reason_tag_ids.ids)],
            })

            scrap.action_validate()




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

class MrpProductionScrapLine(models.Model):
    _name = 'mrp.production.scrap.line'
    _description = 'MRP Production Scrap Line'

    production_scrap_id = fields.Many2one( 'mrp.production', string='Manufacturing Order',
        ondelete='cascade', required=True
    )
    serial_number_id = fields.Many2one('stock.lot',store=True)
    serial_number = fields.Char(string='Serial Number')
    location_id = fields.Many2one('stock.location', string='Scrap Location', domain="[('usage', '=', 'internal')]")
    source_location_id = fields.Many2one('stock.location', string='Source Location')
    quantity = fields.Float(string='Scrap Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    scrap_reason_tag_ids = fields.Many2many( comodel_name='stock.scrap.reason.tag',
        string='Scrap Reason',
    )