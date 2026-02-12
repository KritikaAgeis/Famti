from odoo import models, fields,api, _
import logging
_logger = logging.getLogger(__name__)

class UOMConversionWizard(models.TransientModel):
    _name = "uom.convert.wizard"
    _description = "UOM Conversion Wizard"

    uom_id = fields.Selection([('kg','Kilogram (kg)'),('gm','Gram (g)'),('lbs','Pound (lb)'),('oz',' Ounce (oz)'),('ton','• Ton / Metric Ton')],string="UOM",default='kg')

    purchase_id = fields.Many2one('purchase.order')

    po_lines = fields.One2many(
        'uom.convert.wizard.line',
        'wizard_id',
        string="PO Lines"
    )

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #
    #     po = self.env['purchase.order'].browse(
    #         self.env.context.get('active_id')
    #     )
    #
    #     if po:
    #         res['purchase_id'] = po.id
    #
    #         lines = []
    #         for line in po.order_line:
    #             lines.append((0, 0, {
    #                 'po_line_id': line.id,
    #             }))
    #         res['po_lines'] = lines
    #
    #     return res

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        print(f'-line 46---{self}--{self.env.context}-{fields_list}----{res}')
        po = self.env['purchase.order'].browse(
            self.env.context.get('order_id')
        )
        print(f'-line 46--------{po}')

        if po:
            res['purchase_id'] = po.id
            lines = []
            for line in po.order_line:
                lines.append((0, 0, {
                    'po_line_id': line.id,

                    # COPY BASE VALUES
                    'base_weight': line.weight_val,
                    'base_width': line.width_val,
                    'base_length': line.length_val,
                    'base_thickness': line.thickness_val,
                }))

            res['po_lines'] = lines

        return res



class UOMConversionWizardLine(models.TransientModel):
    _name = "uom.convert.wizard.line"
    _description = "UOM Conversion Wizard Line"

    wizard_id = fields.Many2one('uom.convert.wizard', ondelete='cascade')
    po_line_id = fields.Many2one('purchase.order.line')

    product_id = fields.Many2one(
        related='po_line_id.product_id',
        readonly=True
    )

    # ---------------- BASE FROM PO ----------------

    # base_weight = fields.Float(
    #     related='po_line_id.weight_val',
    #     store=True,
    #     readonly=True,
    # )
    # base_width = fields.Float(
    #     related='po_line_id.width_val',
    #     store=True,
    #     readonly=True,
    # )
    # base_length = fields.Float(
    #     related='po_line_id.length_val',
    #     store=True,
    #     readonly=True,
    # )
    # base_thickness = fields.Float(
    #     related='po_line_id.thickness_val',
    #     store=True,
    #     readonly=True,
    # )

    base_weight=fields.Float()
    base_width = fields.Float()
    base_length = fields.Float()
    base_thickness = fields.Float()

    # ---------------- CONVERTED ----------------

    weight_val = fields.Float(compute='_compute_converted_vals')
    weight_uom = fields.Selection(
        [('kg','Kg'),('gm','Gram'),('lbs','Lb'),('ton','Ton'),('oz','Ounce')],
        compute='_compute_converted_vals'
    )

    width_val = fields.Float(compute='_compute_converted_vals')
    width_uom = fields.Selection(
        [('mm','MM'),('inch','Inch')],
        compute='_compute_converted_vals'
    )

    length_val = fields.Float(compute='_compute_converted_vals')
    length_uom = fields.Selection(
        [('m','Meter'),('feet','Feet')],
        compute='_compute_converted_vals'
    )

    thickness_val = fields.Float(compute='_compute_converted_vals')
    thickness_uom = fields.Selection(
        [('mm','MM'),('mil','Mil')],
        compute='_compute_converted_vals'
    )

    @api.depends(
        'wizard_id.uom_id',
        'po_line_id.weight_val',
        'po_line_id.width_val',
        'po_line_id.length_val',
        'po_line_id.thickness_val',
    )
    def _compute_converted_vals(self):
        print(f'-line 46--------{self.env.context}--{self.env.context.get("active_id")}')
        active_id = self.env.context.get("active_id") or []
        print(f"lines==",active_id)
        if isinstance(active_id, str):
            import re
            active_ids = list(map(int, re.findall(r'\d+', active_id)))

        lines = self.env['purchase.order.line'].browse(active_ids)
        print(f'lines==',lines)
        for po_line,line in zip(lines,self):
            print(f'-line 4144---{self}----{line}--{type(line)}--')
            bw = po_line.weight_val or 0.0
            bwid = po_line.width_val or 0.0
            bl = po_line.length_val or 0.0
            bt = po_line.thickness_val or 0.0

            uom = self.wizard_id.uom_id or 'kg'
            if uom == 'gm':
                line.weight_val = bw * 1000
                line.weight_uom = 'gm'
            elif uom == 'lbs':
                line.weight_val = bw * 2.20462
                line.weight_uom = 'lbs'
            elif uom == 'ton':
                line.weight_val = bw / 1000
                line.weight_uom = 'ton'
            elif uom == 'oz':
                line.weight_val = bw * 35.274
                line.weight_uom = 'oz'
            else:
                line.weight_val = bw
                line.weight_uom = 'kg'

            # -------- WIDTH --------
            if uom in ('lbs', 'oz'):
                line.width_val = bwid / 25.4
                line.width_uom = 'inch'
            else:
                line.width_val = bwid
                line.width_uom = 'mm'

            # -------- LENGTH --------
            if uom in ('lbs', 'oz'):
                line.length_val = bl
                line.length_uom = 'feet'
            else:
                line.length_val = bl * 0.3048
                line.length_uom = 'm'

            # -------- THICKNESS --------
            if uom in ('lbs', 'oz'):
                line.thickness_val = bt / 25.4
                line.thickness_uom = 'mil'
            else:
                line.thickness_val = bt / 1000
                line.thickness_uom = 'mm'
