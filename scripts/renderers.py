"""
    Creates classes that render toggles data into either html or csv
"""
import datetime
import io
import os
import csv
import logging
from collections import OrderedDict

import click
import jinja2


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CsvRenderer():
    """
    Used to output toggles+annotations data as CSS
    """

    def __init__(self):
        pass

    def render_flag_csv_report(self, idas):
        flag_toggles = []
        header = set()
        for ida_name, ida in idas.items():
            for flag_toggle in ida.toggles['WaffleFlag']:
                data_dict = flag_toggle.full_data()
                header = header.union(set(data_dict.keys()))
                flag_toggles.append(data_dict)
        self.write_csv("test_flag.csv", flag_toggles, header)

    def render_switch_csv_report(self, idas):
        switch_toggles = []
        header = set()
        for ida_name, ida in idas.items():
            for switch_toggle in ida.toggles['WaffleSwitch']:
                data_dict = switch_toggle.full_data()
                header = header.union(set(data_dict.keys()))
                switch_toggles.append(data_dict)
        self.write_csv("test_switch.csv", switch_toggles, header)


    def write_csv(self, file_name, data, fieldnames):
        """
        writes data_dict in file with name file_name
        """
        with open(file_name, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for datum in data:
                writer.writerow(datum)


class HtmlRenderer():

    def __init__(self, template_dir, report_dir):
        self.jinja_environment = jinja2.Environment(
            autoescape=False,
            loader=jinja2.FileSystemLoader('templates'),
            lstrip_blocks=True,
            trim_blocks=True
        )
        self.report_dir = report_dir
        if not os.path.isdir(report_dir):
            os.mkdir(report_dir)

    def render_file(self, output_file_name, template_name, variables={}):
        file_path = os.path.join(self.report_dir, output_file_name)
        template = self.jinja_environment.get_template(template_name)
        with io.open(file_path, 'w') as output:
            output.write(
                template.render(**variables)
            )

    def render_html_report(self, idas, environment_name, show_state=True):
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        report_path = 'feature_toggle_report.html'
        LOGGER.info('Attempting to render HTML report')
        self.render_file(
            report_path, 'report.tpl',
            variables={
                'idas': idas, 'environment': environment_name,
                'report_date': report_date,
                'show_state': show_state,

            }
        )
        LOGGER.info(
            'Succesfully rendered HTML report to {}'.format(report_path)
        )
