# This script demonstrates how to interact with the DataModel class.
# Assumes config.yaml is in the same folder as this script.
import os
import json
from pysisense import DataModel, APIClient

# Set the path to your config file
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

# Initialize the API client
api_client = APIClient(config_file=config_path, debug=True)

# --- Initialize the Dashboard class using the shared APIClient ---
datamodel = DataModel(api_client=api_client)

# --- Example 1: Get DataModel ---
response = datamodel.get_datamodel("pysense_databricks_ec")
print(json.dumps(response, indent=4))


# --- Example 2: Get DataModel Detail ---
response = datamodel.get_all_datamodel()
print(json.dumps(response, indent=4))
df = api_client.to_dataframe(response)
print(df)


# --- Example 2: Get Connection ---
response = datamodel.get_connection("pysense_databricks")
print(json.dumps(response, indent=4))


# --- Example 3: Get Table Schema from DataSource ---
connection_name = "pysense_databricks"
database_name = "samples"
schema_name = "nyctaxi"
table_name = "trips"
response = datamodel.get_table_schema(
    connection_name=connection_name,
    database_name=database_name,
    schema_name=schema_name,
    table_name=table_name
)
print(json.dumps(response, indent=4))
df = api_client.to_dataframe(response)
print(df)

# --- Example 4: Create DataModel ---
# ELASTICUBE DataModel Creation
response = datamodel.create_datamodel("MyDataModel_ec", "extract")
print(json.dumps(response, indent=4))
# LIVE DataModel Creation
response = datamodel.create_datamodel("MyDataModel_live", "live")
print(json.dumps(response, indent=4))


# --- Example 5: Generate Connection Payload ---
# ATHENA(BASIC) Example
datasource_type = "Athena"
connection_params = {
    "name": "athena_basic",
    "description": "this is a description",   # Optional, specify if needed
    "region": "us-east-1",
    "s3_output_location": "s3://pysense-sdk/athena-output/",     
    "aws_access_key": "XYZ1234567890", 
    "aws_secret_key": "XYZ1234567890",   
    "schema": "pysense",                      # Optional, specify if needed
    "additional_parameters": "timeout=60;"    # Optional, specify if needed
}
athena_connection = datamodel.generate_connections_payload(datasource_type, connection_params)
print(json.dumps(athena_connection, indent=4))

# Redshift Example
datasource_type = "RedShift"
connection_params = {
    "name": "pysense_redshift",
    "description": "Redshift connection example",     # Optional, specify if needed
    "server": "examplecluster.abc123xyz789.us-west-2.redshift.amazonaws.com:5439",
    "username": "XYZ@sisense.com",
    "password": "password",  
    "default_database": "dev",                        # Optional, specify if needed
    "additional_parameters": ""                       # Optional, specify if needed
}
redshift_connection = datamodel.generate_connections_payload(datasource_type, connection_params)
print(json.dumps(redshift_connection, indent=4))

# BigQuery Example
datasource_type = "BigQuery"
connection_params = {
    "name": "pysense_bigquery",
    "description": "BigQuery connection example",
    "use_service_account": True,
    "service_account_key_path": "/opt/sisense/storage/gcp/service_account_key.json",
    "use_proxy_server": False,
    "use_dynamic_schema": False,
    "record_field_flattening_level": "2",
    "unnest_arrays": False,
    "allow_large_results": False,
    "use_storage_api": True,
    "additional_parameters": "timeout=60;",
    "database": "fda_food"
}
bigquery_connection = datamodel.generate_connections_payload(datasource_type, connection_params)
print(json.dumps(bigquery_connection, indent=4))

# DataBricks Example
datasource_type = "DataBricks"
connection_params = {
    "name": "pysense_databricks",
    "description": "DataBricks connection example",                      # Optional, specify if needed
    "connection_string": "jdbc:databricks://<server-hostname>:443;httpPath=<http-path>;AuthMech=3;",
    "token": "XYZ1234567890",                             
    "use_dynamic_schema": False,                                         # Optional, specify if needed
    "schema": ""                                                         # Optional, specify if needed
}
databricks_connection = datamodel.generate_connections_payload(datasource_type, connection_params)
print(json.dumps(databricks_connection, indent=4))


# --- Example 6: Create Connection ---
response = datamodel.create_connections(athena_connection)
print(json.dumps(response, indent=4))


