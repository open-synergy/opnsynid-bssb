# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "BSSB",
    "version": "8.0.1.5.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "operating_unit",
        "fixed_asset",
        "fixed_asset_capital_improvement",
        "fixed_asset_complex_asset",
        "fixed_asset_estimation_change",
        "fixed_asset_impairment",
        "fixed_asset_retirement_donation",
        "fixed_asset_retirement_missing",
        "fixed_asset_retirement_sale",
        "fixed_asset_retirement_scrap",
        "fixed_asset_retirement_stolen",
        "stock_move_show_price_unit",
        "stock_rental_operation",
        "stock_donation_operation",
        "stock_stolen_operation",
        "stock_missing_operation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/operating_unit_data.xml",
        "data/stock_warehouse_data.xml",
        "data/account_journal_data.xml",
        # "data/product_category_data.xml",
        "data/account_type_data.xml",
        "data/account_account_data.xml",
        "data/account_asset_category_data.xml",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "menu.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "views/account_asset_asset_views.xml",
        "views/account_asset_improvement_views.xml",
        "views/account_complex_asset_installation_views.xml",
        "views/account_complex_asset_removal_views.xml",
        "views/account_asset_change_estimation_salvage_views.xml",
        "views/account_asset_change_estimation_useful_life_views.xml",
        "views/account_asset_impairment_views.xml",
        "views/account_asset_impairment_reversal_views.xml",
        "views/account_asset_retirement_donation_views.xml",
        "views/account_asset_retirement_missing_views.xml",
        "views/account_asset_retirement_sale_views.xml",
        "views/account_asset_retirement_scrap_views.xml",
        "views/account_asset_retirement_stolen_views.xml",
        "views/stock_quant_views.xml",
        "views/purchase_receipt_views.xml",
        "views/internal_movement_views.xml",
        "views/sale_delivery_views.xml",
        "views/rent_in_views.xml",
        "views/donation_in_views.xml",
        "views/donation_out_views.xml",
        "views/interwarehouse_in_views.xml",
        "views/interwarehouse_out_views.xml",
        "views/stock_quant_ou_perating_unit_change_views.xml",
        "views/sale_delivery_views.xml",
        "views/stolen_views.xml",
        "views/missing_views.xml",
    ],
}
