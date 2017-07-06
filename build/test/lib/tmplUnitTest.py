## This file is to be used as the basis for unit tests of the template generator, will expand as needed
import unittest
import json

class test_template_generator(unittest.TestCase):
    """ Template Generator Unit Test Class """

    #### Very Simple Example Test Case
    def test_1nic_template_tag(self):
        """ Test 1nic Template Tag is Correct """
        tmpl_loc = 'supported/standalone/1nic/new_stack/PAYG/'
        tmpl_file = tmpl_loc + 'azuredeploy.json'
        with open(tmpl_file, 'r') as file_str:
            file_data = json.load(file_str)
        tmpl_tag = file_data['variables']['f5TemplateTag']
        self.assertEqual(tmpl_tag, '1nic')

if __name__ == '__main__':
    unittest.main()
