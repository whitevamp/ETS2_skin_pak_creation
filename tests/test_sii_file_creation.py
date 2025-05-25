import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import io

# Functions to be tested
from core.sii_file_creation import create_truck_sii, create_trailer_sii

# Mock config values that will be patched in tests
# These are just placeholders for clarity, the actual mocking happens in decorators
# import core.config # This line is not strictly needed here but shows what we are targeting

class TestSiiFileCreation(unittest.TestCase):

    def setUp(self):
        # Sample data for calling the functions
        self.paint_id = "test_skin"
        self.truck_model = "scania.s_2016"
        self.trailer_model = "scs_box"
        # The path argument will be a dummy for mocked 'open'
        self.dummy_path = Path("dummy/path/to/file.sii")

    # --- Tests for create_truck_sii ---

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', True)
    @patch('core.sii_file_creation.create_metallic_sui', True)
    def test_create_truck_sii_both_true(self, mock_file_open):
        create_truck_sii(self.paint_id, self.dummy_path, self.truck_model)
        
        # Get the written content from the mock
        written_content = mock_file_open().write.call_args[0][0]
        
        self.assertIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertIn(f'@include "{self.paint_id}_mask.sui"', written_content)
        self.assertIn(f'accessory_paint_job_data: {self.paint_id}_0.{self.truck_model}.paint_job', written_content)
        self.assertIn(f'paint_job_mask: "/vehicle/truck/upgrade/paintjob/{self.truck_model}/{self.paint_id}/{self.paint_id}_0.tobj"', written_content)

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', True)
    @patch('core.sii_file_creation.create_metallic_sui', False)
    def test_create_truck_sii_mask_true_metallic_false(self, mock_file_open):
        create_truck_sii(self.paint_id, self.dummy_path, self.truck_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertNotIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertIn(f'@include "{self.paint_id}_mask.sui"', written_content)

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', False)
    @patch('core.sii_file_creation.create_metallic_sui', True)
    def test_create_truck_sii_mask_false_metallic_true(self, mock_file_open):
        create_truck_sii(self.paint_id, self.dummy_path, self.truck_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertNotIn(f'@include "{self.paint_id}_mask.sui"', written_content)

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', False)
    @patch('core.sii_file_creation.create_metallic_sui', False)
    def test_create_truck_sii_both_false(self, mock_file_open):
        create_truck_sii(self.paint_id, self.dummy_path, self.truck_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertNotIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertNotIn(f'@include "{self.paint_id}_mask.sui"', written_content)

    # --- Tests for create_trailer_sii ---

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', True)
    @patch('core.sii_file_creation.create_metallic_sui', True)
    def test_create_trailer_sii_both_true(self, mock_file_open):
        create_trailer_sii(self.paint_id, self.dummy_path, self.trailer_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertIn(f'@include "{self.paint_id}_mask.sui"', written_content)
        self.assertIn(f'accessory_paint_job_data: {self.paint_id}.{self.trailer_model}.paint_job', written_content)
        self.assertIn(f'paint_job_mask: "/vehicle/trailer_owned/upgrade/paintjob/{self.trailer_model}/{self.paint_id}/{self.paint_id}_shared.tobj"', written_content)

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', True)
    @patch('core.sii_file_creation.create_metallic_sui', False)
    def test_create_trailer_sii_mask_true_metallic_false(self, mock_file_open):
        create_trailer_sii(self.paint_id, self.dummy_path, self.trailer_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertNotIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertIn(f'@include "{self.paint_id}_mask.sui"', written_content)

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', False)
    @patch('core.sii_file_creation.create_metallic_sui', True)
    def test_create_trailer_sii_mask_false_metallic_true(self, mock_file_open):
        create_trailer_sii(self.paint_id, self.dummy_path, self.trailer_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertNotIn(f'@include "{self.paint_id}_mask.sui"', written_content)

    @patch('core.sii_file_creation.open', new_callable=mock_open)
    @patch('core.sii_file_creation.create_mask_sui', False)
    @patch('core.sii_file_creation.create_metallic_sui', False)
    def test_create_trailer_sii_both_false(self, mock_file_open):
        create_trailer_sii(self.paint_id, self.dummy_path, self.trailer_model)
        written_content = mock_file_open().write.call_args[0][0]
        self.assertNotIn(f'@include "{self.paint_id}_metallic.sui"', written_content)
        self.assertNotIn(f'@include "{self.paint_id}_mask.sui"', written_content)

if __name__ == '__main__':
    unittest.main()
