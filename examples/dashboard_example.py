# This script demonstrates how to interact with the Dashboard class.
# Assumes config.yaml is in the same folder as this script.
import os
import json
from pysisense import APIClient, Dashboard

# Set the path to your config file
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

# Initialize the API client
api_client = APIClient(config_file=config_path, debug=True)

# --- Initialize the Dashboard class using the shared APIClient ---
dashboard = Dashboard(api_client=api_client)


# --- Example 1: Get all dashbaord ---
response = dashboard.get_all_dashboards()
print(json.dumps(response, indent=4))                                      
dashboard = api_client.to_dataframe(response)
print(dashboard)
api_client.export_to_csv(response, 'all_dashboard.csv')


# --- Example 2: Get dashboard by ID ---
dashboard_id = "65d62c9wregfhg0e33bc64e8"
response = dashboard.get_dashboard_by_id(dashboard_id)
print(json.dumps(response, indent=4))
dashboard = api_client.to_dataframe(response)
print(dashboard)                                                           
api_client.export_to_csv(response, 'dashboard.csv')                         


# --- Example 3: Get dashboard by name ---
dashboard_name = "Sample ECommerce"
response = dashboard.get_dashboard_by_name(dashboard_name)
print(json.dumps(response, indent=4))
dashboard = api_client.to_dataframe(response)
print(dashboard)                                                        


# --- Example 4: Add a Custom Script to a Dashboard ---
dashboard_id = "65d62c9574851800339cf49e"
script = """
dashboard.on('widgetready', function(d) {
    // Set background color for dashboard columns and layout
    $('.dashboard-layout-column').css('background-color', '#f0f0f0');
    $('.dashboard-layout').css('background-color', '#f0f0f0');

    // Remove horizontal dividers between layout cells
    $('.dashboard-layout-cell-horizontal-divider').remove();

    // Style individual dashboard cells
    $('.dashboard-layout-subcell-vertical')
        .css('background-color', 'white')
        .css('box-shadow', '4px 5px 12px #00000078');

    $('.dashboard-layout-subcell-host').css('padding', '10px');

    // Adjust overall dashboard padding
    $('.dashboard-layout')
        .css('padding-right', '20px')
        .css('padding-left', '20px');
});
"""
# Add the script to the dashboard
response = dashboard.add_dashboard_script(dashboard_id, script, executing_user='sisensepy@sisense.com')
print(response)


# --- Example 5: Add widget script ---
dashboard_id = "67dc928ae72ce30033bc6680"
widget_id = "67dc929be72ce30033bc6682"
script = """
widget.on('beforeviewloaded', function(se, ev){


    var legendAlign = 'left',
         verticalAlign= 'top',
        layout =  'horizontal',
        x = 0,
        y = 0
    
    /************************************/

var legend = ev.options.legend;
    legend.align =   legendAlign
    legend.verticalAlign= verticalAlign
    legend.layout= layout
    legend.x=x
    legend.y=y
    
}) 
"""
response = dashboard.add_widget_script(dashboard_id,widget_id, script, executing_user='sisensepy@sisense.com')
print(response)


# # --- Example 6: Add Dashboard Shares ---
dashboard_id = "6823c49365acb80033041c88"
shares = [
    {"name": "john.doe@sisense.com", "type": "user", "rule": "edit"},
    {"name": "viewer@sisense.com", "type": "user", "rule": "view"},
    {"name": "mig_test", "type": "group", "rule": "view"}
]
response = dashboard.add_dashboard_shares(dashboard_id, shares)
print(response)


# # --- Example 7: Get columns from a Dashboard
dashboard_id = "pysense_databricks"
dashboard_columns = dashboard.get_dashboard_columns(dashboard_id)
print(json.dumps(dashboard_columns, indent=4)) 
df = api_client.to_dataframe(dashboard_columns)
print(df)


# # --- Example 8: Get Dashboard Shares ---
dashboard_name = "pysense_databricks"
# Fetch share information
share_info = dashboard.get_dashboard_share(dashboard_name)
print(json.dumps(share_info, indent=4))
# Display results
df = api_client.to_dataframe(share_info)
print(df)