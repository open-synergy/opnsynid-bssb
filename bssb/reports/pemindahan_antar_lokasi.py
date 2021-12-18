# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

import pytz
from openerp.report import report_sxw


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.context = context
        self.nomor = 0
        self.localcontext.update(
            {
                "convert_datetime_utc": self._convert_datetime_utc,
                "nomor": self._get_nomor,
            }
        )

    def _convert_datetime_utc(self, dt):
        if dt:
            obj_user = self.pool.get("res.users")
            user = obj_user.browse(self.cr, self.uid, [self.uid])[0]
            convert_dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            if user.tz:
                tz = pytz.timezone(user.tz)
            else:
                tz = pytz.utc
            convert_utc = pytz.utc.localize(convert_dt).astimezone(tz)
            format_utc = convert_utc.strftime("%d %b %Y %H:%M:%S")

            return format_utc
        else:
            return "-"

    def _get_nomor(self):
        self.nomor += 1
        return self.nomor
