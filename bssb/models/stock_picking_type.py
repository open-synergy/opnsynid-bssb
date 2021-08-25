# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    operating_unit_ids = fields.Many2many(
        string="Allowed Operating Unit(s)",
        comodel_name="operating.unit",
        relation="rel_stock_picking_type_2_ou",
        column1="picking_type_id",
        column2="operating_unit_id",
    )
