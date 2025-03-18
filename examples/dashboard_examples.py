import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pysisense.dashboard import Dashboard
from pysisense.api_client import APIClient

# Create an instance of APIClient
api_client = APIClient()

# Initialize the Dashboard class with the default config file
dashboard = Dashboard(debug=False)


# # --- Example 1: Get all dashbaord ---
# response = dashboard.get_all_dashboards()
# dashboard = api_client.to_dataframe(response)
# print(dashboard) # Print the dataframe
# api_client.export_to_csv(response, 'all_dashboard.csv') # Save the dataframe to a csv file

# # --- Example 2: Get dashboard by ID ---
# dashboard_id = "65d62c9574851800339cf49e"
# response = dashboard.get_dashboard_by_id(dashboard_id)
# dashboard = api_client.to_dataframe(response)
# print(dashboard) # Print the dataframe
# api_client.export_to_csv(response, 'dashboard.csv') # Save the dataframe to a csv file

## --- Example 3: Add Dashboard Script ---
# payload = "{\"script\":\"dashboard.on('widgetready',function(d) {\\n\\n     \\n\\n    //Card view\\n\\n    $('.dashboard-layout-column').css('background-color', '#f0f0f0');\\n\\n    $('.dashboard-layout').css('background-color', '#f0f0f0');\\n\\n    $('.dashboard-layout-cell-horizontal-divider').remove();\\n\\n   \\n\\n    $('.dashboard-layout-subcell-vertical').css('background-color', 'white').css('box-shadow', '4px 5px 12px #00000078')\\n\\n   \\n\\n    $('.dashboard-layout-subcell-host').css('padding', '10');\\n\\n    $('.dashboard-layout').css('padding-right', '20px');\\n\\n    $('.dashboard-layout').css('padding-left', '20px');\\n\\n});\"}"
# print(f'RAW: {payload}')
dashboard_id = "65d62c9574851800339cf49e"

payload = """
dashboard.on('widgetready',function(d) {
    //Card view

    $('.dashboard-layout-column').css('background-color', '#f0f0f0');

    $('.dashboard-layout').css('background-color', '#f0f0f0');

    $('.dashboard-layout-cell-horizontal-divider').remove();

    $('.dashboard-layout-subcell-vertical').css('background-color', 'white').css('box-shadow', '4px 5px 12px #00000078')

    $('.dashboard-layout-subcell-host').css('padding', '10');

    $('.dashboard-layout').css('padding-right', '20px');

    $('.dashboard-layout').css('padding-left', '20px');

});
"""
response = dashboard.add_dashboard_script(dashboard_id, payload, api_username='sisensepy@sisense.com')
print(response) 
