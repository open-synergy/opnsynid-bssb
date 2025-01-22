# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json
import os
import tempfile
from datetime import datetime
from dateutil.relativedelta import relativedelta

import requests
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class CoreBankingAssetBatch(models.Model):
    _name = "cb_asset_batch"
    _inherit = [
        "mail.thread",
        "tier.validation",
        "base.workflow_policy_object",
        "base.sequence_document",
    ]
    _description = "Core Banking Asset Batch"

    _state_from = ["draft", "confirm"]
    _state_to = ["open"]

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

    @api.model
    def _domain_cb_group_id(self):
        return [('operating_unit_ids', 'in', self.env.user.operating_unit_ids.ids)]
    
    cb_group_id = fields.Many2one(
        string="Core Banking Group",
        comodel_name="cb_group",
        readonly=True,
        required=True,
        domain=_domain_cb_group_id,
        states={
            "draft": [("readonly", False)],
        },
    )
    accounting_category_id = fields.Many2one(
        string="Accounting Category",
        comodel_name="fixed_asset_accounting_category",
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
        default="automatic",
    )

    depreciation_line_ids = fields.Many2many(
        string="Depreciation Lines",
        comodel_name="account.asset.depreciation.line",
        rel="rel_asset_batch_2_depr_line",
        col1="batch_id",
        col2="line_id",
        required=False,
        states={
            "draft": [("readonly", False)],
        },        
    )

    @api.multi
    @api.depends(
        "depreciation_line_ids",
        "depreciation_line_ids.amount",
    )
    def _compute_automatic_depreciation_amount(self):
        for document in self:
            result = 0.0
            for line in document.depreciation_line_ids:
                result += line.amount
            document.automatic_depreciation_amount = result

    automatic_depreciation_amount = fields.Float(
        string="Automatic Depreciation Amount",
        compute="_compute_automatic_depreciation_amount",
        store=True,
        compute_sudo=True,
    )

    manual_depreciation_amount = fields.Float(
        string="Manual Depreciation Amount",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
    )

    @api.multi
    @api.depends(
        "depreciation_amount_method",
        "automatic_depreciation_amount",
        "manual_depreciation_amount",
    )
    def _compute_final_depreciation_amount(self):
        for document in self:
            result = 0.0
            if document.depreciation_amount_method == "manual":
                result = document.manual_depreciation_amount
            else:
                result = document.automatic_depreciation_amount
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
        required=False,
        states={
            "draft": [("readonly", False)],
        },
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        default="draft",
        copy=False,
    )

    @api.multi
    def _compute_policy(self):
        _super = super(CoreBankingAssetBatch, self)
        _super._compute_policy()

    # Policy Field
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    send_ok = fields.Boolean(
        string="Can Send",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )
    restart_validation_ok = fields.Boolean(
        string="Can Restart Validation",
        compute="_compute_policy",
    )

    @api.onchange(
        "accounting_category_id"
    )
    def onchange_depreciation_account_id(self):
        self.depreciation_account_id = False
        if self.accounting_category_id:
            self.depreciation_account_id = self.accounting_category_id.account_depreciation_id

    @api.onchange(
        "accounting_category_id"
    )
    def onchange_depreciation_expense_account_id(self):
        self.depreciation_expense_account_id = False
        if self.accounting_category_id:
            self.depreciation_expense_account_id = self.accounting_category_id.account_expense_depreciation_id

    @api.onchange(
        "date_start",
        "date_end",
    )
    def onchange_description(self):
        result = ""
        if self.date_start and self.date_end:
            result = "Penyusutan aset %s S.D. %s" % (self.date_start, self.date_end)
        self.description = result


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
                
    @api.constrains(
        "date",
        "date_end",
    )
    def _check_periode_date_end(self):
        for record in self:
            if record.date and record.date_end:
                cb_date = datetime.strptime(self.date, "%Y-%m-%d")
                cb_date += relativedelta(day=1)
                check_date = cb_date + relativedelta(
                    months=1, days=-1
                )
                if record.date_end > check_date.strftime("%Y-%m-%d"):
                    msg_err = _("Date End cannot be greater than %s") % (check_date.strftime("%d-%m-%Y"))
                    raise UserError(msg_err)

    @api.multi
    def _set_response(self, resp_type, response_msg, response):
        self.ensure_one()
        self.write(
            {
                "response_msg": response_msg,
            }
        )
        self.env.cr.commit()
        if resp_type == "failed":
            msg_err = _("%s") % (response)
            raise UserError(msg_err)
        else:
            return True   

    @api.multi
    def _prepare_open_data(self):
        self.ensure_one()
        return {
            "state": "open",
        } 
                
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
    def _prepare_open_data(self):
        self.ensure_one()
        return {
            "state": "open",
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
        }
    

    @api.multi
    def validate_tier(self):
        _super = super(CoreBankingAssetBatch, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_open()

    @api.multi
    def action_open(self):
        for document in self:
            document.write(document._prepare_open_data())

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
            document._load_depreciation_line()
            document.request_validation()

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())

    @api.multi
    def action_load_depreciation_line(self):
        for document in self:
            document._load_depreciation_line()

    @api.multi
    def _load_depreciation_line(self):
        self.ensure_one()
        Line = self.env["account.asset.depreciation.line"]
        criteria = [
            ("type", "=", "depreciate"),
            ("subtype_id", "=", False),
            ("move_check", "=", False),
            ("init_entry", "=", False),
            ("line_date", ">=", self.date_start),
            ("line_date", "<=", self.date_end),
            ("asset_id.state", "=", "open"),
            ("asset_id.operating_unit_id.cb_group_id", "=", self.cb_group_id.id),
            ("asset_id.accounting_category_id.id", "=", self.accounting_category_id.id),
        ]
        lines = Line.search(criteria)
        # raise UserError(str(lines))
        self.write({
            "depreciation_line_ids": [(6, 0, lines.ids)]
        })

    @api.multi
    def _prepare_data_core_banking(self):
        backend = self.cb_asset_backend_id
        rek_debit = self.cb_group_id.code + self.depreciation_expense_account_id.code.replace(".","")
        rek_credit = self.cb_group_id.code + self.depreciation_account_id.code.replace(".","")
        data = {
            "APP_ID": backend.app_id,
            "NO_TRANS": self.name,
            "REK_DEBET": rek_debit,
            "NOMINAL_DEBET": self.final_depreciation_amount,
            "KET_DEBET": self.description,
            "NOTLP_DEBET": "",
            "JENIS_TRANS": "0200",
            "REK_KREDIT1": rek_credit,
            "NOMINAL_KREDIT1": self.final_depreciation_amount,
            "KET_KREDIT1": self.description,
            "NOTLP_KREDIT1": "",
        }
        return data
    
    @api.multi
    def _get_token(self):
        self.ensure_one()
        backend = self.cb_asset_backend_id

        if not backend:
            msg_err = _("Backend Not Found")
            return self._set_response("failed", msg_err, msg_err)

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
                return self._set_response("success", msg_err, response.text)
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
                return self._set_response("failed", msg_err, response.text)
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
            return self._set_response("failed", msg_err, e)
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
            return self._set_response("failed", msg_err, e)
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
            return self._set_response("failed", msg_err, e)            
    
    @api.multi
    def _send_2_core_banking(self, data):
        self.ensure_one()
        backend = self.cb_asset_backend_id

        if not backend:
            msg_err = _("Backend Not Found")
            return self._set_response("failed", msg_err, msg_err)
        if not backend.token:
            msg_err = _("Token Not Found")
            return self._set_response("failed", msg_err, msg_err)

        url = backend.base_url + backend.api_endpoint

        headers = {
            "Authorization": "Bearer " + backend.token,
        }
        try:
            response = requests.request(
                "POST", url, headers=headers, json=data
            )
            if response.status_code == 200:
                try:
                    success_code = response.text[1:3]
                    if success_code == "00":
                        self.action_done()
                        msg_err = _(
                            """
                        Status: Success
                        API: %s
                        Data: %s
                        Response: %s
                        """
                            % (url, data, response.text)
                        )
                        self.depreciation_line_ids.action_mark_as_init()
                        return self._set_response("success", msg_err, response.text)
                    else:
                        msg_err = _(
                            """
                        Status: Error status code
                        API: %s
                        Data: %s
                        Response: %s
                        """
                            % (url, data, (response.text + " status code " + success_code))
                        )
                        return self._set_response("success", msg_err, response.text)                         
                except:
                    msg_err = _(
                        """
                    Status: Error parsing status code
                    API: %s
                    Data: %s
                    Response: %s
                    """
                        % (url, data, (response.text + " " + success_code))
                    )
                    return self._set_response("success", msg_err, response.text)                     
            else:
                msg_err = _(
                    """
                Status: Error
                API: %s
                Data: %s
                Response: %s
                """
                    % (url, data, response.text)
                )
                return self._set_response("success", msg_err, response.text)                
        except requests.exceptions.Timeout as e:
            msg_err = _(
                """
            Status: Timeout
            API: %s
            Data: %s
            Message Error: %s
            """
                % (url, data, e)
            )
            return self._set_response("failed", msg_err, e)
        except requests.exceptions.ConnectionError as e:
            msg_err = _(
                """
            Status: ConnectionError
            API: %s
            Data: %s
            Message Error: %s
            """
                % (url, data, e)
            )
            return self._set_response("failed", msg_err, e)
        except ValueError as e:
            msg_err = _(
                """
            Status: ValueError
            API: %s
            Data: %s
            Massage Error: %s
            """
                % (url, data, e)
            )
            return self._set_response("failed", msg_err, e)

    @api.multi
    def action_send(self):
        for document in self:
            if document._get_token():
                data = self._prepare_data_core_banking()
                document._send_2_core_banking(data)
