# NOTE: Have to disable the Django Debug Toolbar FIRST!
# In settings.py comment out the INTERNAL_IPS or set DEBUG = FALSE
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


from vcb.test import clearMC3Bank
from functional_tests.test import SeleniumTestCase
from vcb.models import Classes

import logging
    
class AdminVCBEditClassMC3(SeleniumTestCase):
    def setUp(self):
        self.setup_admin_user(0, 0, False)
        
        self.browser = webdriver.Chrome(settings.SELENIUM_WEBDRIVER)
        self.browser.implicitly_wait(10)
    
    def tearDown(self):
        self.browser.quit()
        clearMC3Bank(self.obj_bank_id)
    
#    def test_admin_can_login(self):
#        """
#        Admin user can log into VCB
#        """
#        self.open('/vcb/')
#        body = self.browser.find_element_by_tag_name('body')
#        self.assertIn('OEIT Video Concept Browser', body.text)
#        
#        self.admin_logs_in()
#        
#        # her username and password are accepted, and she is taken to
#        # the Site Administration page
#        body = self.browser.find_element_by_tag_name('body')
#        self.assertIn('Video Player', body.text)
#        
#    def test_dashboard_renders_properly(self):
#        """
#        The dashboard renders properly for the Admin user. This means it 
#        should include an "Administrative" heading with two sub-buttons
#        for modifying classes and downloading a click log
#        """
#        self.admin_log_in_complete()
#        self.admin_check_dashboard()
#
#    
#    def test_click_log_downloads(self):
#        """
#        Clicking on the "Download Click Log" button downloads a text file
#        """
#        self.fail('Not really testable with Selenium--test by hand')
#        
#    def test_class_selector_modal_opens(self):
#        """
#        Creating / Modifying a class opens up the class selector modal
#        """
#        self.admin_log_in_complete()
#        
#        self.check_admin_class_modal()
#        
#        close_modal_x = self.browser.find_element_by_class_name('close')
#        close_modal_x.click()
#        
#        modal_wait = WebDriverWait(self.browser, 5).until(
#                EC.invisibility_of_element_located((By.CLASS_NAME,'modal-backdrop')))
#        
#        #Check that it opens again correctly  
#        self.check_admin_class_modal()
#        
#        cancel_modal_btn = self.browser.find_element_by_link_text('Cancel')
#        cancel_modal_btn.click()
#        
#        modal_wait = WebDriverWait(self.browser, 5).until(
#                EC.invisibility_of_element_located((By.CLASS_NAME,'modal-backdrop')))
#        
#        #Check that it opens again correctly   
#        self.check_admin_class_modal()
#    
#    def test_opening_existing_class_opens_right_admin_div(self):
#        """
#        Clicking on an existing class opens the right admin div
#        """
#        self.admin_login_and_open_existing_class_edit()
#        
#        self.assertTrue(self.check_exists_by_id('admin_div'))
#        
#        admin_status_box = self.browser.find_element_by_id('admin_status_box')
#        self.assertIn(
#            'successfully loaded',
#            admin_status_box.text)
#        
#        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
#        self.assertEqual(
#            'Class Canvas - test class',
#            admin_header.text)
#        
#        self.assertTrue(self.check_exists_by_id('cancel_map'))
#        self.assertTrue(self.check_exists_by_id('save_map'))
#        
#        self.open_topic_tree_one_level_with_activities()
#        
#    def test_creating_new_class_opens_right_admin_div(self):
#        """
#        Creating a new class opens the right admin div
#        """
#        self.admin_log_in_complete()
#        self.check_admin_class_modal()
#        
#        add_class = self.browser.find_element_by_id('add_class')
#        add_class.click()
#        
#        class_name = self.browser.find_element_by_id('class_name')
#        class_number = self.browser.find_element_by_id('class_number')
#        semester = self.browser.find_element_by_id('semester')
#        
#        class_name.send_keys('test class 2')
#        
#        ok_modal_btn = self.browser.find_element_by_link_text('OK')
#        ok_modal_btn.click()
#        
#        modal_status = self.browser.find_element_by_id('status_box')
#        
#        self.assertEqual(
#            'You must include a class name, a class number, and a semester',
#            modal_status.text)
#        
#        class_name.clear()
#        
#        class_number.send_keys('0.000')
#        
#        ok_modal_btn = self.browser.find_element_by_link_text('OK')
#        ok_modal_btn.click()
#        
#        self.assertEqual(
#            'You must include a class name, a class number, and a semester',
#            modal_status.text)
#        
#        class_number.clear()
#        semester.send_keys('Fall 2013')
#        
#        ok_modal_btn = self.browser.find_element_by_link_text('OK')
#        ok_modal_btn.click()
#        
#        self.assertEqual(
#            'You must include a class name, a class number, and a semester',
#            modal_status.text)
#            
#        class_name.send_keys('test class 2')
#        class_number.send_keys('0.000')
#        
#        ok_modal_btn = self.browser.find_element_by_link_text('OK')
#        ok_modal_btn.click()
#                        
#        self.assertTrue(self.check_exists_by_id('admin_div'))
#        
#        admin_status_box = self.browser.find_element_by_id('admin_status_box')
#        self.assertIn(
#            'successfully loaded',
#            admin_status_box.text)
#        
#        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
#        self.assertEqual(
#            'Class Canvas - test class 2, Fall 2013',
#            admin_header.text)
#        
#        self.assertTrue(self.check_exists_by_id('cancel_map'))
#        self.assertTrue(self.check_exists_by_id('save_map'))
#        
#        self.open_new_admin_tree()
#        
#        second_bank_id = Classes.objects.get(class_name = 'test class 2').obj_bank_id
#        clearMC3Bank(second_bank_id)
#        
#    def test_can_add_objective(self):
#        """
#        Once an admin div is open, the admin user can add an objective to the root
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_objective_to_root()
#        
#        self.click_modal_okay()
#
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#    
#    def test_cancel_add_objective_does_nothing(self):
#        """
#        Once an admin div is open, the admin user can add an objective to the root. But
#        canceling the modal does not add anything to the root.
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_objective_to_root()
#
#        self.click_modal_cancel()
#        
#        admin_status_box = self.browser.find_element_by_id('admin_status_box')
#        
#        self.assertEqual(
#            admin_status_box.text,
#            'Sorry, you must include a unique, non-blank objective name')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text_not_present('new learning objective')
#        
#    def test_can_add_subobjective(self):
#        """
#        An admin user can add a subobjective to an existing objective
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_subobjective_to_objective()
#        
#        self.click_modal_okay()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('new sub learning objective')
#
#    def test_cancel_add_subobjective_does_nothing(self):
#        """
#        An admin user can add a subobjective to an existing objective
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_subobjective_to_objective()
#        
#        self.click_modal_cancel()
#                
#        admin_status_box = self.browser.find_element_by_id('admin_status_box')
#        
#        self.assertEqual(
#            admin_status_box.text,
#            'Sorry, you must include a unique, non-blank objective name')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text_not_present('new sub learning objective')
#        
#    def test_can_add_activity_to_root_objective(self):
#        """
#        An admin user can add an activity to a root objective
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_activity_wrapper('learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text_not_present('test sub activity')
#    
#    def test_can_add_activity_to_subobjective(self):
#        """
#        An admin user can add an activity to a subobjective
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_activity_wrapper('sub learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('test sub activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#    
#    def test_cancel_add_activity_to_root_objective_does_nothing(self):
#        """
#        Nothing happens when an admin user cancels add an activity 
#        to an objective
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_activity_to_objective('learning objective')
#        
#        self.click_modal_cancel()
#        
#        admin_status_box = self.browser.find_element_by_id('admin_status_box')
#        
#        self.assertIn(
#            'Sorry, you must include all video details',
#            admin_status_box.text)
#                
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text_not_present('Demo 1')
#        self.check_svg_text_not_present('Demo 2')
#        self.check_svg_text_not_present('sub test activity')
#    
#    def test_no_context_menu_for_saved_activities(self):
#        """
#        Right-clicking an activity in the tree should bring up no context menu
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.right_click_svg_box('test activity')
#        
#        add_obj = self.browser.find_element_by_id('add_object')
#        add_act = self.browser.find_element_by_id('add_activity')
#        del_obj = self.browser.find_element_by_id('delete_object')
#        
#        self.assertFalse(add_obj.is_displayed())
#        self.assertFalse(add_act.is_displayed())
#        self.assertFalse(del_obj.is_displayed())
#        
#    def test_can_delete_activity(self):
#        """
#        An admin user can delete an activity she just added
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_activity_wrapper('learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.delete_activity('Demo 1')
#        
#        self.click_modal_cancel()
#              
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text_not_present('test sub activity')
#
#        self.delete_activity('Demo 1')
#        
#        self.click_modal_okay()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text_not_present('Demo 1')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.delete_activity('Demo 2')
#        
#        self.click_modal_okay()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text_not_present('Demo 1')
#        self.check_svg_text_not_present('Demo 2')
#        self.check_svg_text_not_present('test sub activity')
#    
#    def test_can_delete_subobjective(self):
#        """
#        An admin user can delete a subobjective she just added
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_subobjective_to_objective()
#        
#        self.click_modal_okay()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('new sub learning objective')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.delete_objective('new sub learning objective')
#        
#        self.click_modal_cancel()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('new sub learning objective')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.delete_objective('new sub learning objective')
#        
#        self.click_modal_okay()
#                
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text_not_present('test sub activity')
#        self.check_svg_text_not_present('new sub learning objective')
#        
#    def test_cannot_delete_saved_objectives(self):
#        """
#        Admin user cannot delete saved MC3 / Local objectives
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.cannot_delete_saved_object('test class')
#        self.cannot_delete_saved_object('learning objective')
#        self.cannot_delete_saved_object('sub learning objective')
#        self.cannot_delete_saved_object('test activity')
#    
#    def test_can_delete_objective(self):
#        """
#        An admin user can delete a root objective she just added
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_objective_to_root()
#        
#        self.click_modal_okay()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text_not_present('sub learning objective')
#        self.check_svg_text_not_present('test activity')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.delete_objective('new learning objective')
#        
#        self.click_modal_cancel()
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text_not_present('sub learning objective')
#        self.check_svg_text_not_present('test activity')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.delete_objective('new learning objective')
#        
#        self.click_modal_okay()
#                
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text_not_present('sub learning objective')
#        self.check_svg_text_not_present('test activity')
#        self.check_svg_text_not_present('test sub activity')
#        self.check_svg_text_not_present('new learning objective')
#    
#    def test_can_save_map(self):
#        """
#        An admin user can save a map she has created. The admin div should close.
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_and_saves_map()
#        
#    def test_close_edited_map(self):
#        """
#        Closing a modified map brings up a modal asking of the user really wants
#        to discard all of the new changes
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_map()
#        
#        self.close_modified_map()
#
#    def test_close_clean_map(self):
#        """
#        Closing a clean map returns to the dashboard with no confirmation modal
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        cancel_btn = self.browser.find_element_by_id('cancel_map')
#        cancel_btn.click()
#        
#        admin_div = self.browser.find_element_by_id('admin_div')
#        close_wait = WebDriverWait(self.browser, 3).until(
#                EC.staleness_of(admin_div))
#                
#        self.admin_check_dashboard()
#    
#    def test_saved_map_renders_properly_topic_view(self):
#        """
#        A saved map renders properly in topic view when selected from the left-hand menu
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_and_saves_map()
#        
#        self.admin_check_dashboard()
#        
#        topic_link = self.browser.find_element_by_xpath(
#                '//ul[@class="nav nav-tabs nav-stacked main-menu"]/li[2]/a[@class="view-tree"]')
#        topic_link.click()
#        
#        box_header_id = 'concept-box-header'
#        tree_heading = 'Concept Tree - test class'
#        load_wait = WebDriverWait(self.browser, 3).until(
#                EC.text_to_be_present_in_element((By.ID, box_header_id), tree_heading))
#        
#        h2_headers = self.browser.find_elements_by_tag_name('h2')
#        self.assertIn(tree_heading, [header.text for header in h2_headers])
#        
#        tree = self.browser.find_element_by_id('tree')
#        
#        self.assertTrue(tree.is_displayed())
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        
#        self.check_number_svg_nodes(3)
#        
#        self.click_svg_box('learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text_not_present('test sub activity')
#        
#        self.check_number_svg_nodes(7)
#        
#        self.click_svg_box('sub learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text('test sub activity')
#        
#        self.check_number_svg_nodes(8)
#        
#        self.click_svg_box('new learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        self.check_svg_text('test sub activity')
#        
#        self.check_number_svg_nodes(8)
#    
#    def test_saved_map_renders_properly_session_view(self):
#        """
#        A saved map renders properly in sesson view when selected from the left-hand menu
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_and_saves_map()
#        
#        self.admin_check_dashboard()
#        
#        session_link = self.browser.find_element_by_xpath(
#                '//ul[@class="nav nav-tabs nav-stacked main-menu"]/li[3]/a[@class="view-tree"]')
#        session_link.click()
#        
#        h2_headers = self.browser.find_elements_by_tag_name('h2')
#        self.assertIn('Concept Tree - test class', [header.text for header in h2_headers])
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('Lecture 0')
#        self.check_svg_text('Lecture 1')
#        
#        self.check_number_svg_nodes(3)
#        
#        self.click_svg_box('Lecture 0')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('Lecture 0')
#        self.check_svg_text('Lecture 1')
#        self.check_svg_text('test activity')
#        self.check_svg_text('test sub activity')
#        
#        self.check_number_svg_nodes(5)
#        
#        self.click_svg_box('Lecture 1')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('Lecture 0')
#        self.check_svg_text('Lecture 1')
#        self.check_svg_text('test activity')
#        self.check_svg_text('test sub activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        
#        self.check_number_svg_nodes(7)
#
#    def test_canceled_map_renders_properly_topic_view(self):
#        """
#        A canceled map renders properly in topic view when selected from the left-hand menu
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_map()
#        
#        self.close_modified_map()
#        
#        yes_btn = self.browser.find_element_by_link_text('Yes')
#        yes_btn.click()
#        
#        self.admin_check_dashboard()
#        
#        self.open_topic_tree_with_activities()
#    
#    def test_canceled_map_renders_properly_session_view(self):
#        """
#        A canceled map renders properly in sesson view when selected from the left-hand menu
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_map()
#        
#        self.close_modified_map()
#        
#        yes_btn = self.browser.find_element_by_link_text('Yes')
#        yes_btn.click()
#        
#        self.admin_check_dashboard()
#        
#        self.open_session_tree()
#
#    
#    def test_clicking_nav_menu_closes_admin_div_when_clean(self):
#        """
#        When the admin canvas is "clean" (the user has made no changes), clicking
#        on the left-hand nav menu closes the admin div and renders the clicked view...
#        in this case, the topic view
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        topic_link = self.browser.find_element_by_xpath(
#                '//ul[@class="nav nav-tabs nav-stacked main-menu"]/li[2]/a[@class="view-tree"]')
#        topic_link.click()
#        
#        admin_div = self.browser.find_element_by_id('admin_div')
#        close_wait = WebDriverWait(self.browser, 3).until(
#                EC.staleness_of(admin_div))
#        
#        tree_heading = 'Concept Tree - test class'
#        
#        h2_headers = self.browser.find_elements_by_tag_name('h2')
#        self.assertIn(tree_heading, [header.text for header in h2_headers])
#        
#        tree = self.browser.find_element_by_id('tree')
#        
#        self.assertTrue(tree.is_displayed())
#        
#        self.open_topic_tree_one_level_with_activities()
#        
#    def test_clicking_nav_menu_brings_confirmation_when_dirty(self):
#        """
#        When the admin canvas is "dirty" (the user has made unsaved changes), 
#        clicking on the left-hand menu will bring up a confirmation box asking
#        if the user really wants to discard her changes.
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.admin_updates_map()
#        
#        topic_link = self.browser.find_element_by_xpath(
#                '//ul[@class="nav nav-tabs nav-stacked main-menu"]/li[2]/a[@class="view-tree"]')
#        topic_link.click()
#        
#        modal_wait = WebDriverWait(self.browser, 3).until(
#                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
#        modal_wait = WebDriverWait(self.browser, 3).until(
#                EC.visibility_of_element_located((By.CLASS_NAME,'modal-backdrop')))
#        
#        modal_body = self.browser.find_element_by_class_name('modal-body')
#        self.assertEqual(
#            'Really throw away all of your un-saved work?',
#            modal_body.text)
#        
#        self.check_for_links('No!')
#        self.check_for_links('Yes')
#    
#    def test_confirm_discard_closes_admin_div(self):
#        """
#        Confirming that she wants to discard her changes will close the admin div
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#
#        self.admin_updates_map()
#
#        self.close_modified_map()
#
#        yes_btn = self.browser.find_element_by_link_text('Yes')
#        yes_btn.click()
#
#        self.admin_check_dashboard()
#    
#    def test_no_discard_returns_to_admin_div(self):
#        """
#        Saying she does not want to discard changes will return her to the admin div
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#
#        self.admin_updates_map()
#
#        self.close_modified_map()
#
#        no_btn = self.browser.find_element_by_link_text('No!')
#        no_btn.click()
#        
#        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
#        self.assertEqual(
#            'Class Canvas - test class',
#            admin_header.text)
#        
#        self.assertTrue(self.check_exists_by_id('cancel_map'))
#        self.assertTrue(self.check_exists_by_id('save_map'))
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text('sub learning objective')
#        self.check_svg_text('test activity')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        
#        self.check_number_svg_nodes(7)
#    
#    def test_logging_out_redirects_to_login_page(self):
#        """
#        Logging out of the admin page should redirect to the main page
#        """
#        self.admin_log_in_complete()
#        log_out = self.browser.find_element_by_link_text('Logout')
#        log_out.click()
#        body = self.browser.find_element_by_tag_name('body')
#        self.assertIn('OEIT Video Concept Browser', body.text)
#    
#    def test_can_add_activity_and_objective(self):
#        """
#        Can add an activity to a newly created objective
#        """
#        self.admin_login_and_open_existing_class_edit()
#        self.open_topic_tree_one_level_with_activities()
#        
#        self.add_objective_to_root()
#        
#        self.click_modal_okay()
#
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        
#        self.check_number_svg_nodes(3)
#        
#        self.add_activity_wrapper('new learning objective')
#        
#        self.check_svg_text('test class')
#        self.check_svg_text('learning objective')
#        self.check_svg_text('new learning objective')
#        self.check_svg_text('Demo 1')
#        self.check_svg_text('Demo 2')
#        
#        self.check_number_svg_nodes(5)
#        
#        save_btn = self.browser.find_element_by_id('save_map')
#        save_btn.click()
#        
#        success_text = 'super successfully created new activity Demo 1 locally;' + \
#                ' super successfully created a new Class Session Lecture 1 locally;' + \
#                ' super successfully mapped activity Demo 1 to Lecture 1 locally;' + \
#                ' super successfully created new activity Demo 2 locally;' + \
#                ' super successfully mapped activity Demo 2 to Lecture 1 locally;' + \
#                ' Successfully mapped objective new learning objective to MC3;' + \
#                ' Saved objective new learning objective;' + \
#                ' and saved test class'
#
#        admin_div = self.browser.find_element_by_id('admin_div')
#        save_wait = WebDriverWait(self.browser, 3).until(
#                EC.staleness_of(admin_div))
#        
#        main_status_box = self.browser.find_element_by_id('main_status_box')
#        
#        self.assertEqual(
#            success_text,
#            main_status_box.text)
#
#    def test_amps_xml_parsed_correctly(self):
#        """
#        Admin user can upload an XML file and see the right parsing for AMPS use
#        """
#        self.admin_log_in_complete()
#        
#        xpath = '//ul[@class="nav nav-tabs nav-stacked main-menu"]/li[7]/a[@class="nav-amps"]'
#        amps_btn = self.browser.find_element_by_xpath(xpath)
#        amps_btn.click()
#        
#        modal_wait = WebDriverWait(self.browser, 5).until(
#                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
#        
#        h3_headers = self.browser.find_elements_by_tag_name('h3')
#        self.assertIn(
#                'Upload XML file',
#                [header.text for header in h3_headers])
#        
#        self.assertTrue(self.check_exists_by_id('modal_status_box'))
#        self.assertTrue(self.check_exists_by_id('xml_form'))
#        self.assertTrue(self.check_exists_by_id('xml_file'))
#        self.assertTrue(self.check_exists_by_id('process'))
#        self.assertTrue(self.check_exists_by_id('modal_results'))
#        
#        label_xpath = '//div/form[@id="xml_form"]/label'
#        xml_label = self.browser.find_element_by_xpath(label_xpath)
#        self.assertEqual(
#                xml_label.text,
#                'XML File:')
#        
#        file_input = self.browser.find_element_by_id('xml_file')
#        file_location = '/Users/cjshaw/Documents/Projects/i2002/3.032/example_xml.xml'
#        file_input.send_keys(file_location)
#        
#        process_btn = self.browser.find_element_by_id('process')
#        process_btn.click()
#        
#        click_wait = WebDriverWait(self.browser, 3).until(
#                EC.presence_of_element_located((By.ID,'table_body')))
#        
#        table_body = self.browser.find_element_by_id('table_body')
#        rows = table_body.find_elements_by_tag_name('tr')
#        expected_offsets = ['00:00:57','00:01:15']
#        expected_subjects = ['Describing screencast','Syllabus']
#        expected_rows = 2
#        
#        row_count = 0
#        for row in rows:
#            offset = row.find_elements_by_tag_name('td')[0]
#            subject = row.find_elements_by_tag_name('td')[1]
#            
#            self.assertEqual(
#                    offset.text,
#                    expected_offsets[row_count])
#            self.assertEqual(
#                    subject.text,
#                    expected_subjects[row_count])
#            row_count += 1
#        
#        self.assertEqual(
#                expected_rows,
#                row_count)

    def test_can_copy_class_to_new_semester(self):
        """
        An admin user can copy a class and create a new version, with a 
        different semester
        """
        self.admin_log_in_complete()
        
        search_bar = self.browser.find_element_by_class_name('search-query')
        
        self.check_admin_class_modal()
        
        test_class = self.browser.find_element_by_xpath('//div[@id="add_semester"]/ul[@class="dropdown-menu"]/li[@class="text-left select-semester"][1]/a')
        test_class.click()
        
        text_wait = WebDriverWait(self.browser, 3).until(
                EC.text_to_be_present_in_element_value((By.ID,'class_name'), 'test class'))
        
        self.assertTrue(self.check_exists_by_id('class_name'))
        self.assertTrue(self.check_exists_by_id('obj_bank_id'))
        self.assertTrue(self.check_exists_by_id('semester'))
        self.assertTrue(self.check_exists_by_id('new_semester'))
        
        class_name = self.browser.find_element_by_id('class_name')
        obj_bank_id = self.browser.find_element_by_id('obj_bank_id')
        semester = self.browser.find_element_by_id('semester')
        new_semester = self.browser.find_element_by_id('new_semester')
        
        self.assertEqual(
                class_name.get_attribute('value'),
                'test class')
        self.assertEqual(
                obj_bank_id.get_attribute('value'),
                self.obj_bank_id.replace('\n','')) # Hack!
        self.assertEqual(
                semester.get_attribute('value'),
                'Spring 2012')

        new_semester.send_keys('Spring 2014')
                
        ok_modal_btn = self.browser.find_element_by_link_text('OK')
        ok_modal_btn.click()
        
        admin_status_box = self.browser.find_element_by_id('admin_status_box')
        
        self.assertIn(
                'Congratulations, the class was successfully copied to a new semester. Your access code is:',
                admin_status_box.text)
        
        modal_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'bootbox')))
        search_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'search-query')))
                
        self.assertFalse(search_bar.is_displayed())
        
        self.assertTrue(self.check_exists_by_id('admin_div'))
        
        admin_status_box = self.browser.find_element_by_id('admin_status_box')
        self.assertIn(
            'successfully copied to a new semester',
            admin_status_box.text)
        
        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
        self.assertEqual(
            'Class Canvas - test class, Spring 2014',
            admin_header.text)
        
        self.assertTrue(self.check_exists_by_id('cancel_map'))
        self.assertTrue(self.check_exists_by_id('save_map'))
        
        self.open_topic_tree_one_level_with_activities()
