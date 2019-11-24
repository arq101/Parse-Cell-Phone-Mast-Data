from argparse import Namespace
from collections import OrderedDict
import mock
import pytest
import sys

import run_phone_mast_analysis_report as analysis_report


@pytest.fixture()
def sample_csv_file(tmpdir):
    """ Fixture creates a CSV source file with data.

    Returns the csv file path.
    """
    csv_file = tmpdir.mkdir('sub').join('sample_phone_masts.csv')
    # header and 3 rows of test data
    csv_file.write(
        'Property Name,Property Address,Unit Name,Tenant Name,Lease Start Date,Lease End Date,Lease Years,'
        'Current Rent\n'
        'Farmhouse 2,Field X,Unit 2,CellWorks Ltd,29 Apr 2008,28 Apr 2018,10,700\n'
        'Farmhouse 1,Field Y,Unit 1,CellWorks Ltd,29 Apr 2002,28 Apr 2020,15,500\n'
        'Farmhouse 3,Field Z,Unit 3,CellWorks Ltd,01 Dec 2019,01 Dec 2021,15,999.99\n'
        )
    return str(csv_file)


class TestPhoneMastAnalysisReport(object):

    def test_check_file_exists(self, sample_csv_file):
        file_exists = analysis_report.check_file_exists(sample_csv_file)
        assert file_exists is None

    def test_check_file_exists_fails(self, sample_csv_file):
        with pytest.raises(ValueError):
            analysis_report.check_file_exists('./invalid_non_existent_file_foobar.csv')

    def test_read_and_sort_csv_data_by_current_rent(self, sample_csv_file):
        sorted_data = analysis_report.read_and_sort_csv_data_by_current_rent(sample_csv_file)
        assert len(sorted_data) == 3
        assert isinstance(sorted_data[0], OrderedDict)
        assert sorted_data[0]['Current Rent'] == '500'
        assert sorted_data[1]['Current Rent'] == '700'
        assert sorted_data[2]['Current Rent'] == '999.99'

    def test_get_top_n_items_from_list_data(self, sample_csv_file):
        sorted_data = analysis_report.read_and_sort_csv_data_by_current_rent(sample_csv_file)
        result = analysis_report.get_top_n_items_from_list_data(data_set=sorted_data, num_of_items=1)
        expected_outcome = {
            'table': [['Farmhouse 1',  'Unit 1', 'CellWorks Ltd', '500']],
            'headers': ('Property Name', 'Unit Name', 'Tenant Name', 'Current Rent')
        }
        assert result == expected_outcome

    def test_print_tabulated_output(self, capsys):
        expected_input = {
            'table': [['Farmhouse 1', 'Unit 1', 'CellWorks Ltd', '500']],
            'headers': ('Property Name', 'Unit Name', 'Tenant Name', 'Current Rent')
        }
        analysis_report.print_tabulated_output(array_obj=expected_input['table'], headers=expected_input['headers'])
        std_out, _ = capsys.readouterr()        
        expected_output = ('\nProperty Name    Unit Name    Tenant Name      Current Rent\n'
                           '---------------  -----------  -------------  --------------\n'
                           'Farmhouse 1      Unit 1       CellWorks Ltd             500\n\n')
        assert std_out == expected_output

    def test_get_records_that_match_number_of_lease_years(self, sample_csv_file):
        matched_data = analysis_report.get_records_that_match_number_of_lease_years(
            csv_file=sample_csv_file, lease_years=15)
        expected_output = {
            'table': [
                ['Farmhouse 1', 'Field Y', 'Unit 1', 'CellWorks Ltd', '29 Apr 2002', '28 Apr 2020', '15', '500'],
                ['Farmhouse 3', 'Field Z', 'Unit 3', 'CellWorks Ltd', '01 Dec 2019', '01 Dec 2021', '15', '999.99']
            ],
            'headers': ['Property Name', 'Property Address', 'Unit Name', 'Tenant Name', 'Lease Start Date',
                        'Lease End Date', 'Lease Years', 'Current Rent'],
            'total_rent': [(1499.99,)]      # total of: 500 + 999.99
        }
        assert matched_data == expected_output

    def test_get_tenant_name_and_mast_count(self, sample_csv_file):
        tenant_counts = analysis_report.get_tenant_name_and_mast_count(csv_file=sample_csv_file)
        expected_outcome = {
            'table': [('CellWorks Ltd', 3)],
            'headers': ['Tenant Name', 'Number of Masts']
        }
        assert tenant_counts == expected_outcome

    def test_get_rental_data_for_lease_between_start_and_end_dates(self, sample_csv_file):
        date_range = ['2000-01-30', '2010-12-31']
        result = analysis_report.get_rental_data_for_lease_between_start_and_end_dates(
            csv_file=sample_csv_file,
            lease_start_dt_range=date_range)
        expected_outcome = {
            'table': [
                ['Farmhouse 2', 'Unit 2', 'CellWorks Ltd', '29/04/2008', '28/04/2018', '10', '700'],
                ['Farmhouse 1', 'Unit 1', 'CellWorks Ltd', '29/04/2002', '28/04/2020', '15', '500'],
            ],
            'headers': ['Property Name', 'Unit Name', 'Tenant Name', 'Lease Start Date',
                        'Lease End Date', 'Lease Years', 'Current Rent']
        }
        assert result == expected_outcome

    @mock.patch('sys.argv')
    def test_arg_parser_requirement_1(self, mock_sys_argv, sample_csv_file, ):
        sys.argv = ['program.py', sample_csv_file, '-top_rents', '5']
        expected_args = Namespace(
            csv_file=sample_csv_file,
            top_rents=5,
            lease_years=None,
            tenants=False,
            lease_starting_range=None
        )
        args = analysis_report.arg_parser()
        assert args == expected_args

    @mock.patch('sys.argv')
    def test_arg_parser_requirements_all(self, mock_sys_argv, sample_csv_file, ):
        sys.argv = ['program.py', sample_csv_file,
                    '-top_rents', '5',
                    '-lease_years', '25',
                    '-tenants',
                    '-lease_starting_range', '1999-06-01', '2007-08-31'
        ]
        expected_args = Namespace(
            csv_file=sample_csv_file,
            top_rents=5,
            lease_years=25,
            tenants=True,
            lease_starting_range=['1999-06-01', '2007-08-31']
        )
        args = analysis_report.arg_parser()
        assert args == expected_args
