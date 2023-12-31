import json
import logging
import os
from dataclasses import dataclass
from typing import NamedTuple, Optional
import sys

import asana
import pandas as pd
from asana.rest import ApiException
from asana.models.task_response_data import TaskResponseData

# TODO: create a generic task_delete function that takes the current task and deletes it if the process fails.

fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SingleOrderTask(NamedTuple):
    """A named tuple for a single order task."""

    order_number: str
    order_date: str
    first_name: str
    last_name: str
    email: str
    total_price: str
    company: str
    task_due_date: str


@dataclass
class AsanaHaney:
    workspace_id: str
    access_token: str = os.getenv("ASANA_TOKEN")
    notes_section_gid: str = os.getenv("NOTES_SECTION_GID")

    admin_assignee_section_gid: str = os.getenv("ASSIGNEE_GID")
    admin_order_entry_section_gid: str = os.getenv("ADMIN_ORDER_ENTRY_SECTION_GID")

    task_opt_fields = [
        "actual_time_minutes",
        "approval_status",
        "assignee",
        "assignee.name",
        "assignee_section",
        "assignee_section.name",
        "assignee_status",
        "completed",
        "completed_at",
        "completed_by",
        "completed_by.name",
        "created_at",
        "created_by",
        "custom_fields",
        "custom_fields.asana_created_field",
        "custom_fields.created_by",
        "custom_fields.created_by.name",
        "custom_fields.currency_code",
        "custom_fields.custom_label",
        "custom_fields.custom_label_position",
        "custom_fields.date_value",
        "custom_fields.date_value.date",
        "custom_fields.date_value.date_time",
        "custom_fields.description",
        "custom_fields.display_value",
        "custom_fields.enabled",
        "custom_fields.enum_options",
        "custom_fields.enum_options.color",
        "custom_fields.enum_options.enabled",
        "custom_fields.enum_options.name",
        "custom_fields.enum_value",
        "custom_fields.enum_value.color",
        "custom_fields.enum_value.enabled",
        "custom_fields.enum_value.name",
        "custom_fields.format",
        "custom_fields.has_notifications_enabled",
        "custom_fields.is_formula_field",
        "custom_fields.is_global_to_workspace",
        "custom_fields.is_value_read_only",
        "custom_fields.multi_enum_values",
        "custom_fields.multi_enum_values.color",
        "custom_fields.multi_enum_values.enabled",
        "custom_fields.multi_enum_values.name",
        "custom_fields.name",
        "custom_fields.number_value",
        "custom_fields.people_value",
        "custom_fields.people_value.name",
        "custom_fields.precision",
        "custom_fields.resource_subtype",
        "custom_fields.text_value",
        "custom_fields.type",
        "dependencies",
        "dependents",
        "due_at",
        "due_on",
        "external",
        "external.data",
        "followers",
        "followers.name",
        "hearted",
        "hearts",
        "hearts.user",
        "hearts.user.name",
        "html_notes",
        "is_rendered_as_separator",
        "liked",
        "likes",
        "likes.user",
        "likes.user.name",
        "memberships",
        "memberships.project",
        "memberships.project.name",
        "memberships.section",
        "memberships.section.name",
        "modified_at",
        "name",
        "notes",
        "num_hearts",
        "num_likes",
        "num_subtasks",
        "parent",
        "parent.created_by",
        "parent.name",
        "parent.resource_subtype",
        "permalink_url",
        "projects",
        "projects.name",
        "resource_subtype",
        "start_at",
        "start_on",
        "tags",
        "tags.name",
        "workspace",
        "workspace.name",
    ]  # list[str] | This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include. (optional)

    # post init
    def __post_init__(self):
        configuration = asana.Configuration()
        configuration.access_token = self.access_token

        object.__setattr__(self, "asana_api", asana.ApiClient(configuration))
        object.__setattr__(self, "asana_task_api", asana.TasksApi(self.asana_api))

    def test_asana_api(self):
        configuration = asana.Configuration()
        configuration.access_token = self.access_token

        users_api_instance = asana.UsersApi(asana.ApiClient(configuration))
        user_gid = "me"

        try:
            user_info = users_api_instance.get_user(user_gid)
            logger.info(f"User information: {user_info}")
            logger.info(f"Hello world! my name is {user_info.data.name} !")

        except ApiException as e:
            logger.error("Exception when calling UserApi->get_user_by_id: %s\n" % e)

    def get_date_with_offset(self, offset: int) -> str:
        """gets the current date in the format YYYY-MM-DD"""
        return (pd.Timestamp.now() - pd.DateOffset(days=offset)).strftime("%Y-%m-%d")

    def create_customer_note(
        self,
        project_gid: str,
        task_tuple: SingleOrderTask,
    ) -> None:
        task_name = self.create_customer_task_name(
            first_name=task_tuple.first_name,
            last_name=task_tuple.last_name,
            company_name=task_tuple.company,
            order_name=task_tuple.order_name,
            order_date=task_tuple.order_date,
        )

        task_notes = self.create_customer_task_notes(task_tuple=task_tuple)

        body = asana.TasksBody(
            {
                "workspace": self.workspace_id,
                "projects": project_gid,
                "name": task_name,
                "notes": task_notes,
                "assignee": self.admin_assignee_section_gid,
                "due_on": task_tuple.task_due_date,
            }
        )
        return body

    def create_customer_task_name(
        self,
        first_name: str,
        last_name: str,
        company_name: str,
        order_name: str,
        order_date: str,
    ) -> str:
        """returns a string for the task name in the following format order_name - [first_name last_name] - company_name // order_date"""

        return f"{order_name} - [{first_name} {last_name}] - {company_name} // {order_date}"

    def create_customer_task_notes(self, task_tuple: SingleOrderTask) -> str:
        """returns a string for the task notes in the following format:
        First Name: {first_name}
        Last Name: {last_name}
        Email: {email}
        Total Price: {total_price}
        Order Date: {order_date}
        Company: {company}
        """

        return f"""

        First Name: {task_tuple.first_name}
        Last Name: {task_tuple.last_name}
        Email: {task_tuple.email}
        Total Price: {task_tuple.total_price}
        Order Date: {task_tuple.order_date}
        Company: {task_tuple.company}
        """

    def create_customer_task(
        self,
        body: asana.TasksBody,
        opt_fields: Optional[list[str]] = task_opt_fields,
    ) -> TaskResponseData:
        try:
            api_response = self.asana_task_api.create_task(body, opt_fields=opt_fields)
            logger.info(api_response)
            return api_response
        except ApiException as e:
            logger.error("Exception when calling TasksApi->create_task: %s\n" % e)
            logger.error("Exiting script")
            sys.exit(1)

    def get_new_task_gid(self, task_api_response: TaskResponseData) -> str:
        task_api_response_dict = task_api_response.to_dict()
        return task_api_response_dict["data"]["gid"]

    def move_task_to_section(
        self,
        task_gid: str,
        section_gid: Optional[str] = notes_section_gid,
        insert_after_task: Optional[str] = "1205405874837458",
    ):
        try:
            section_api_client = asana.SectionsApi(self.asana_api)

            body = asana.SectionGidAddTaskBody(
                {"task": task_gid, "insert_after": insert_after_task}
            )  # this is the template.

            api_response = section_api_client.add_task_for_section(
                section_gid, body=body
            )
            logger.info(api_response)
            return api_response
        except ApiException as e:
            logger.error(
                "Exception when calling TasksApi->add_task_for_section: %s\n" % e
            )

    def get_sections_of_project(self, project_gid: str):
        """more of a meta function to see what sections are available for a given project
        can't see this in the actual asana app, but it's available in the api

        Args:
            project_gid (str): _description_
        """
        pass

    def create_abanonded_cart_task(self):
        pass

    def get_max_order_number_and_date(self):
        """gets the current max order number and date and writes it to a table so we know"""
        pass

    def get_section_tasks_since_date(
        self, section_gid: str, date_since: Optional[str] = None
    ) -> list:
        """gets the tasks in a section from a given date

        Args:
            section_gid (str): _description_
        """

        if not date_since:
            date_since = self.get_date_with_offset(7)

        return self.asana_task_api.get_tasks_for_section(
            section_gid=section_gid, completed_since=date_since
        ).data

    def assign_incomplete_task(self, task_id: str):
        task_data = self.asana_task_api.get_task(task_id).to_dict()

        if (
            task_data["data"]["completed"] == False
            and not task_data["data"]["assignee"]
        ):
            body = asana.TasksBody(
                {
                    "assignee": self.admin_assignee_section_gid,
                }
            )

            self.asana_task_api.update_task(body=body, task_gid=task_id)
            logger.info(
                    f"Task {task_id} has been assigned to {self.admin_assignee_section_gid}"
                )

        elif isinstance(task_data["data"]["assignee"], dict):
            if (
                task_data["data"]["assignee"]["gid"] != self.admin_assignee_section_gid
                and task_data["data"]["completed"] == False
            ):
                body = asana.TasksBody(
                    {
                        "assignee": self.admin_assignee_section_gid,
                    }
                )

                self.asana_task_api.update_task(body=body, task_gid=task_id)

                logger.info(
                    f"Task {task_id} has been assigned to {self.admin_assignee_section_gid}"
                )
        else:
            logger.info(f"Task {task_id} has already been assigned or completed")
            logger.info(f"Task data: {task_data['data']['assignee']}")
