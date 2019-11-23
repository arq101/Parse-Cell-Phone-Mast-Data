#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s -- %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def read_input_csv_file():
    pass


def sort_data_by_current_rent(ascending=True):
    pass


def get_top_n_items_from_list_data(num_of_items):
    pass


def arg_parser():
    parser = argparse.ArgumentParser(description='This script produces some analysis on mobile '
                                                 'phone mast data provided as csv input.')
    # positional arg
    parser.add_argument('csvfile', action='store', help='file path of csv')

    # optional arg
    parser.add_argument('-r', '--rent', action='store', default=5, type=int,
                        help='prints top n number of records of data sorted in ascending order '
                             'by current rent')
    args = parser.parse_args()
    return args


def main():
    cmdline_args = arg_parser()


if __name__ == '__main__':
    main()
