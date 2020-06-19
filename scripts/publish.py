"""
Utilities that help us publish this data to Confluence.
"""
import logging
import os

import click
import jinja2
import yaml
from atlassian import Confluence
from slugify import slugify

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_confluence_connection():
    """
    Make sure the required environment variables are set and return a
    Confluence object, which is used for accessing the Confluence API
    """
    confluence_base_url = _get_env_var('CONFLUENCE_BASE_URL')
    confluence_user_email = _get_env_var('CONFLUENCE_USER_EMAIL')
    confluence_api_token = _get_env_var('CONFLUENCE_API_TOKEN')
    confluence = Confluence(
        confluence_base_url, confluence_user_email, confluence_api_token
    )
    return confluence


def _get_env_var(env_var_name):
    value = os.getenv(env_var_name, None)
    if not value:
        raise NameError(
            'Environment variable {} is not set. This is required to '
            'publish the feature toggle report to Confluence'.format(
                env_var_name
            )
        )
    return value


def publish_to_confluence(confluence, report_path, confluence_space_id,
                          confluence_page_name):
    """
    Publish the HTML report found at `report_path` to confluence space
    `confluence_space_id` and name it `report_name`
    """
    with io.open(report_path, 'r') as report_file:
        feature_toggle_report_html = report_file.read()

    LOGGER.info('Attempting to publish HTML report to Confluence')
    try:
        publish_result = confluence.update_page(
            confluence_space_id, confluence_page_name,
            feature_toggle_report_html
        )
    except TypeError:
        LOGGER.error(
            "Unable to find a space in Confluence with the following "
            "id {}".format(confluence_space_id)
        )
        sys.exit(1)

    if 'statusCode' in publish_result.keys():
        LOGGER.error(
            "Encountered the following error when publishing to Confluence: "
            "{}.".format(publish_result['message'])
        )
        sys.exit(1)

    LOGGER.info('Successfully published HTML report to Confluence')



