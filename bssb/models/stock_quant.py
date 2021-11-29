# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    operating_unit_id = fields.Many2one(
        string="Operating Unit",
        comodel_name="operating.unit",
        default=lambda self: self.env["res.users"].operating_unit_default_get(
            self._uid
        ),
    )

    @api.model
    def create(self, values):
        _super = super(StockQuant, self)
        result = _super.create(values)
        move = result.history_ids[0]
        if move.picking_id:
            picking = move.picking_id
            ou_id = picking.operating_unit_id and picking.operating_unit_id.id or False
            result.write({"operating_unit_id": ou_id})
        return result

    @api.multi
    def _prepare_fixed_asset_data(self):
        self.ensure_one()
        _super = super(StockQuant, self)
        result = _super._prepare_fixed_asset_data()
        move = self.history_ids[0]  # TODO: Error prone?
        if move.picking_id:
            picking = move.picking_id
            operating_unit_id = (
                picking.operating_unit_id and picking.operating_unit_id.id or False
            )
        result.update(
            {
                "operating_unit_id": operating_unit_id,
            }
        )
        return result