#                    
#    def test_copy_to_existing_semester_displays_error_message(self):
#        """
#        Trying to copy a course into a semester that already exists
#        should display an error message
#        """
#        self.admin_log_in_complete()
#        
#        self.check_admin_class_modal()
#        
#        test_class = self.browser.find_element_by_xpath('//div[@id="add_semester"]/ul[@class="dropdown-menu"]/li[@class="text-left select-semester"][1]/a')
#        test_class.click()
#        
#        text_wait = WebDriverWait(self.browser, 3).until(
#                EC.text_to_be_present_in_element_value((By.ID,'class_name'), 'test class'))
#        
#        self.assertTrue(self.check_exists_by_id('class_name'))
#        self.assertTrue(self.check_exists_by_id('obj_bank_id'))
#        self.assertTrue(self.check_exists_by_id('semester'))
#        self.assertTrue(self.check_exists_by_id('new_semester'))
#        
#        class_name = self.browser.find_element_by_id('class_name')
#        obj_bank_id = self.browser.find_element_by_id('obj_bank_id')
#        semester = self.browser.find_element_by_id('semester')
#        new_semester = self.browser.find_element_by_id('new_semester')
#        
#        self.assertEqual(
#                class_name.get_attribute('value'),
#                'test class')
#        self.assertEqual(
#                obj_bank_id.get_attribute('value'),
#                self.obj_bank_id.replace('\n','')) # Hack!
#        self.assertEqual(
#                semester.get_attribute('value'),
#                'Spring 2012')
#        
#        new_semester.send_keys('Spring 2012')
#        
#        ok_modal_btn = self.browser.find_element_by_link_text('OK')
#        ok_modal_btn.click()
#        
#        modal_status_box = self.browser.find_element_by_id('status_box')
#        
#        self.assertEqual(
#                modal_status_box.text,
#                'Your new semester cannot already exist')