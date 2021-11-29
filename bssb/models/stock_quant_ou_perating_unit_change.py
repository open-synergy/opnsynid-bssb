# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockQuantOperatingUnitChange(models.Model):
    _name = "stock.quant_operating_unit_change"
    _description = "Quant Operating Unit Change"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "tier.validation",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["open"]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    @api.model
    def _default_date_change(self):
        return fields.Datetime.now()

    @api.multi
    @api.depends(
        "company_id",
    )
    def _compute_policy(self):
        _super = super(StockQuantOperatingUnitChange, self)
        _super._compute_policy()

    name = fields.Char(
        string="# Document",
        required=True,
        readonly=True,
        default="/",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_change = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        default=lambda self: self._default_date_change(),
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    source_operating_unit_id = fields.Many2one(
        string="Source Operating Unit",
        comodel_name="operating.unit",
        default=lambda self: self.env["res.users"].operating_unit_default_get(
            self._uid
        ),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    dest_operating_unit_id = fields.Many2one(
        string="Destination Operating Unit",
        comodel_name="operating.unit",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    lot_id = fields.Many2one(
        string="# Lot",
        comodel_name="stock.production.lot",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
        string="State",
        required=True,
        readonly=True,
        track_visibility="onchange",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "On Progress"),
            ("valid", "Valid"),
            ("cancel", "Cancel"),
        ],
        default="draft",
        copy=False,
    )
    confirmed_date = fields.Datetime(
        string="Confirmation Date",
        readonly=True,
        copy=False,
    )
    confirmed_user_id = fields.Many2one(
        string="Confirmation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    opened_date = fields.Datetime(
        string="Opened Date",
        readonly=True,
        copy=False,
    )
    opened_user_id = fields.Many2one(
        string="Open By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    validated_date = fields.Datetime(
        string="Validation Date",
        readonly=True,
        copy=False,
    )
    validated_user_id = fields.Many2one(
        string="Validation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    cancelled_date = fields.Datetime(
        string="Cancellation Date",
        readonly=True,
        copy=False,
    )
    cancelled_user_id = fields.Many2one(
        string="Cancellation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    valid_ok = fields.Boolean(
        string="Can Validate",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    restart_validation_ok = fields.Boolean(
        string="Can Restart Validation",
        compute="_compute_policy",
    )

    @api.multi
    def validate_tier(self):
        _super = super(StockQuantOperatingUnitChange, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_open()

    @api.multi
    def restart_validation(self):
        _super = super(StockQuantOperatingUnitChange, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()

    @api.multi
    def action_confirm(self):
        for change in self:
            change.write(self._prepare_confirm_data())
            change.request_validation()

    @api.multi
    def action_open(self):
        for change in self:
            change.write(self._prepare_open_data())

    @api.multi
    def action_valid(self):
        for change in self:
            change.write(self._prepare_valid_data())

    @api.multi
    def action_cancel(self):
        for change in self:
            change.write(self._prepare_cancel_data())
            change.restart_validation()

    @api.multi
    def action_restart(self):
        for change in self:
            change.write(self._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        result = {
            "state": "confirm",
            "confirmed_user_id": self.env.user.id,
            "confirmed_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _prepare_open_data(self):
        self.ensure_one()
        result = {
            "state": "open",
            "opened_user_id": self.env.user.id,
            "opened_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _prepare_valid_data(self):
        self.ensure_one()
        self._change_quant_ownership()
        result = {
            "state": "valid",
            "validated_user_id": self.env.user.id,
            "validated_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _change_quant_ownership(self):
        self.ensure_one()
        criteria = [
            ("lot_id", "=", self.lot_id.id),
        ]
        quants = self.env["stock.quant"].search(criteria)
        quants.write({"operating_unit_id": self.dest_operating_unit_id.id})
        assets = self.env["account.asset.asset"].search(criteria)
        assets.write({"operating_unit_id": self.dest_operating_unit_id.id})

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        result = {
            "state": "cancel",
            "cancelled_user_id": self.env.user.id,
            "cancelled_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        result = {
            "state": "draft",
            "confirmed_user_id": False,
            "confirmed_date": False,
            "validated_user_id": False,
            "validated_date": False,
            "cancelled_user_id": False,
            "cancelled_date": False,
        }
        return result

    @api.model
    def create(self, values):
        _super = super(StockQuantOperatingUnitChange, self)
        result = _super.create(values)
        ctx = self.env.context.copy()
        ctx.update(
            {
                "ir_sequence_date": result.date_change,
            }
        )
        sequence = result.with_context(ctx)._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )

        return result
