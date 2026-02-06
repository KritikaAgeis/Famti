from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.tools import OrderedSet


class MrpBatchProduceLine(models.TransientModel):
    _name = 'mrp.batch.produce.line'
    _description = 'Batch Production Line'

    wizard_id = fields.Many2one('mrp.batch.produce', string='Wizard',ondelete='cascade', required=True)
    serial_number = fields.Char(string='Serial Number')
    location_id = fields.Many2one('stock.location', string='Location')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')


class MrpBatchProduce(models.TransientModel):
    _inherit = 'mrp.batch.produce'

    sn_quantity = fields.Float(string='Quantity per Lot')
    sn_recived_quantity = fields.Float(string='Quantity Received',compute="_compute_total_qty", store=True,)
    line_ids = fields.One2many('mrp.batch.produce.line', 'wizard_id', string='Line Items')

    @api.depends('production_id')
    def _compute_total_qty(self):
        for wizard in self:
            wizard.sn_recived_quantity = wizard.production_id.product_qty

    def action_produce_lots(self):
        self.ensure_one()

        production = self.production_id
        serial_line_vals = []

        for line in self.line_ids:
            serial_line_vals.append({
                'production_id': production.id,
                'serial_number': line.serial_number,
                'quantity': line.quantity,
                'uom_id': line.uom_id.id,
                'location_id': line.location_id.id,
            })

        if serial_line_vals:
            self.env['mrp.production.serial.line'].create(serial_line_vals)

        return {'type': 'ir.actions.act_window_close'}


    def action_generate_production_text(self):
        self.ensure_one()
        if not self.lot_name:
            raise UserError(_('Please specify the first serial number you would like to use.'))
        
        lots_name = self.env['stock.lot'].generate_lot_names(self.lot_name, self.lot_qty)
        serial_numbers = [lot['lot_name'] for lot in lots_name]
        self.line_ids = [(5, 0, 0)] 
        qty_per_lot = self.sn_recived_quantity / self.lot_qty
        line_vals = []
        for serial in serial_numbers:
            line_vals.append((0, 0, {
                'serial_number': serial,
                'quantity': qty_per_lot,           
                'uom_id': self.production_id.product_uom_id.id,
                'location_id': self.production_id.location_dest_id.id,
            }))
        self.line_ids = line_vals

        action = self.env["ir.actions.actions"]._for_xml_id("mrp.action_mrp_batch_produce")
        action['res_id'] = self.id
        return action


    def _production_text_to_object(self, mark_done=False):
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_("Please generate serial/lot lines first."))

        productions_amount = []
        productions_lot_names = []

        for line in self.line_ids:
            if not line.serial_number:
                raise UserError(_("Serial/Lot number is missing in a line."))
            if line.quantity <= 0:
                raise UserError(_("Quantity must be greater than zero."))

            productions_lot_names.append(line.serial_number)
            productions_amount.append(line.quantity)

        productions = self.production_id._split_productions({
            self.production_id: productions_amount
        })

        lots = self.env['stock.lot'].search([
            ('company_id', 'in', [self.production_id.company_id.id, False]),
            ('name', 'in', productions_lot_names),
            ('product_id', '=', self.production_id.product_id.id),
        ])

        existing_lot_names = lots.mapped('name')
        new_lots = []

        for lot_name in productions_lot_names:
            if lot_name not in existing_lot_names:
                new_lots.append({
                    'name': lot_name,
                    'product_id': self.production_id.product_id.id,
                    'company_id': self.production_id.company_id.id,
                })

        if new_lots:
            lots |= self.env['stock.lot'].create(new_lots)

        lots_by_name = {lot.name: lot for lot in lots}

        productions_to_set = OrderedSet()
        for production, line in zip(productions, self.line_ids):
            production.lot_producing_id = lots_by_name[line.serial_number]
            production.qty_producing = line.quantity
            production.set_qty_producing()
            productions_to_set.add(production.id)

        productions = self.env['mrp.production'].browse(productions_to_set)

        if mark_done:
            return productions.with_context(from_wizard=True).button_mark_done()

        print_actions = productions._autoprint_mass_generated_lots()
        if print_actions:
            return {
                'type': 'ir.actions.client',
                'tag': 'do_multi_print',
                'params': {'reports': print_actions},
            }