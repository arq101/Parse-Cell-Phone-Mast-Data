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
        'Farmhouse 2,Field X,Unit 2,CellWorks Ltd,29 Apr 2008,28 Apr 2018,10,700,\n'
        'Farmhouse 1,Field Y,Unit 1,CellWorks Ltd,29 Apr 2002,28 Apr 2020,18,500,\n'
        'Farmhouse 3,Field Z,Unit 3,CellWorks Ltd,01 Dec 2019,01 Dec 2021,2,999.99,\n'
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
        assert expected_outcome == result

    def test_print_tabulated_output(self, capsys):
        expected_input = {
            'table': [['Farmhouse 1', 'Unit 1', 'CellWorks Ltd', '500']],
            'headers': ('Property Name', 'Unit Name', 'Tenant Name', 'Current Rent')
        }
        analysis_report.print_tabulated_output(list_obj=expected_input['table'], headers=expected_input['headers'])
        std_out, _ = capsys.readouterr()
        assert std_out == ('Property Name    Unit Name    Tenant Name      Current Rent\n'
                           '---------------  -----------  -------------  --------------\n'
                           'Farmhouse 1      Unit 1       CellWorks Ltd             500\n')

    @mock.patch('sys.argv')
    def test_arg_parser(self, m_sys_argv, sample_csv_file, ):
        sys.argv = ['program.py', sample_csv_file, '-r', '5']

        expected_args = Namespace(csv_file=sample_csv_file, top_rents=5)
        args = analysis_report.arg_parser()
        assert args == expected_args
