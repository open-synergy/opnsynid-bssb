# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    # @api.multi
    # def _picking_assign(procurement_group, location_from, location_to):
    #     _super = super(StockMove, self)
    #     result = _super._picking_assign(procurement_group, location_from, location_to)
    #     for move in self:
    #         if move.move_orig_ids:
    #             for move1 in move.move_orig_ids:
    #                 if move1.picking_id.operating_unit_id:
    #                     move.picking_id.write({"operating_unit_id": move1.picking_id.operating_unit_id})
    #     return result
