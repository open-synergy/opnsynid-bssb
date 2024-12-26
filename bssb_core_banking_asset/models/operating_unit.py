# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    cb_group_id = fields.Many2one(
        string="Core Banking Group",
        comodel_name="cb_group",
    )
