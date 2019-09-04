# gather-feature-toggle-state.py

# As part of the Feature Toggle Report Generator utility, this script queries
# a database (i.e. Devstack MySQL container, read-replica) for data on the
# state of feature toggles (i.e. waffle flags) in a set of idas (i.e. edxapp)
# and write it to a JSON file. These are used as inputs to
# https://github.com/edx/edx-toggles/blob/master/scripts/feature_toggle_report_generator.py


from __future__ import print_function

import datetime
import decimal
import io
import json
import os
import re
import shutil

import click
from mysql import connector


def create_db_connection(database):
    """
    Connect to a MySQL database server, and use the database specified by
    `database`.
    """
    username = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    host = os.getenv('DB_HOST', '0.0.0.0')
    port = os.getenv('DB_PORT', '3506')

    db_target = "{}@{}:{}".format(database, host, port)
    print('Attempting to connect to {}'.format(db_target))
    try:
        connection = connector.connect(
            user=username, password=password, host=host,
            database=database, port=port
        )
    except connector.errors.InterfaceError:
        print('Unable to connect to {}'.format(db_target))
        sys.exit(1)
    print('Successfully connected to {}'.format(db_target))
    return connection


def link_headers_to_data(cursor):
    """
    return a list of dictionaries, each one mapping header names to the values
    in a row returned from a query
    """
    header_names = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    tagged_data = []
    for row in rows:
        data = {item[0]: item[1] for item in zip(header_names, row)}
        tagged_data.append(data)
    return tagged_data


def write_file(output_path, app, json_data):
    file_name = "{}_waffle.json".format(app)
    file_path = os.path.join(output_path, file_name)
    print("Writing feature toggle data to: {}".format(file_path))
    with open(file_path, 'w') as output_file:
        json.dump(json_data, output_file)
    print("Finished writing {}".format(file_path))



def format_as_json_dump(data):
    """
    Transform data pulled from the database into JSON data structures
    in the same format as those returned by the Django `dumpdata` command
    """

    boolean_fields = [
        'testing', 'superusers', 'staff', 'authenticated', 'rollout'
    ]
    boolean_or_null_fields = ['everyone', 'percent']

    json_data = []
    for table_name, rows in data.items():
        formatted_table_name = re.sub('_', '.', table_name)

        for row in rows:

            model = {}
            model['model'] = formatted_table_name
            model['pk'] = row['id']

            fields = {}
            for header, value in row.items():
                if header == 'id':
                    continue
                elif isinstance(value, datetime.datetime):
                    value = value.strftime('%Y-%m-%dT%H:%M:%SZ')
                elif isinstance(value, decimal.Decimal):
                    value = float(value)
                elif header in boolean_fields:
                    value = bool(value)
                elif header in boolean_or_null_fields:
                    value = bool(value) if isinstance(value, int) else None
                elif header in ['users', 'groups']:
                    value = value.split(',') if value else []
                fields[header] = value

            model['fields'] = fields

            json_data.append(model)

    return json_data


def build_query(table_name):
    if table_name == 'waffle_flag':
        query = (
            "SELECT waffle_flag.*, "
            "GROUP_CONCAT(DISTINCT(IFNULL(waffle_flag_users.user_id, 'NULL')) SEPARATOR ',') AS users, "
            "GROUP_CONCAT(DISTINCT(IFNULL(waffle_flag_groups.group_id, 'NULL')) SEPARATOR ',') AS groups "
            "FROM waffle_flag "
            "LEFT JOIN waffle_flag_users ON waffle_flag.id=waffle_flag_users.flag_id "
            "LEFT JOIN waffle_flag_groups ON waffle_flag.id=waffle_flag_groups.flag_id "
            "GROUP BY waffle_flag_users.flag_id, waffle_flag_groups.flag_id;"
        )
    else:
        query = "SELECT * FROM {};".format(table_name)
    return query


@click.command()
@click.argument(
    'output_path', default="feature-toggle-data",
)
def main(output_path):
    # as we add support for additional idas (i.e. ecommerce) add them here:
    idas = [
        {
            'app': 'lms',
            'database': 'edxapp',
            'table_names': [
                'waffle_flag', 'waffle_switch', 'waffle_sample'
            ]
        }
    ]

    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    print('Creating output directory at: {}'.format(output_path))
    os.mkdir(output_path)

    for ida in idas:
        print('Gathering feature toggle state data for {}'.format(ida['app']))
        connection = create_db_connection(ida['database'])

        try:
            cursor = connection.cursor(buffered=True)

            feature_toggle_data = {}

            for table in ida['table_names']:
                query = build_query(table)
                cursor.execute(query)
                tagged_data = link_headers_to_data(cursor)

                feature_toggle_data[table] = tagged_data
        except connector.errors.ProgrammingError:
            print('Encountered an error when running {}'.format(query))
            sys.exit(1)
        finally:
            connection.close()

        json_data = format_as_json_dump(feature_toggle_data)
        write_file(output_path, ida['app'], json_data)


if __name__ == "__main__":
    main()
