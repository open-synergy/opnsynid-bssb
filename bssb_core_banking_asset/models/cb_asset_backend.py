# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json

import requests
from openerp import _, api, fields, models


class CoreBankingAssetBackend(models.Model):
    _name = "cb_asset_backend"
    _description = "Core Banking Asset Backend"

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        default="/",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        copy=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("running", "Running"),
        ],
        copy=False,
        default="draft",
        required=True,
        readonly=True,
    )

    # GENERAL
    base_url = fields.Char(
        string="Base URL",
        required=True,
    )
    api_endpoint = fields.Char(
        string="API Endpoint",
        required=True,
    )
    api_token = fields.Char(
        string="API Token",
        required=True,
    )
    username = fields.Char(
        string="Username",
        required=True,
    )
    password = fields.Char(
        string="Password",
        required=True,
    )
    token = fields.Text(
        string="Token",
    )
    app_id = fields.Char(
        string="App ID",
    )
    response_msg = fields.Text(
        string="Response",
        copy=True,
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            if rec.code:
                name = "[{}] {}".format(rec.code, rec.name)
            else:
                name = "%s" % (rec.name)
            result.append((rec.id, name))
        return result

    @api.multi
    def action_running(self):
        for record in self:
            check_running_backend_ids = self.search(
                [
                    ("state", "=", "running"),
                    ("company_id", "=", self.env.user.company_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if check_running_backend_ids:
                check_running_backend_ids.write({"state": "draft"})
            record.company_id.write({"cb_asset_backend_id": record.id})
            record.write({"state": "running"})

    @api.multi
    def action_restart(self):
        for record in self:
            record.company_id.write({"cb_asset_backend_id": False})
            record.write({"state": "draft"})

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
    def _get_token(self):
        self.ensure_one()

        url = self.base_url + self.api_token

        payload = json.dumps({
            "user": self.username,
            "password": self.password,
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
    def action_test_connection(self):
        for record in self:
            record._get_token()
