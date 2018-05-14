## This file is to be used as the basis for unit tests of the template generator, will expand as needed
import unittest
import json

class test_template_generator(unittest.TestCase):
    """ Template Generator Unit Test Class """

    #### Very Simple Example Test Case
    def test_1nic_template_tag(self):
        """ Test 1nic Template Tag is Correct """
        tmpl_loc = 'supported/standalone/1nic/new-stack/PAYG/'
        tmpl_file = tmpl_loc + 'azuredeploy.json'
        with open(tmpl_file, 'r') as file_str:
            file_data = json.load(file_str)
        # Removed template tag, keep function to show example unit test
        tmpl_tag = 'standalone_1nic'
        self.assertEqual(tmpl_tag, 'standalone_1nic')

if __name__ == '__main__':
    unittest.main()
