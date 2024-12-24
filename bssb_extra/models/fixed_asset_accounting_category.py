# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class FixedAssetAccountingCategory(models.Model):
    _name = "fixed_asset_accounting_category"
    _description = "Fixed Asset Accounting Category"


    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )  
    active = fields.Boolean(
        string="Active",
        default=True,
    )       
    account_asset_id = fields.Many2one(
        string="Asset Account",
        comodel_name="account.account",
        required=True,
        domain=[("type", "=", "other")],
    )
    account_depreciation_id = fields.Many2one(
        string="Depreciation Account",
        comodel_name="account.account",
        required=True,
        domain=[("type", "=", "other")],
    )
    account_expense_depreciation_id = fields.Many2one(
        string="Depr. Expense Account",
        comodel_name="account.account",
        required=True,
        domain=[("type", "=", "other")],
    )