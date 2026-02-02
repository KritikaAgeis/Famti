from unicodedata import category

from odoo import models, fields,_
import base64
import csv
import io
from odoo.exceptions import UserError

class FamtiLotImportWizard(models.TransientModel):
    _name = "famti.lot.import.wizard"
    _description = "Import Lots from Excel/CSV"

    file = fields.Binary(string="File", required=True)
    filename = fields.Char()


    def action_import(self):
        self.ensure_one()

        move = self.env['stock.move'].browse(self.env.context.get('active_id'))
        if not move:
            raise UserError(_("No stock move found."))

        if move.product_id.tracking == 'none':
            raise UserError(_("Product is not tracked by lot/serial."))

        move.move_line_ids.filtered(
            lambda l: not l.quantity or l.state != 'done'
        ).unlink()

        # Decode file
        data = base64.b64decode(self.file)
        file_io = io.StringIO(data.decode('utf-8-sig'))
        reader = csv.DictReader(file_io)

        required_fields = {'lot_name', 'qty'}
        if not required_fields.issubset(reader.fieldnames):
            raise UserError(_("CSV must contain columns: lot, qty"))

        StockLot = self.env['stock.lot']
        StockMoveLine = self.env['stock.move.line']

        for row in reader:
            lot_name = row.get('lot_name')
            film = row.get('film')
            film_type = row.get('film_type')
            thickness = row.get('thickness')
            weight = row.get('weight')
            core_id = row.get('core_id')
            category=row.get('category')
            lot_number = row.get('lot_number')
            pallet_no = row.get('pallet_no')
            qty = float(row.get('qty', 0))

            if not lot_name or qty <= 0:
                continue

            # Find or create lot/serial
            lot = StockLot.search([
                ('name', '=', lot_name),
                ('product_id', '=', move.product_id.id),
                ('company_id', '=', move.company_id.id),
            ], limit=1)

            if not lot:
                lot = StockLot.create({
                    'name': lot_name,
                    'product_id': move.product_id.id,
                    'company_id': move.company_id.id,
                })

            # Create move line
            moveline=StockMoveLine.create({
                'move_id': move.id,
                'lot_name': lot_name,
                'film':film,
                'film_type':film_type,
                'thickness': thickness,
                'weight': weight,
                'core_id': core_id,
                'category': category,
                'lot_number': lot_number,
                'pallet_no': pallet_no,
                'picking_id': move.picking_id.id,
                'product_id': move.product_id.id,
                # 'product_uom_id': move.product_uom.id,
                'quantity': qty,
                'lot_id': lot.id,
                'location_id': move.location_id.id,
                # 'location_dest_id': move.location_dest_id.id,
            })
        return {'type': 'ir.actions.act_window_close'}
