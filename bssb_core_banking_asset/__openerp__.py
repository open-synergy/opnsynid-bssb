# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BSBB - Core Banking Asset",
    "version": "8.0.1.0.0",
    "category": "Extra",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "bssb",
        "fixed_asset",
    ],
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "views/cb_asset_backend_views.xml",
        "views/res_company_views.xml",
        "views/operating_unit_views.xml",
        "views/cb_asset_batch_views.xml",
        "views/cb_group_views.xml",
    ],
    "demo": [
    ],
    "images": [
    ],
}
