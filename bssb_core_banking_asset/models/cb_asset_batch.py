# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json
import os
import tempfile
from datetime import datetime

import requests
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class CoreBankingAssetBatch(models.Model):
    _name = "cb_asset_batch"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
    ]
    _description = "Core Banking Asset Batch"

    name = fields.Char(
        string="# Batch",
        default="/",
        required=True,
        copy=False,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        },
    )
    date = fields.Date(
        string="Date",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    date_start = fields.Date(
        string="Date Start",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    date_end = fields.Date(
        string="Date End",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
    )
    depreciation_account_id = fields.Many2one(
        string="Depreciation Account",
        comodel_name="account.account",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
    )
    depreciation_expense_account_id = fields.Many2one(
        string="Depreciation Expense Account",
        comodel_name="account.account",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
    )
    depreciation_amount_method = fields.Selection(
        string="Depreciation Amount Method",
        selection=[
            ("manual", "Manual"),
            ("automatic", "Automatic"),
        ],
        default="manual",
    )

    @api.multi
    @api.depends(
        "depreciation_amount_method",
    )
    def _compute_automatic_depreciation_amount(self):
        for document in self:
            result = 0.0
            document.automatic_depreciation_amount = result

    automatic_depreciation_amount = fields.Float(
        string="Automatic Depreciation Amount",
        compute="_compute_automatic_depreciation_amount",
        store=True,
        compute_sudo=True,
    )

    @api.multi
    @api.depends(
        "depreciation_amount_method",
    )
    def _compute_manual_depreciation_amount(self):
        for document in self:
            result = 0.0
            document.manual_depreciation_amount = result

    manual_depreciation_amount = fields.Float(
        string="Manual Depreciation Amount",
        compute="_compute_manual_depreciation_amount",
        store=True,
        compute_sudo=True,
    )

    @api.multi
    @api.depends(
        "automatic_depreciation_amount",
        "manual_depreciation_amount",
    )
    def _compute_final_depreciation_amount(self):
        for document in self:
            result = 0.0
            document.final_depreciation_amount = result

    final_depreciation_amount = fields.Float(
        string="Final Depreciation Amount",
        compute="_compute_final_depreciation_amount",
        store=True,
        compute_sudo=True,
    )
    description = fields.Text(
        string="Description",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        default="draft",
        copy=False,
    )

    @api.model
    def _get_cb_asset_backend_id(self):
        company = self.env.user.company_id
        backend = company.cb_asset_backend_id
        return backend and backend.id or False

    cb_asset_backend_id = fields.Many2one(
        string="Backend",
        comodel_name="cb_asset_backend",
        default=lambda self: self._get_cb_asset_backend_id(),
        required=True,
    )

    @api.model
    def _get_is_admin(self):
        result = False
        if self.env.user.has_group("base.group_system"):
            result = True
        return result

    is_admin = fields.Boolean(
        string="Is Admin?",
        default=lambda self: self._get_is_admin(),
    )
    response_msg = fields.Text(
        string="Response",
        copy=True,
    )

    @api.constrains(
        "date_start",
        "date_end",
    )
    def _check_tanggal(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    msg_err = _("Date Start cannot be greater than Date End")
                    raise UserError(msg_err)
                
    @api.multi
    def _set_response(self, resp_type, response_msg):
        self.ensure_one()
        self.write(
            {
                "response_msg": response_msg,
            }
        )
        if resp_type == "failed":
            return False
        else:
            return True    
                
    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
        }
    
    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update(
            {
                "ir_sequence_date": self.date,
            }
        )
        sequence = self.with_context(ctx)._create_sequence()
        return {
            "state": "confirm",
            "name": sequence,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
        }
                
    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())

    @api.multi
    def _prepare_data_core_banking(self):
        company = self.env.user.company_id
        backend = company.cb_asset_backend_id
        data = {
            "APP_ID": backend.app_id,
            "NO_TRANS": self.name,
            "REK_DEBET": self.warehouse_id.code + self.depreciation_expense_account_id.code,
            "NOMINAL_DEBET": self.final_depreciation_amount,
            "KET_DEBET": self.description,
            "NOTLP_DEBET": "",
            "JENIS_TRANS": "0200",
        }
        # Range nanti diganti sama line_ids
        for i in range(1,4):
            rek_kredit = "REK_KREDIT" + str(i)
            nominal_kredit = "NOMINAL_KREDIT" + str(i)
            ket_kredit = "KET_KREDIT" + str(i)
            notlp_kredit = "NOTLP_KREDIT" + str(i)
            data[rek_kredit] = self.warehouse_id.code + self.depreciation_account_id.code
            data[nominal_kredit] = self.final_depreciation_amount
            data[ket_kredit] = self.description
            data[notlp_kredit] = ""
            i+=1

        return data
    
    @api.multi
    def _get_token(self):
        self.ensure_one()
        company = self.env.user.company_id
        backend = company.cb_asset_backend_id

        if not backend:
            msg_err = _("Backend Not Found")
            return self._set_response("failed", msg_err)

        url = backend.base_url + backend.api_token

        payload = json.dumps({
            "user": backend.username,
            "password": backend.password,
        })
        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload
            )
            result = response.json()
            code = result["code"]
            if code == "00":
                backend.token = result["message"]
                msg_err = _(
                    """
                Status: Success
                API: %s
                Payload: %s
                Response: %s
                """
                    % (url, payload, response.text)
                )
                return self._set_response("success", msg_err)
            else:
                msg_err = _(
                    """
                Status: Error
                API: %s
                Payload: %s
                Response: %s
                """
                    % (url, payload, response.text)
                )
                return self._set_response("failed", msg_err)
        except requests.exceptions.Timeout as e:
            msg_err = _(
                """
            Status: Timeout
            API: %s
            Payload: %s
            Massage Error: %s
            """
                % (url, payload, e)
            )
            return self._set_response("failed", msg_err)
        except requests.exceptions.ConnectionError as e:
            msg_err = _(
                """
            Status: ConnectionError
            API: %s
            Payload: %s
            Massage Error: %s
            """
                % (url, payload, e)
            )
            return self._set_response("failed", msg_err)
        except ValueError as e:
            msg_err = _(
                """
            Status: ValueError
            API: %s
            Payload: %s
            Massage Error: %s
            """
                % (url, payload, e)
            )
            return self._set_response("failed", msg_err)            
    
    @api.multi
    def _send_2_core_banking(self, data):
        self.ensure_one()
        company = self.env.user.company_id
        backend = company.cb_asset_backend_id

        if not backend:
            msg_err = _("Backend Not Found")
            return self._set_response("failed", msg_err)
        if not backend.token:
            msg_err = _("Token Not Found")
            return self._set_response("failed", msg_err)

        url = backend.base_url + backend.api_endpoint

        headers = {
            "Authorization": "Bearer " + backend.token,
        }
        try:
            response = requests.request(
                "POST", url, headers=headers, json=data
            )
            if response.status_code == 200:
                self.action_done()
                msg_err = _(
                    """
                Status: Success
                API: %s
                Payload: %s
                Response: %s
                """
                    % (url, payload, response.text)
                )
                return self._set_response("success", msg_err)
            else:
                msg_err = _(
                    """
                Status: Error
                API: %s
                Payload: %s
                Response: %s
                """
                    % (url, payload, response.text)
                )
                return self._set_response("success", msg_err)                
        except requests.exceptions.Timeout as e:
            msg_err = _(
                """
            Status: Timeout
            API: %s
            Payload: %s
            Message Error: %s
            """
                % (url, payload, e)
            )
            return self._set_response("failed", msg_err)
        except requests.exceptions.ConnectionError as e:
            msg_err = _(
                """
            Status: ConnectionError
            API: %s
            Payload: %s
            Message Error: %s
            """
                % (url, payload, e)
            )
            return self._set_response("failed", msg_err)
        except ValueError as e:
            msg_err = _(
                """
            Status: ValueError
            API: %s
            Payload: %s
            Massage Error: %s
            """
                % (url, payload, e)
            )
            return self._set_response("failed", msg_err)

    @api.multi
    def action_send(self):
        for document in self:
            if document._get_token():
                data = self._prepare_data_core_banking()
                document._send_2_core_banking(data)
