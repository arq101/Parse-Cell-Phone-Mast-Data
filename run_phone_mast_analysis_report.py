#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import arrow
import csv
from collections import Counter
from datetime import datetime
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


def get_tenant_name_and_mast_count(csv_file):
    with open(csv_file, 'r') as fh:
        csv_reader = csv.DictReader(fh)

        # NOTE: assuming tenant names are to be taken literally as given in the source data,
        # (some tenant names have the same name, but difference in upper/lower case and missing spaces)
        tenant_names = [row['Tenant Name'] for row in csv_reader]

    tenant_name_counts = Counter(tenant_names)
    return {
        'table': [(tenant, count) for tenant, count in tenant_name_counts.items()],
        'headers': ['Tenant Name', 'Number of Masts']
    }


def get_rental_data_for_lease_between_start_and_end_dates(csv_file, lease_start_dt_range):
    with open(csv_file, 'r') as fh:
        csv_reader = csv.DictReader(fh)
        col_headers = csv_reader.fieldnames
        rental_data = list(csv_reader)

    try:
        lease_start_date_1 = arrow.get(lease_start_dt_range[0], 'YYYY-MM-DD')
        lease_start_date_2 = arrow.get(lease_start_dt_range[1], 'YYYY-MM-DD')
    except ValueError as err:
        logger.error(str(err))
        raise

    # convert string dates to Python arrow datetime objects in order to do date comparisons
    for item in rental_data:
        item['Lease Start Date'] = arrow.get(item['Lease Start Date'], 'DD MMM YYYY')
        item['Lease End Date'] = arrow.get(item['Lease End Date'], 'DD MMM YYYY')

    filter_data = list(filter(
        lambda row: (row['Lease Start Date'] >= lease_start_date_1 and row['Lease Start Date'] <= lease_start_date_2),
        rental_data))

    for item in filter_data:
        item['Lease Start Date'] = item['Lease Start Date'].format('DD/MM/YYYY')
        item['Lease End Date'] = item['Lease End Date'].format('DD/MM/YYYY')

    # creating a list of lists in order to tabulate this data ...
    table_list = [
        [row['Property Name'], row['Unit Name'], row['Tenant Name'], row['Lease Start Date'], row['Lease End Date'],
         row['Lease Years'], row['Current Rent']] for row in filter_data
    ]
    return {
        'table': table_list,
        'headers': ['Property Name', 'Unit Name', 'Tenant Name', 'Lease Start Date',  'Lease End Date',
                    'Lease Years', 'Current Rent']
    }


def arg_parser():
    parser = argparse.ArgumentParser(description='This script produces some analysis on mobile '
                                                 'phone mast data provided as csv input.')
    # positional arg
    parser.add_argument('csv_file', action='store', help='file path of csv')

    # optional args
    parser.add_argument('-top_rents', action='store', dest='top_rents', type=int,
                        help='prints top n number of records of data sorted in ascending order '
                             'by current rent')
    parser.add_argument('-lease_years', action='store', dest='lease_years', type=int,
                        help='prints records that equal the given number of lease years')
    parser.add_argument('-tenants', action='store_true', dest='tenants', default=False,
                        help='prints tenants and associated number of masts')
    parser.add_argument('-lease_starting_range', action='store', dest='lease_starting_range', nargs=2,
                        help='Prints rental data for lease starting and ending between given dates, '
                             'date format: yyyy-mm-dd')

    args = parser.parse_args()
    return args


def main():
    logger.info('--starting--')
    cmdline_args = arg_parser()

    check_file_exists(cmdline_args.csv_file)
    # process top rents
    if cmdline_args.top_rents:
        sorted_rent_data = read_and_sort_csv_data_by_current_rent(csv_file=cmdline_args.csv_file)
        top_rents = get_top_n_items_from_list_data(data_set=sorted_rent_data,
                                                   num_of_items=cmdline_args.top_rents)
        logger.info(f'Top {cmdline_args.top_rents} mobile phone mast sites in ascending order of current rent ...')
        print_tabulated_output(array_obj=top_rents['table'], headers=top_rents['headers'])

    # process rentals matching number of lease years
    if cmdline_args.lease_years:
        matched_lease_yrs_data = get_records_that_match_number_of_lease_years(
            csv_file=cmdline_args.csv_file,
            lease_years=cmdline_args.lease_years)
        logger.info(f'Mobile phone masts that have a lease of {cmdline_args.lease_years} years ...')
        print_tabulated_output(array_obj=matched_lease_yrs_data['table'],
                               headers=matched_lease_yrs_data['headers'])
        logger.info(f'Total rent for sites that have a lease of {cmdline_args.lease_years} years ...')
        print_tabulated_output(array_obj=matched_lease_yrs_data['total_rent'], headers=['Total Rent'])

    # process tenants and associated number of sites
    if cmdline_args.tenants:
        logger.info('Tenants and the number of masts associated to them ...')
        tenants_and_mast_count = get_tenant_name_and_mast_count(csv_file=cmdline_args.csv_file)
        print_tabulated_output(array_obj=tenants_and_mast_count['table'], headers=tenants_and_mast_count['headers'])

    # process rentals with leases starting between given dates
    if cmdline_args.lease_starting_range:
        logger.info(f'Rentals with a lease start date between {cmdline_args.lease_starting_range[0]} '
                    f'and {cmdline_args.lease_starting_range[1]} ...')
        leaseing_between_data = get_rental_data_for_lease_between_start_and_end_dates(
            csv_file=cmdline_args.csv_file,
            lease_start_dt_range=cmdline_args.lease_starting_range)
        print_tabulated_output(array_obj=leaseing_between_data['table'], headers=leaseing_between_data['headers'])

    # TODO this could done more cleanly with more time
    if not cmdline_args.top_rents and not cmdline_args.lease_years and not cmdline_args.tenants and \
            not cmdline_args.lease_starting_range:
        logger.warning('No command line options were selected!')

    logger.info('--end--')


if __name__ == '__main__':
    main()
