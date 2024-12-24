# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class AccountAssetCategory(models.Model):
    _name = "account.asset.category"
    _inherit = "account.asset.category"


  
    accounting_category_id = fields.Many2one(
        string="Accounting Category",
        comodel_name="fixed_asset_accounting_category",
    )
