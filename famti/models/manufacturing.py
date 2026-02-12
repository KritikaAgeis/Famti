from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from datetime import date

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

    consumable_line_ids = fields.One2many('mrp.consumables','production_id',
        string='Consumables'
    )

    product_code =fields.Char(string="Product Code")

    @api.onchange('product_id')
    def _onchange_product_id_set_code(self):
        for rec in self:
            if rec.product_id:
                rec.product_code = rec.product_id.default_code
            else:
                rec.product_code = False
    


    def _prepare_stock_lot_values(self):
        self.ensure_one()

        name = self.env['stock.lot']._get_next_serial(
            self.company_id,
            self.product_id
        )

        return {
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': name,
        }


    def action_generate_serial(self):
        wc = self.workorder_ids[:1].workcenter_id
        ctx = dict(self.env.context)

        if wc and wc.code:
            ctx['machine_code'] = wc.code

        res = super(MrpProduction, self.with_context(ctx)).action_generate_serial()

        for production in self:
            if production.lot_producing_id:

                production.serial_line_ids.unlink()

                self.env['mrp.production.serial.line'].create({
                    'production_id': production.id,
                    'serial_number': production.lot_producing_id.name,
                    'location_id': production.location_dest_id.id,
                    'quantity': production.qty_producing,
                    'uom_id': production.product_uom_id.id,
                    'total_input': production.product_qty,
                })

        return res
    

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
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        self.bom_id = False

        return res
    

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
                    'thickness': move.thickness,
                    'thickness_uom': move.thickness_uom,
                    'width': move.width,
                    'width_uom': move.width_uom,
                    'core_id': move.core_id,
                    'length': move.length,
                    'length_uom': move.length_uom,
                    'recived': move.recived,
                    'billed': move.billed,
                    'film_category': move.film_category,
                    'film': move.film,
                    'film_type': move.film_type,
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
            # if not mo.product_code:
            #     mo.product_code = mo.action_product_code()

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
                'thickness': line.thickness,
                'thickness_uom': line.thickness_uom,
                'core_id': line.core_id,
                'weight': line.quantity,
                'width_uom': line.width_uom,
                'width': line.width,
                'width_uom': line.width_uom,
                'length': line.length,
                'length_uom': line.length_uom,
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

    def action_product_code(self):
        month_code = {
            1: 'A', 2: 'B', 3: 'C', 4: 'D',
            5: 'E', 6: 'F', 7: 'G', 8: 'H',
            9: 'I', 10: 'J', 11: 'K', 12: 'L',
        }
        today = date.today()
        year = today.year
        month = month_code[today.month]
        wc = self.workorder_ids[:1].workcenter_id or \
            self.bom_id.operation_ids[:1].workcenter_id

        machine_code = wc.code if wc and wc.code else 'X'
        print("=====machine_code===",machine_code)

        prefix = f"{machine_code}{year}{month}"
        print("====prefix==",prefix)
        last_mo = self.search(
            [('product_code', 'like', prefix + '%')],
            order='product_code desc',
            limit=1
        )

        seq = 1
        if last_mo and last_mo.product_code:
            last_seq = last_mo.product_code[-4:]
            if last_seq.isdigit():
                seq = int(last_seq) + 1

        new_code = f"{prefix}{str(seq).zfill(4)}"
        print("----new_code-----",new_code)
        # self.product_code = new_code

        return f"{prefix}{str(seq).zfill(4)}"

       




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

    thickness = fields.Float(string='Thickness')
    thickness_uom = fields.Selection(selection=[('guage','Guage'),('micron','Micron')],default='micron',string=" ")
    width = fields.Float(string='Width')
    width_uom = fields.Selection(selection=[('mm','MM'),('inch','Inch'),('kg', 'Kg'),
                                        ('lbs', 'Lbs'),
                                        ('gm', 'Gm'),],default='mm',string=" ")
    core_id = fields.Selection(selection=[('3','3 Inch'),('6','6 Inch')],string="Core")
    length = fields.Float(string='Length')
    length_uom = fields.Selection(selection=[('m','M'),('feet','Feet')],default='feet',string=" ")
    recived = fields.Float(string='Recived')
    billed = fields.Float(string='Billed')
    film_category = fields.Char(string="Film Category",  help="This helps to categorise specific product.")
    film = fields.Char(string="Film", help="Product Film.")
    film_type = fields.Char(string="Film Type", help="Film Type")

    total_input = fields.Float(string=" Input")
    total_output = fields.Float(string=" Output")
    total_scrap = fields.Float(string=" Scrap")


class MrpProductionScrapLine(models.Model):
    _name = 'mrp.production.scrap.line'
    _description = 'MRP Production Scrap Line'

    production_scrap_id = fields.Many2one( 'mrp.production', string='Manufacturing Order',
        ondelete='cascade', required=True
    )
    serial_number_id = fields.Many2one('stock.lot',store=True)
    serial_number = fields.Char(string='Serial Number')
    location_id = fields.Many2one('stock.location', string='Destination Location', domain="[('usage', '=', 'internal')]")
    source_location_id = fields.Many2one('stock.location', string='Source Location')
    quantity = fields.Float(string='Scrap Qty')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    scrap_reason_tag_ids = fields.Many2many( comodel_name='stock.scrap.reason.tag',
        string='Scrap Reason',
    )

    thickness = fields.Float(string='Thickness')
    thickness_uom = fields.Selection(selection=[('guage','Guage'),('micron','Micron')],default='micron',string=" ")
    width = fields.Float(string='Width')
    width_uom = fields.Selection(selection=[('mm','MM'),('inch','Inch'),('kg', 'Kg'),
                                        ('lbs', 'Lbs'),
                                        ('gm', 'Gm'),],default='mm',string=" ")
    core_id = fields.Selection(selection=[('3','3 Inch'),('6','6 Inch')],string="Core")
    length = fields.Float(string='Length')
    length_uom = fields.Selection(selection=[('m','M'),('feet','Feet')],default='feet',string=" ")
    recived = fields.Float(string='Recived')
    billed = fields.Float(string='Billed')
    film_category = fields.Char(string="Film Category",  help="This helps to categorise specific product.")
    film = fields.Char(string="Film", help="Product Film.")
    film_type = fields.Char(string="Film Type", help="Film Type")


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
    _description = 'Work Center'


    code = fields.Char('Code', copy=False,required=True)

class MrpConsumables(models.Model):
    _name = 'mrp.consumables'
    _description = 'Consumables Products'

    production_id = fields.Many2one('mrp.production',string='Manufacturing Order',
        ondelete='cascade'
    )
    product_id = fields.Many2one('product.product',string='Consumable Product',required=True,)
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom',string='UoM', related='product_id.uom_id',store=True,readonly=True)

    location_id = fields.Many2one('stock.location',string='Source Location',required=True,
        domain="[('usage', '=', 'internal')]"
    )

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_finish(self):
        res = super().button_finish()

        for wo in self:
            mo = wo.production_id
            if mo and not mo.product_code:
                mo.action_product_code()   

        return res