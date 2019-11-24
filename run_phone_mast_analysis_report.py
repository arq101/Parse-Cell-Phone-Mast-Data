#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import logging
import os
from tabulate import tabulate


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s -- %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def check_file_exists(csv_file):
    """Throws exception if the given file path does not exist.

    :param csv_file: str
    :return:
    """
    if not os.path.isfile(os.path.abspath(csv_file)):
        logger.error(f'Input file {csv_file} not found!')
        raise ValueError
    return None


def read_and_sort_csv_data_by_current_rent(csv_file, descending=False):
    """Reads the given csv file and returns the data sorted by the 'Current Rent' column

    :param csv_file:    str
    :param descending:  bool
    :return: list of dicts
    """
    with open(csv_file, 'r') as fh:
        logger.info(f'Reading data from {csv_file} ...')
        csv_reader = csv.DictReader(fh)
        sorted_data = sorted(csv_reader, key=lambda row: float(row['Current Rent']), reverse=descending)
    return sorted_data


def get_top_n_items_from_list_data(data_set, num_of_items):
    """Gets the first n number of elements from a list

    :param data_set:        list of dicts
    :param num_of_items:    int
    :return: dict
    """
    top_dataset = data_set[:num_of_items]
    # creating a list of lists in order to tabulate this data ...
    table_list = [[row['Property Name'], row['Unit Name'], row['Tenant Name'], row['Current Rent']] for row in
                  top_dataset]
    return {
        'table': table_list,
        'headers': ('Property Name', 'Unit Name', 'Tenant Name', 'Current Rent')
    }


def print_tabulated_output(list_obj, headers):
    """Produces a tabulated output of the from the given data set

    :param list_obj:    list of lists, where each sublist represent a row of data
    :param headers:     list of column headers
    :return:
    """
    print(tabulate(list_obj, headers=headers))


def arg_parser():
    parser = argparse.ArgumentParser(description='This script produces some analysis on mobile '
                                                 'phone mast data provided as csv input.')
    # positional arg
    parser.add_argument('csv_file', action='store', help='file path of csv')

    # optional arg
    parser.add_argument('-r', action='store', dest='top_rents', type=int,
                        help='prints top n number of records of data sorted in ascending order '
                             'by current rent')
    args = parser.parse_args()
    return args


def main():
    cmdline_args = arg_parser()
    print('\n')

    check_file_exists(cmdline_args.csv_file)
    if cmdline_args.top_rents:
        sorted_rent_data = read_and_sort_csv_data_by_current_rent(cmdline_args.csv_file)
        top_rents = get_top_n_items_from_list_data(data_set=sorted_rent_data, num_of_items=cmdline_args.top_rents)
        print(f'\n>> Top {cmdline_args.top_rents} mobile phone mast sites in ascending order of current rent ...\n')
        print_tabulated_output(list_obj=top_rents['table'], headers=top_rents['headers'])

    print('\n')
    logger.info('--end--')


if __name__ == '__main__':
    main()
