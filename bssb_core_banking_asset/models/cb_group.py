# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class CoreBankingGroup(models.Model):
    _name = "cb_group"
    _description = "Core Banking Group"


    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    ) 
    operating_unit_ids = fields.One2many(
        string="Operating Units",
        comodel_name="operating.unit",
        inverse_name="cb_group_id",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    # POLICY
    cb_asset_confirm_group_ids = fields.Many2many(
        string="Allowed to Confirm",
        comodel_name="res.groups",
        relation="rel_cb_group_2_group_confirm",
        column1="cb_group_id",
        column2="group_id",
    )
    cb_asset_send_group_ids = fields.Many2many(
        string="Allowed to Send",
        comodel_name="res.groups",
        relation="rel_cb_group_2_group_send",
        column1="cb_group_id",
        column2="group_id",
    )
    cb_asset_cancel_group_ids = fields.Many2many(
        string="Allowed to Cancel",
        comodel_name="res.groups",
        relation="rel_cb_group_2_group_cancel",
        column1="cb_group_id",
        column2="group_id",
    )
    cb_asset_restart_group_ids = fields.Many2many(
        string="Allowed to Restart",
        comodel_name="res.groups",
        relation="rel_cb_group_2_group_restart",
        column1="cb_group_id",
        column2="group_id",
    )