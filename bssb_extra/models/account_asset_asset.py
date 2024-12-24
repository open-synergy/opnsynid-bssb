# -*- coding: utf-8 -*-
# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountAssetAsset(models.Model):
    _inherit = "account.asset.asset"

    account_asset_id = fields.Many2one(
        string="Asset Account",
        comodel_name="account.account",
        related="category_id.account_asset_id",
        readonly=True,
        store=True,
    )
    account_depreciation_id = fields.Many2one(
        string="Depreciation Account",
        comodel_name="account.account",
        related="category_id.account_depreciation_id",
        readonly=True,
        store=True,
    )
    account_expense_depreciation_id = fields.Many2one(
        string="Depr. Expense Account",
        comodel_name="account.account",
        related="category_id.account_expense_depreciation_id",
        readonly=True,
        store=True,
    )
    account_plus_value_id = fields.Many2one(
        string="Plus-Value Account",
        comodel_name="account.account",
        related="category_id.account_plus_value_id",
        readonly=True,
        store=True,
    )
    account_min_value_id = fields.Many2one(
        string="Min-Value Account",
        comodel_name="account.account",
        related="category_id.account_min_value_id",
        readonly=True,
        store=True,
    )
    account_residual_value_id = fields.Many2one(
        string="Residual Value Account",
        comodel_name="account.account",
        related="category_id.account_residual_value_id",
        readonly=True,
        store=True,
    )
    accounting_category_id = fields.Many2one(
        string="Accounting Category",
        comodel_name="fixed_asset_accounting_category",
    )  

    @api.onchange(
        "category_id"
    )  
    def onchange_accounting_category_id(self):
        self.accounting_category_id = False
        if self.category_id:
            self.accounting_category_id = self.category_id.accounting_category_id
