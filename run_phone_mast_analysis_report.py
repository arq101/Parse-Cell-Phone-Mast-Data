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

    :param csv_file: str    path of csv file
    :return:
    """
    if not os.path.isfile(os.path.abspath(csv_file)):
        logger.error(f'Input file {csv_file} not found!')
        raise ValueError
    return None


def read_and_sort_csv_data_by_current_rent(csv_file, descending=False):
    """Reads the given csv file and returns the data sorted by the 'Current Rent' column

    :param csv_file:    str     path of csv file
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

    :param data_set:        list    array of OrderedDict objects
    :param num_of_items:    int     for the number of items to get from list
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


def print_tabulated_output(array_obj, headers):
    """Produces a tabulated output of the from the given data set

    :param array_obj:   list    each element is a list representing a row of data
    :param headers:     list    array of column headers
    :return:
    """
    print()
    print(tabulate(array_obj, headers=headers))
    print()


def get_records_that_match_number_of_lease_years(csv_file, lease_years):
    """Reads the given csv file and gets the records that matched the given number of lease years.

    :param csv_file:        str     path of csv file
    :param lease_years:     int     number of lease years
    :return:
    """
    with open(csv_file, 'r') as fh:
        csv_reader = csv.DictReader(fh)
        col_headers = csv_reader.fieldnames
        matched_data = list(filter(lambda row: int(row['Lease Years']) == lease_years, csv_reader))

    # get the rows that match number of lease years as a list of lists,
    # (to be used for tabulating results)
    # matched_data has OrderedDict objects
    table_list = [list(row.values()) for row in matched_data]

    # NOTE: the source data was not clear if the rent for each site is monthly/annual or over the lease period,
    # therefore assuming it is over the lease period
    total_rent_of_records = sum([float(row['Current Rent']) for row in matched_data])
    total_rent_of_records = [(total_rent_of_records,)]  # tabulation requires a list of iterable objects

    # for no matches table_list obj is empty
    return {
        'table': table_list,
        'headers': col_headers,
        'total_rent': total_rent_of_records
    }


def arg_parser():
    parser = argparse.ArgumentParser(description='This script produces some analysis on mobile '
                                                 'phone mast data provided as csv input.')
    # positional arg
    parser.add_argument('csv_file', action='store', help='file path of csv')

    # optional args
    parser.add_argument('-r', action='store', dest='top_rents', type=int,
                        help='prints top n number of records of data sorted in ascending order '
                             'by current rent')
    parser.add_argument('-l', action='store', dest='lease_years', type=int,
                        help='prints records that equal the given number of lease years')
    args = parser.parse_args()
    return args


def main():
    logger.info('--starting--')
    cmdline_args = arg_parser()

    check_file_exists(cmdline_args.csv_file)
    if cmdline_args.top_rents:
        sorted_rent_data = read_and_sort_csv_data_by_current_rent(csv_file=cmdline_args.csv_file)
        top_rents = get_top_n_items_from_list_data(data_set=sorted_rent_data,
                                                   num_of_items=cmdline_args.top_rents)
        logger.info(f'Top {cmdline_args.top_rents} mobile phone mast sites in ascending order of current rent ...')
        print_tabulated_output(array_obj=top_rents['table'], headers=top_rents['headers'])

    if cmdline_args.lease_years:
        matched_lease_yrs_data = get_records_that_match_number_of_lease_years(
            csv_file=cmdline_args.csv_file,
            lease_years=cmdline_args.lease_years)
        logger.info(f'Mobile phone masts that have a lease of {cmdline_args.lease_years} years ...')
        print_tabulated_output(array_obj=matched_lease_yrs_data['table'],
                               headers=matched_lease_yrs_data['headers'])
        logger.info(f'Total rent for sites that have a lease of {cmdline_args.lease_years} years ...')
        print_tabulated_output(array_obj=matched_lease_yrs_data['total_rent'], headers=['Total Rent'])

    if not cmdline_args.top_rents and not cmdline_args.lease_years:
        logger.warning('No command line options were selected!')

    logger.info('--end--')


if __name__ == '__main__':
    main()
