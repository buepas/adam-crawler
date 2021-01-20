from typing import Any

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class RowParser():

    def __init__(self, driver: webdriver):
        self.driver = driver
        self.filter = {'goto_adam_fold': "folder", "goto_adam_file": "file", "ilLinkResourceHandlerGUI": "link"}

    def parse(self):
        ret = []
        elements = self.driver.find_elements_by_class_name("ilObjListRow")


        for elem in elements:
            try:
                ref_a = elem.find_element_by_css_selector('a.il_ContainerItemTitle')
                ref = ref_a.get_attribute('href')
                ret.append((ref_a.text, ref, self.get_ref_type(ref)))
            except NoSuchElementException:
                print("test")

        return ret

    def get_ref_type(self, ref):
        for pattern, ref_type in self.filter.items():
            if pattern in ref:
                return ref_type
        return "unknown"