# --- Example 7: Create Dataset ---
response = datamodel.create_dataset(
    datamodel_name="MyDataModel_ec",
    connection_name="pysense_bigquery",
    database_name="fda_food",                                             # Data source database name
    schema_name="fda_food",                                               # Data source schema name
    dataset_name=""                                                       # Optional, defaults to schema name
)
print(json.dumps(response, indent=4))


# *** For LIVE DataModel, Only 1 Database is supported and if tables have different schema then provide them explicitly ***
# --- Example 8A: Create Table with Full Configuration ---
datamodel_name = "MyDataModel_ec"
# dataset_id = "945ce5ac-ce68-4a5f-a4e8-577631023add"                     # Optional, will be inferred if not provided
table_name = "housing"
import_query = "SELECT * FROM `fda_food`.`housing` LIMIT 10"              # Optional
description = "Housing table for ML use case"                             # Optional
tags = ["housing", "ML"]                                                  # Optional
build_behavior_config = {                                                 # Required only for 'extract' models
    "mode": "increment",                                                  # Options: "replace", "replace_changes", "append", "increment"
    "column_name": "latitude"                                             # Required if mode is "increment"
}
# schema_name = "fda_food"                                                # If your table's schema is different from the dataset's schema, provide it here
# database_name = "fda_food"                                              # If your table's database is different from the dataset's database, provide it here

response = datamodel.create_table(
    datamodel_name=datamodel_name,
    table_name=table_name,
    # dataset_id=dataset_id,
    import_query=import_query,
    description=description,
    tags=tags,
    build_behavior_config=build_behavior_config
)
print(json.dumps(response, indent=4))

# --- Example 8B: Create Table with Minimal Inputs ---
# Optional parameters like dataset_id, import_query, description, tags, and build_behavior_config will be handled internally
datamodel_name = "MyDataModel_ec"
table_name = "food_enforcement"

response = datamodel.create_table(
    datamodel_name=datamodel_name,
    table_name=table_name
)
print(json.dumps(response, indent=4))


# --- Example 9: Setup DataModel ---
datamodel_name="MyDataModel_live"
datamodel_type="live"                                                       # Options: "extract", "live"
connection_name="pysense_databricks"
dataset_name=""                                                             # Optional, defaults to schema name
database_name="samples"                                                     # Data source database name
schema_name="nyctaxi"                                                       # Data source schema name                  
tables = [
    {   
        "database_name":"samples",                                          # Data source database name
        "schema_name":"nyctaxi",                                            # Data source schema name
        "table_name": "trips",
        "import_query": "SELECT * FROM `nyctaxi`.`trips` LIMIT 10",         # Optional, specify if needed
        "description": "Trips data for FY23",                               # Optional, specify if needed    
        "tags": ["trips", "fact"],                                          # Optional, specify if needed
        "build_behavior_config": {                                          # Required only for "extract" datamodel otherwise leave blank {} or gets ignored in the case of "live"
            "mode": "increment",                                            # Options: "replace", "replace_changes", "append", "increment"
            "column_name": "tpep_pickup_datetime"                           # Required only for "increment" otherwise leave blank ""
        }
    },
    {
        "database_name":"samples",                                          # Data source database name
        "schema_name":"tpch",                                               # Data source schema name
        "table_name": "customer",
        "import_query": "SELECT * FROM `tpch`.`customer` LIMIT 10",         # Optional, specify if needed
        "description": "Customer master data",                              # Optional, specify if needed
        "tags": ["customer", "dimension"],                                  # Optional, specify if needed
        "build_behavior_config": {                                          # Required only for "extract" datamodel otherwise leave blank {} or gets ignored in the case of "live"
            "mode": "replace"                                               # Options: "replace", "replace_changes", "append", "increment"
        }
    }
]

response = datamodel.setup_datamodel(
    datamodel_name=datamodel_name,
    datamodel_type=datamodel_type,
    connection_name=connection_name,
    dataset_name=dataset_name,
    database_name=database_name,                                            # Data source database name
    schema_name=schema_name,                                                # Data source schema name
    tables=tables,
)
print(json.dumps(response, indent=4))


