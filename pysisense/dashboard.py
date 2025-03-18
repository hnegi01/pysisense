"""
1. Add widget Dashboard Script
2. Add widget Script
3. Update Dashboard Script
4. Update Widget Script
5. Replace Dashboard Script by matching string from existing script
6. Replace Widget Script by matching string from existing script
7. Add users to share
8. Republish Dashboard
9. Export Dashboard
10. Export Widget
11. Change Dashboard Owner
12. Export widget/dashboard as csv
13. Get all dashboards
14. Get all tables AND columns used in dashboard
"""

from pysisense.api_client import APIClient
from pysisense.access_management import AccessManagement
import json


class Dashboard:
    def __init__(self, api_client=None, config_file="config.yaml", debug=False):
        """
        Initializes the Dashboard class.

        If no API client is provided, it will create an APIClient internally using the provided config file.

        Parameters:
            api_client (APIClient, optional): An existing APIClient instance. If None, a new APIClient is created.
            config_file (str): Path to the YAML configuration file. Default is 'config.yaml'.
            debug (bool, optional): Enables debug logging if True. Default is False.
        """
        # If an API client is provided, use it. Otherwise, initialize a new APIClient with the config file.
        if api_client:
            self.api_client = api_client
        else:
            self.api_client = APIClient(config_file=config_file, debug=debug)

        # Initialize AccessManagement using the source client
        self.access_mgmt = AccessManagement(self.api_client, debug=debug)
        
        # Use the logger from the APIClient instance
        self.logger = self.api_client.logger

    def get_all_dashboards(self):
        """
        Retrieves all dashboards from the Sisense server.

        Parameters: None

        Returns: 
            List : A list of dictionaries containing information about each dashboard.
        """
        # Construct the endpoint URL for retrieving all dashboards
        endpoint = "/api/v1/dashboards/admin?dashboardType=owner"
        # Send a GET request to the endpoint
        response = self.api_client.get(endpoint)
        self.logger.debug(f"Response: {len(response.json())} dashboards found.")
        # Return the JSON response
        return response.json()
    
    def get_dashboard_by_id(self, dashboard_id):
        """
        Retrieves a specific dashboard by its ID.

        Parameters:
            dashboard_id (str): The ID of the dashboard to retrieve.

        Returns:
            List : A list of dictionaries containing information about the dashboard with the specified ID.
        """
        # Construct the endpoint URL for retrieving a specific dashboard by ID
        endpoint = f"/api/v1/dashboards/admin?dashboardType=owner&id={dashboard_id}"
        # Send a GET request to the endpoint
        response = self.api_client.get(endpoint)
        self.logger.debug(f"Response: Dashboard with ID {dashboard_id} found.")
        # Return the JSON response
        return response.json()


    def add_dashboard_script(self, dashboard_id, script, api_username=None):
        """
        Adds a script to a dashboard, temporarily changing ownership if required.

        Parameters:
            dashboard_id (str): The ID of the dashboard where the script will be added.
            script (str): The JavaScript script as either:
                        - A properly formatted JSON string.
                        - A raw Python docstring (multi-line string).
            api_username (str, optional): The username of the API user. This is used to temporarily change 
                                        the owner of the dashboard, as only the owner can add scripts. 
                                        If not provided, assumes the dashboard owner is the same as the API user.

        Returns:
            str: Success message or error details.
        """
        
        add_script_endpoint = f"/api/dashboards/{dashboard_id}"

        # If api_username is provided, temporarily change dashboard ownership
        if api_username:
            self.logger.debug(f"API username '{api_username}' provided. Fetching original owner of dashboard {dashboard_id}.")
            
            dashboard_response = self.api_client.get(f"/api/v1/dashboards/admin?dashboardType=owner&id={dashboard_id}&asObject=false")
            if dashboard_response is None or dashboard_response.status_code != 200:
                self.logger.error(f"Dashboard with ID '{dashboard_id}' not found or failed to retrieve.")
                return f"Error: Dashboard '{dashboard_id}' not found."

            dashboard_data = dashboard_response.json()
            original_owner_id = dashboard_data[0].get("owner")
            
            # Fetch existing dashboard shares before changing ownership
            self.logger.debug(f"Retrieving existing shares of dashboard {dashboard_id} to restore later.")
            shares_response = self.api_client.get(f"/api/shares/dashboard/{dashboard_id}?adminAccess=true")
            
            if shares_response is None or shares_response.status_code != 200:
                error_message = shares_response.json() if shares_response else "No response received."
                self.logger.error(f"Failed to retrieve shares for dashboard {dashboard_id}. Error: {error_message}")
                return f"Error: Failed to retrieve shares for dashboard {dashboard_id}."

            shares = shares_response.json().get("sharesTo", [])

            # Change ownership to api_username
            self.logger.info(f"Changing ownership of dashboard {dashboard_id} to '{api_username}'.")
            api_user = self.access_mgmt.get_user(api_username)
            api_user_id = api_user.get("USER_ID")

            if not api_user_id:
                self.logger.error(f"User '{api_username}' not found.")
                return f"Error: User '{api_username}' not found."

            ownership_response = self.api_client.post(
                f"/api/v1/dashboards/{dashboard_id}/change_owner?adminAccess=true",
                data={"ownerId": api_user_id, "originalOwnerRule": "edit"}
            )

            if ownership_response is None or ownership_response.status_code != 200:
                error_message = ownership_response.json() if ownership_response else "No response received."
                self.logger.error(f"Failed to change ownership of dashboard {dashboard_id}. Error: {error_message}")
                return f"Error: Failed to change ownership of dashboard {dashboard_id}."

            self.logger.info(f"Ownership of dashboard {dashboard_id} successfully changed to '{api_username}'.")
        else:
            self.logger.debug(f"No API username provided. Assuming the dashboard owner is the same as the API user.")

        # Convert script to JSON format if needed
        try:
            if isinstance(script, str) and not script.startswith("{"):
                self.logger.debug("Script received as a Python docstring. Converting to JSON format.")
                script = json.dumps({"script": script}, ensure_ascii=False)

            script_dict = json.loads(script) if isinstance(script, str) else script
            self.logger.debug(f"Final script payload prepared: {script_dict}")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format for script.")
            return "Error: Script must be a valid JSON string."

        # Add script to the dashboard
        script_response = self.api_client.put(add_script_endpoint, data=script_dict)

        if script_response is None or script_response.status_code != 200:
            error_message = script_response.json() if script_response else "No response received."
            self.logger.error(f"Failed to add script to dashboard {dashboard_id}. Error: {error_message}")
            return f"Error: Failed to add script to dashboard {dashboard_id}."

        self.logger.info(f"Script successfully added to dashboard {dashboard_id}.")

        # Restore original ownership if changed
        if api_username:
            self.logger.info(f"Restoring original ownership of dashboard {dashboard_id} to '{original_owner_id}'.")
            
            shares_payload = [{"shareId": s["shareId"], "type": s["type"], "rule": s.get("rule", "edit"), "subscribe": s.get("subscribe", False)} for s in shares]
            
            restore_shares_response = self.api_client.post(
                f"/api/shares/dashboard/{dashboard_id}", 
                data={"sharesTo": shares_payload}
            )

            if restore_shares_response is None or restore_shares_response.status_code != 200:
                error_message = restore_shares_response.json() if restore_shares_response else "No response received."
                self.logger.error(f"Failed to restore shares for dashboard {dashboard_id}. Error: {error_message}")
                return f"Error: Failed to restore shares for dashboard {dashboard_id}."

            ownership_restore_response = self.api_client.post(
                f"/api/v1/dashboards/{dashboard_id}/change_owner",
                data={"ownerId": original_owner_id, "originalOwnerRule": "edit"}
            )

            if ownership_restore_response is None or ownership_restore_response.status_code != 200:
                error_message = ownership_restore_response.json() if ownership_restore_response else "No response received."
                self.logger.error(f"Failed to revert ownership of dashboard {dashboard_id} to original owner. Error: {error_message}")
                return f"Error: Failed to revert ownership of dashboard {dashboard_id}."

            self.logger.info(f"Ownership of dashboard {dashboard_id} successfully restored to original owner.")

        return "Script added successfully."


    def add_dashboard_shares(self, dashboard_id, users=None,groups=None):
        """
        Adds shares to a dashboard.

        Parameters:
            dashboard_id (str): The ID of the dashboard to which the shares will be added.
            users (list, optional): A list of usernames to share the dashboard with.
            groups (list, optional): A list of group names to share the dashboard with.

        Returns:
            str: Success message or error details.
        """
        endpoint = f"/api/dashboards/{dashboard_id}/shares"
        
        # Get user and group IDs from usernames and group names
        if users:
            for user in users:
                user_id = self.access_mgmt.get_user_id_by_username(user)
                if user_id is None:
                    self.logger.error(f"User '{user}' not found.")
                    return f"Error: User '{user}' not found."
                user = user_id

        # Create a payload dictionary
        payload = {}

        # Add users and groups to the payload if they are provided
        if users:
            payload["users"] = users
        if groups:
            payload["groups"] = groups

        try:
            # Send a POST request to add shares
            response = self.api_client.post(endpoint, json=payload)

            if response is None:
                self.logger.error(f"POST request to {endpoint} failed: No response received.")
                return "Error: No response from API"

            if response.status_code == 200:
                self.logger.info(f"Shares successfully added to dashboard {dashboard_id}.")
                return "Shares added successfully"
            else:
                try:
                    error_message = response.json()
                except ValueError:
                    error_message = response.text  

                self.logger.error(f"Failed to add shares to dashboard {dashboard_id}. Error: {error_message}")
                return f"Error: {error_message}"

        except Exception as e:
            self.logger.exception(f"Exception while adding shares to dashboard {dashboard_id}: {e}")
            return f"Exception: {str(e)}"