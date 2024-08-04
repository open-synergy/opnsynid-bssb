# -*- coding: utf-8 -*-
# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp import tools


class LaporanDepresiasiBulanan(models.Model):
    _name = "laporan_depresiasi_bulanan"
    _description = "Laporan Depresiasi Bulanan"
    _auto = False

    asset_id = fields.Many2one(
        string="# Asset",
        comodel_name="account.asset.asset",
    )
    date = fields.Date(
        string="Date",
    )
    operating_unit_id = fields.Many2one(
        string="# Operating Unit",
        comodel_name="operating.unit",
    )
    amount = fields.Float(
        string="Amount",
    )
    category_id = fields.Many2one(
        string="# Category",
        comodel_name="account.asset.category",
    )
    account_asset_id = fields.Many2one(
        string="# Asset Account",
        comodel_name="account.account",
    )
    account_depreciation_id = fields.Many2one(
        string="# Depreciation Account",
        comodel_name="account.account",
    )
    account_expense_depreciation_id = fields.Many2one(
        string="Depr. Expense Account",
        comodel_name="account.account",
    )
    account_plus_value_id = fields.Many2one(
        string="Plus-Value Account",
        comodel_name="account.account",
    )
    account_min_value_id = fields.Many2one(
        string="Min-Value Account",
        comodel_name="account.account",
    )
    account_residual_value_id = fields.Many2one(
        string="Residual Value Account",
        comodel_name="account.account",
    )

    def _select(self):
        select_str = """
        SELECT
            a.id AS id,
            a.asset_id AS asset_id,
            a.line_date AS date,
            b.operating_unit_id AS operating_unit_id,
            a.amount AS amount,
            b.category_id AS category_id,
            b.account_asset_id AS account_asset_id,
            b.account_depreciation_id AS account_depreciation_id,
            b.account_expense_depreciation_id AS account_expense_depreciation_id,
            b.account_plus_value_id AS account_plus_value_id,
            b.account_min_value_id AS account_min_value_id,
            b.account_residual_value_id AS account_residual_value_id
        """
        return select_str

    def _from(self):
        from_str = """
        account_asset_depreciation_line AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1 AND 
            a.type = 'depreciate' AND 
            (a.init_entry IS TRUE OR a.move_check IS TRUE) AND
            a.subtype_id IS NULL
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN account_asset_asset AS b ON a.asset_id = b.id
        """
        return join_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        # pylint: disable=locally-disabled, sql-injection
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            %s
            %s
        )""" % (
            self._table,
            self._select(),
            self._from(),
            self._join(),
            self._where()
            # self._group_by()
        ))
