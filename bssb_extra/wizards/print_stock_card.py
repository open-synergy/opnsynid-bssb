# -*- coding: utf-8 -*-
# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import fields, models


class PrintStockCard(models.TransientModel):
    _inherit = "stock.print_stock_card"

    location_ids = fields.Many2many(
        comodel_name="stock.location",
        domain=[
            ("usage", "=", "internal"),
        ],
    )

    product_ids = fields.Many2many(
        comodel_name="product.product",
        required=False,
    )
