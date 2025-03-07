from unittest import TestCase
from unittest.mock import Mock, call, patch

from wb_st_challenge import __main__ as main


class MainRunTest(TestCase):
    @patch('wb_st_challenge.__main__.processor')
    @patch('builtins.print')
    def test_calls_to_processor_funcs(self, m_print, m_processor):
        m_processor.process_data.return_value = Mock(
            total=525.114,
            high_cost_full_days=0,
            high_cost_travel_days=1,
            low_cost_full_days=2,
            low_cost_travel_days=3,
        )

        filename = '/some/path/file.csv'

        exit_code = main.run(filename)
        self.assertEqual(exit_code, 0)

        m_processor.get_data_from_csv.assert_called_once_with(filename)
        m_processor.process_data.assert_called_once_with(m_processor.get_data_from_csv.return_value)
        m_print.assert_has_calls(
            [
                call('Total: $525.11'),
                call('High Cost Full Days: 0'),
                call('High Cost Travel Days: 1'),
                call('Low Cost Full Days: 2'),
                call('Low Cost Travel Days: 3'),
            ]
        )


class MainTest(TestCase):
    @patch('wb_st_challenge.__main__.os')
    @patch('wb_st_challenge.__main__.run')
    @patch('builtins.print')
    def test_default_behavior_with_valid_command(self, m_print, m_run, m_os):
        m_os.path.exists.return_value = True
        m_os.path.isfile.return_value = True
        args = [None, 'some_filename.xyz']

        m_print.reset_mock()
        exit_code = main.main(args)
        m_print.assert_not_called()
        self.assertEqual(exit_code, m_run.return_value)

        m_os.path.exists.assert_called_once_with('some_filename.xyz')
        m_os.path.isfile.assert_called_once_with('some_filename.xyz')
        m_run.assert_called_once_with('some_filename.xyz')

    @patch('wb_st_challenge.__main__.os')
    @patch('wb_st_challenge.__main__.run')
    @patch('builtins.print')
    def test_that_a_filename_is_required(self, m_print, m_run, m_os):
        args = [None]
        exit_code = main.main(args)
        m_print.assert_has_calls(
            [
                call('Usage: python -m wb_st_challenge <filename>'),
            ]
        )
        self.assertEqual(exit_code, 1)

        m_run.assert_not_called()
        m_os.path.exists.assert_not_called()
        m_os.path.isfile.assert_not_called()

        m_print.reset_mock()

        with self.subTest('Ensure that excess arguments are not allowed'):
            args = [None, 'filename.xyz', 'something else']
            exit_code = main.main(args)
            m_print.assert_has_calls(
                [
                    call('Usage: python -m wb_st_challenge <filename>'),
                ]
            )
            self.assertEqual(exit_code, 1)
            m_run.assert_not_called()
            m_os.path.exists.assert_not_called()
            m_os.path.isfile.assert_not_called()

    @patch('wb_st_challenge.__main__.os')
    @patch('wb_st_challenge.__main__.run')
    @patch('builtins.print')
    def test_that_filename_exists_and_is_a_file(self, m_print, m_run, m_os):
        with self.subTest('path does not exist'):
            m_os.path.exists.return_value = False
            args = [None, 'some_filename.xyz']

            m_print.reset_mock()
            exit_code = main.main(args)
            self.assertEqual(exit_code, 1)
            m_print.assert_has_calls([call('Error: File \'some_filename.xyz\' does not exist or else is not a file.')])
            m_run.assert_not_called()
            m_os.path.exists.assert_called_once_with('some_filename.xyz')
            m_os.path.isfile.assert_not_called()

        m_print.reset_mock()
        m_os.reset_mock()

        with self.subTest('path exists but is not a file'):
            m_os.path.exists.return_value = True
            m_os.path.isfile.return_value = False
            args = [None, 'some_filename.xyz']

            m_print.reset_mock()
            exit_code = main.main(args)
            self.assertEqual(exit_code, 1)
            m_print.assert_has_calls([call('Error: File \'some_filename.xyz\' does not exist or else is not a file.')])
            m_run.assert_not_called()
            m_os.path.exists.assert_called_once_with('some_filename.xyz')
            m_os.path.isfile.assert_called_once_with('some_filename.xyz')
