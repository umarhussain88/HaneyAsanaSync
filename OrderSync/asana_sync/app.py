import asana
from asana.rest import ApiException
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import sys

load_dotenv()


def test_asana_api():
    configuration = asana.Configuration()
    configuration.access_token = os.getenv("ASANA_TOKEN")

    # Construct resource API Instance
    users_api_instance = asana.UsersApi(asana.ApiClient(configuration))
    user_gid = "me"

    try:
        # Get your user info
        user_info = users_api_instance.get_user(user_gid)

        # Print out your information
        print(f"User information: {user_info}")

        print(f"Hello world! my name is {user_info.data.name} !")

    except ApiException as e:
        print("Exception when calling UserApi->get_user_by_id: %s\n" % e)
        

def create_asana_client() -> asana.ApiClient:
    """Creates an Asana API client."""
    configuration = asana.Configuration()
    configuration.access_token = os.getenv("ASANA_TOKEN")
    return asana.ApiClient(configuration)


def create_psql_engine():
    """Creates a SQLAlchemy engine for the Postgres database."""
    return create_engine(
        f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}'
        f'@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
    )


def get_latest_single_order_customers(engine):
    df = pd.read_sql("SELECT * FROM dm_shopify.single_customer_orders", con=engine)
    return df.head(2)


# def create_customer_note_iterator(data_frame : pd.DataFrame) -> pd.core.series.Series:
#     for _, row in data_frame.iterrows():
#         #schema - first_name, last_name, email, total_price, order_date, company 
#         return row
    
def create_customer_note(asana_api : asana.ApiClient, project_gid : str, task_series : pd.core.series.Series) -> None:
    test_project_gid = '1205355682434550'
    
    asana_task_api = asana.TasksApi(asana_api)
    
    opt_fields = ["actual_time_minutes","approval_status","assignee","assignee.name","assignee_section","assignee_section.name","assignee_status","completed","completed_at","completed_by","completed_by.name","created_at","created_by","custom_fields","custom_fields.asana_created_field","custom_fields.created_by","custom_fields.created_by.name","custom_fields.currency_code","custom_fields.custom_label","custom_fields.custom_label_position","custom_fields.date_value","custom_fields.date_value.date","custom_fields.date_value.date_time","custom_fields.description","custom_fields.display_value","custom_fields.enabled","custom_fields.enum_options","custom_fields.enum_options.color","custom_fields.enum_options.enabled","custom_fields.enum_options.name","custom_fields.enum_value","custom_fields.enum_value.color","custom_fields.enum_value.enabled","custom_fields.enum_value.name","custom_fields.format","custom_fields.has_notifications_enabled","custom_fields.is_formula_field","custom_fields.is_global_to_workspace","custom_fields.is_value_read_only","custom_fields.multi_enum_values","custom_fields.multi_enum_values.color","custom_fields.multi_enum_values.enabled","custom_fields.multi_enum_values.name","custom_fields.name","custom_fields.number_value","custom_fields.people_value","custom_fields.people_value.name","custom_fields.precision","custom_fields.resource_subtype","custom_fields.text_value","custom_fields.type","dependencies","dependents","due_at","due_on","external","external.data","followers","followers.name","hearted","hearts","hearts.user","hearts.user.name","html_notes","is_rendered_as_separator","liked","likes","likes.user","likes.user.name","memberships","memberships.project","memberships.project.name","memberships.section","memberships.section.name","modified_at","name","notes","num_hearts","num_likes","num_subtasks","parent","parent.created_by","parent.name","parent.resource_subtype","permalink_url","projects","projects.name","resource_subtype","start_at","start_on","tags","tags.name","workspace","workspace.name"] # list[str] | This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include. (optional)
    body = asana.TasksBody({"workspace" : '15984642679817', "projects" : project_gid, "name" : "Create note", "notes" : task_series.to_markdown()})

    try:
        api_response = asana_task_api.create_task(body, opt_fields=opt_fields)
        print(api_response)
    except ApiException as e:
        print("Exception when calling TasksApi->create_task: %s\n" % e)


# # Configure OAuth2 access token for authorization: oauth2
# configuration = asana.Configuration()
# configuration.access_token = '<YOUR_PERSONAL_ACCESS_TOKEN>'
# api_client = asana.ApiClient(configuration)

# # create an instance of the API class
# api_instance = asana.TasksApi(api_client)
# body = asana.TasksBody({"param1": "value1", "param2": "value2",}) # TasksBody | The task to create.
# opt_fields = ["actual_time_minutes","approval_status","assignee","assignee.name","assignee_section","assignee_section.name","assignee_status","completed","completed_at","completed_by","completed_by.name","created_at","created_by","custom_fields","custom_fields.asana_created_field","custom_fields.created_by","custom_fields.created_by.name","custom_fields.currency_code","custom_fields.custom_label","custom_fields.custom_label_position","custom_fields.date_value","custom_fields.date_value.date","custom_fields.date_value.date_time","custom_fields.description","custom_fields.display_value","custom_fields.enabled","custom_fields.enum_options","custom_fields.enum_options.color","custom_fields.enum_options.enabled","custom_fields.enum_options.name","custom_fields.enum_value","custom_fields.enum_value.color","custom_fields.enum_value.enabled","custom_fields.enum_value.name","custom_fields.format","custom_fields.has_notifications_enabled","custom_fields.is_formula_field","custom_fields.is_global_to_workspace","custom_fields.is_value_read_only","custom_fields.multi_enum_values","custom_fields.multi_enum_values.color","custom_fields.multi_enum_values.enabled","custom_fields.multi_enum_values.name","custom_fields.name","custom_fields.number_value","custom_fields.people_value","custom_fields.people_value.name","custom_fields.precision","custom_fields.resource_subtype","custom_fields.text_value","custom_fields.type","dependencies","dependents","due_at","due_on","external","external.data","followers","followers.name","hearted","hearts","hearts.user","hearts.user.name","html_notes","is_rendered_as_separator","liked","likes","likes.user","likes.user.name","memberships","memberships.project","memberships.project.name","memberships.section","memberships.section.name","modified_at","name","notes","num_hearts","num_likes","num_subtasks","parent","parent.created_by","parent.name","parent.resource_subtype","permalink_url","projects","projects.name","resource_subtype","start_at","start_on","tags","tags.name","workspace","workspace.name"] # list[str] | This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include. (optional)

# try:
#     # Create a task
#     api_response = api_instance.create_task(body, opt_fields=opt_fields)
#     pprint(api_response)
# except ApiException as e:
#     print("Exception when calling TasksApi->create_task: %s\n" % e)

if __name__ == "__main__":
    test_asana_api()
    
    
    engine = create_psql_engine()
    df = get_latest_single_order_customers(engine)
    
    asana_api = create_asana_client()
    
    for _, row in df.iterrows():
        create_customer_note(asana_api=asana_api,project_gid='1205355682434550', task_series=row)
    
    
    
