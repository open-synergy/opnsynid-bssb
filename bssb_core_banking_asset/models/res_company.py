# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cb_asset_backend_id = fields.Many2one(
        string="Active Core Banking Asset Backend",
        comodel_name="cb_asset_backend",
        domain="[('state', '=', 'running')]",
    )

    cb_asset_batch_sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
    )
