# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = "stock.quant"

    @api.multi
    def _prepare_fixed_asset_data(self):
        self.ensure_one()
        _super = super(StockQuant, self)
        result = _super._prepare_fixed_asset_data()
        categ = self._get_asset_category()
        accounting_category_id = categ = categ.accounting_category_id and categ.accounting_category_id.id or False
        result.update({
            "accounting_category_id": accounting_category_id,
        })
        return result
