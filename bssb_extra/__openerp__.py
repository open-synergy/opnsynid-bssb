# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "BSBB Extra",
    "version": "8.0.1.0.0",
    "category": "Extra",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "bssb",
        "opnsynid_stock_balance_aeroo_report",
        "opnsynid_stock_card_aeroo_report",
    ],
    "data": [
        "menu.xml",
        "data/base_sequence_configurator_data.xml",
        "views/account_asset_asset_views.xml",
        "views/account_asset_asset_qr_views.xml",
        "reports/laporan_depresiasi_bulanan.xml",
        "reports/stock_balance_reports.xml",
        "reports/stock_card_reports.xml",
    ],
    "demo": [
    ],
    "images": [
    ],
}
