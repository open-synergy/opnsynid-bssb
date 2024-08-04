# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockQuantOperatingUnitChange(models.Model):
    _inherit = "stock.quant_operating_unit_change"

    @api.onchange(
        "lot_id",
    )
    def onchange_source_operating_unit_id(self):
        self.source_operating_unit_id = False
        if self.lot_id:
            if len(self.lot_id.quant_ids) > 0:
                self.source_operating_unit_id = \
                    self.lot_id.quant_ids[-1].operating_unit_id.id