# --- Example 10: Deploy DataModel ---
# ELASTICUBE DATAMODEL DEPLOYMENT
datamodel_name = "MyDataModel_ec2"
response = datamodel.deploy_datamodel(
    datamodel_name=datamodel_name,
    build_type="by_table",                                                    # Other options: "full", "schema_changes"
    row_limit=1000,
    schema_origin="latest"                                                    # Other option: "running"
)
print(json.dumps(response, indent=4))

# LIVE DataModel Deployment
datamodel_name = "MyDataModel_live"
response = datamodel.deploy_datamodel(
    datamodel_name=datamodel_name
    # No need to specify build_type, row_limit, or schema_origin
    # These will be internally set to "publish" and ignored
)
print(json.dumps(response, indent=4))


# --- Example 11: Describe DataModel ---
response = datamodel.describe_datamodel("pysense_databricks_ec")
print(json.dumps(response, indent=4))
df = api_client.to_dataframe(response)
print(df)
datamodel_info = api_client.export_to_csv(response, file_name="datamodel_info.csv")


# --- Example 12: Describe DataModel ---
response = datamodel.describe_datamodel_raw("pysense_databricks_ec")
print(json.dumps(response, indent=4))


# --- Example 13: Get DataModel Shares ---
response = datamodel.get_datamodel_shares("pysense_databricks_ec")
print(json.dumps(response, indent=4))
df = api_client.to_dataframe(response)
print(df)


# --- Example 14A: Get Datasecurity ---
response = datamodel.get_datasecurity("pysense_databricks")
print(json.dumps(response, indent=4))
df = api_client.to_dataframe(response)
print(df)

# --- Example 14B: Get Datasecurity for all DataModels ---
response = datamodel.get_all_datamodel()
all_datamodels = []
for model in response:
    all_datamodels.append(model["title"])

all_ds = []
for datamodel_name in all_datamodels:
    response = datamodel.get_datasecurity(datamodel_name)
    if response:  # Skip empty lists
        all_ds.extend(response) 
# Print the combined list of all datasecurity details
df = api_client.to_dataframe(all_ds)
print(df)
api_client.export_to_csv(all_ds, file_name="datamodel_security.csv")


# --- Example 15: Get Datasecurity Information in Detail ---
response = datamodel.get_datasecurity_detail("pysense_databricks")
df = api_client.to_dataframe(response)
print(df)

response = datamodel.get_all_datamodel()
all_datamodels = []
for model in response:
    all_datamodels.append(model["title"])

all_ds = []
for datamodel_name in all_datamodels:
    response = datamodel.get_datasecurity_detail(datamodel_name)
    if response:  # Skip empty lists
        all_ds.extend(response) 
# Print the combined list of all datasecurity details
df = api_client.to_dataframe(all_ds)
print(df)
api_client.export_to_csv(all_ds, file_name="get_datasecurity_detail.csv")


# # --- Example 16: Get Table and Columns  ---
response = datamodel.get_model_schema("pysense_databricks")
print(json.dumps(response, indent=4))
df = api_client.to_dataframe(response)
print(df)


# --- Example 17: Add Shares  ---
datamodel_name = "pysense_databricks"
shares_to_add = [
    {"name": "autotest@sisense.com", "type": "user", "permission": "EDIT"},
    {"name": "mig_test", "type": "group", "permission": "USE"},
    {"name": "viewer@sisense.com", "type": "user", "permission": "READ"}
]
response = datamodel.add_datamodel_shares(datamodel_name, shares_to_add)
print(json.dumps(response, indent=4))


# --- Example 18: Get Data  ---
datamodel_name = "pysense_databricks"
table_name = "trips"
query = "SELECT count(*) FROM trips"
response = datamodel.get_data(datamodel_name, table_name, query)
print(json.dumps(response, indent=4))

# As DataFrame
df = api_client.to_dataframe(datamodel.get_data("pysense_databricks", "trips"))
print(df)

# As CSV
api_client.export_to_csv(response, file_name=f"{table_name}.csv")


# --- Example 19: Get DataModel Row Count ---
datamodel_name = "pysense_databricks_ec"
response = datamodel.get_row_count(datamodel_name)
print(json.dumps(response, indent=4))
# As DataFrame
df = api_client.to_dataframe(datamodel.get_row_count(datamodel_name))
print(df)
# As CSV
api_client.export_to_csv(response, file_name=f"{datamodel_name}_count.csv")