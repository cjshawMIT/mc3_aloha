# Testing structure modeled off of this
# https://github.com/lincolnloop/django-selenium-intro/tree/master/selenium_intro
import logging
import pickle
import pdb

from django.test import LiveServerTestCase
from django.contrib.auth.models import User, Group
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from vcb.test import create_data

class SeleniumTestCase(LiveServerTestCase):
    """
    A base test case for selenium, providing helper methods for generating
    clients and logging in profiles.
    """
        
    def open(self, url):
        self.browser.get("%s%s" % (self.live_server_url, url))

    def setup_admin_user(self, pdays, tdays, local=True):
        """
        Create the admin user and classes
        """
        self.maxDiff = None
        admin_user = User.objects.create_superuser(username='super',
                                                   password='user',
                                                   email='me@mit.edu')
        result = create_data(pdays, tdays, local)
        self.new_class_session = result['new_class_session']
        self.new_obj = result['new_obj']
        self.new_sub_obj = result['new_sub_obj']
        self.new_activity = result['new_activity']
        self.new_sub_activity = result['new_sub_activity']
        self.new_session = result['new_session']
        
        self.obj_bank_id = self.new_class_session.obj_bank_id
        
        group_name = self.new_class_session.class_name + ', ' + self.new_class_session.semester
        
        new_group, created = Group.objects.get_or_create(
                name = group_name)
        admin_user.groups.add(new_group)
    
    def setup_student_user(self, pdays, tdays, local=True):
        """
        Create the student user and classes
        """
        student = User.objects.create_user(username='student',
                                 password='learner',
                                 email='you@mit.edu')
        result = create_data(pdays, tdays, local)
        self.new_class_session = result['new_class_session']
        self.new_obj = result['new_obj']
        self.new_sub_obj = result['new_sub_obj']
        self.new_activity = result['new_activity']
        self.new_sub_activity = result['new_sub_activity']
        self.new_session = result['new_session']
    
        self.obj_bank_id = self.new_class_session.obj_bank_id
        
        group_name = self.new_class_session.class_name + ', ' + self.new_class_session.semester
        
        new_group, created = Group.objects.get_or_create(
                name = group_name)
        student.groups.add(new_group)
    
    def add_objective_to_root(self):
        """
        Admin users can add objectives to the root node when editing a class
        """
        action_div = self.browser.find_element_by_id('action_div')
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box('test class')
                        
        self.assertTrue(action_div.is_displayed())
        add_obj = self.browser.find_element_by_id('add_object')
        add_act = self.browser.find_element_by_id('add_activity')
        del_obj = self.browser.find_element_by_id('delete_object')
        
        self.assertTrue(add_obj.is_displayed())
        self.assertFalse(add_act.is_displayed())
        self.assertFalse(del_obj.is_displayed())
        
        # click outside of the svg to verify the action menu closes
        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
        admin_header.click()
        
        unload_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.ID, 'action_div')))
        
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box('test class')
                
        self.assertTrue(action_div.is_displayed())
        self.assertTrue(add_obj.is_displayed())
        self.assertFalse(add_act.is_displayed())
        self.assertFalse(del_obj.is_displayed())
        
        create_obj_btn = self.browser.find_element_by_id('add_object')
        create_obj_btn.click()
        
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
        
        obj_name_modal = self.browser.find_element_by_xpath(
                '//div[@class="bootbox modal fade in"]')
        modal_background = self.browser.find_element_by_class_name('modal-backdrop')

        self.assertTrue(obj_name_modal.is_displayed())
        self.assertTrue(modal_background.is_displayed())
        
        obj_name_input = self.browser.find_element_by_xpath(
                '//div[@class="modal-body"]/form/input[@class="input-block-level"]')
        
        obj_name_input.send_keys('new learning objective')
     
    def add_subobjective_to_objective(self):
        """
        Admin users can add subobjectives to objectives when editing a class
        """
        action_div = self.browser.find_element_by_id('action_div')
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box('learning objective')
                
        self.assertTrue(action_div.is_displayed())
        add_obj = self.browser.find_element_by_id('add_object')
        add_act = self.browser.find_element_by_id('add_activity')
        del_obj = self.browser.find_element_by_id('delete_object')
        
        self.assertTrue(add_obj.is_displayed())
        self.assertTrue(add_act.is_displayed())
        self.assertFalse(del_obj.is_displayed())
        
        # click outside of the svg to verify the action menu closes
        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
        admin_header.click()
        
        unload_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.ID, 'action_div')))
        
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box('learning objective')
                
        self.assertTrue(action_div.is_displayed())
        self.assertTrue(add_obj.is_displayed())
        self.assertTrue(add_act.is_displayed())
        self.assertFalse(del_obj.is_displayed())
         
        create_obj_btn = self.browser.find_element_by_id('add_object')
        create_obj_btn.click()
         
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
        
        obj_name_modal = self.browser.find_element_by_xpath(
                '//div[@class="bootbox modal fade in"]')
        modal_background = self.browser.find_element_by_class_name('modal-backdrop')
        self.assertTrue(obj_name_modal.is_displayed())
        self.assertTrue(modal_background.is_displayed())
        
        obj_name_input = self.browser.find_element_by_xpath(
                '//div[@class="modal-body"]/form/input[@class="input-block-level"]')
        
        obj_name_input.send_keys('new sub learning objective')

    def add_activity_to_objective(self, parent_label):
        """
        Admin users can add activities to objective with text parent_label
        when editing a class
        """
        action_div = self.browser.find_element_by_id('action_div')
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box(parent_label)
                
        self.assertTrue(action_div.is_displayed())
        add_obj = self.browser.find_element_by_id('add_object')
        add_act = self.browser.find_element_by_id('add_activity')
        del_obj = self.browser.find_element_by_id('delete_object')
        
        self.assertTrue(add_obj.is_displayed())
        self.assertTrue(add_act.is_displayed())
        
        if 'new' in parent_label:
            self.assertTrue(del_obj.is_displayed())
        else:
            self.assertFalse(del_obj.is_displayed())
        
        # click outside of the svg to verify the action menu closes
        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
        admin_header.click()
        
        unload_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.ID, 'action_div')))
        
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box(parent_label)
                
        self.assertTrue(action_div.is_displayed())
        self.assertTrue(add_obj.is_displayed())
        self.assertTrue(add_act.is_displayed())
        if 'new' in parent_label:
            self.assertTrue(del_obj.is_displayed())
        else:
            self.assertFalse(del_obj.is_displayed())
         
        create_act_btn = self.browser.find_element_by_id('add_activity')
        create_act_btn.click()
         
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
        
        obj_name_modal = self.browser.find_element_by_xpath(
                '//div[@class="bootbox modal fade in"]')
        modal_background = self.browser.find_element_by_class_name('modal-backdrop')
        self.assertTrue(obj_name_modal.is_displayed())
        self.assertTrue(modal_background.is_displayed())
        
        h3_headers = self.browser.find_elements_by_tag_name('h3')
        self.assertIn(
            'Enter the video data:',
            [header.text for header in h3_headers])
        
        self.assertTrue(self.check_exists_by_id('video_file'))
        self.assertTrue(self.check_exists_by_id('class_session'))
        self.assertTrue(self.check_exists_by_id('recorded_date'))
        self.assertTrue(self.check_exists_by_id('pubdate'))
        self.assertTrue(self.check_exists_by_id('add-row'))
        self.assertTrue(self.check_exists_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][1]/td[2]/input'))
        self.assertTrue(self.check_exists_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][1]/td[3]/input'))
        
        video_input = self.browser.find_element_by_id('video_file')
        #video_input.send_keys('/Users/cjshaw/Documents/Projects/i2002/17595.mp4')
        video_input.send_keys('/Users/cjshaw/Documents/Projects/i2002/sample_movie.mp4')
    
    def add_activity_wrapper(self, parent_label):
        """
        Manages the add activity process
        """
        self.add_activity_to_objective(parent_label)
        
        ok_modal_btn = self.browser.find_element_by_link_text('OK')
        ok_modal_btn.click()
        
        modal_status_box = self.browser.find_element_by_id('status_box')
        
        self.assertIn(
            'Please wait for the video to finish uploading, before pressing OK',
            modal_status_box.text)
            
        percent = self.browser.find_element_by_class_name('percent')
        
        file_wait = WebDriverWait(self.browser, 300).until(
                EC.text_to_be_present_in_element((By.ID,'status_box'), 'Upload complete.'))
        
        ok_modal_btn = self.browser.find_element_by_link_text('OK')
        ok_modal_btn.click()
        
        self.assertIn(
            'Please fill in all fields, including at least one Timetag',
            modal_status_box.text)
        
        self.fill_activity_form()
        
        self.click_modal_okay()
        
    
    def add_activity_wrapper_xml(self, parent_label):
        """
        Manages the add activity process but using an XML file
        """
        self.add_activity_to_objective(parent_label)
        
        ok_modal_btn = self.browser.find_element_by_link_text('OK')
        ok_modal_btn.click()
        
        modal_status_box = self.browser.find_element_by_id('status_box')
        
        self.assertIn(
            'Please wait for the video to finish uploading, before pressing OK',
            modal_status_box.text)
            
        percent = self.browser.find_element_by_class_name('percent')
        
        file_wait = WebDriverWait(self.browser, 100).until(
                EC.text_to_be_present_in_element((By.ID,'status_box'), 'Upload complete.'))
        
        ok_modal_btn = self.browser.find_element_by_link_text('OK')
        ok_modal_btn.click()
        
        self.assertIn(
            'Please fill in all fields, including at least one Timetag',
            modal_status_box.text)
        
        self.fill_activity_form_xml()
        
        self.click_modal_okay()
    
    def admin_logs_in(self):
        """
        Helper function that logs the student user into the page
        """
        email_tab = self.browser.find_element_by_link_text('Login with Email')
        email_tab.click()
        
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('super')
        
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('user')

        submit = self.browser.find_element_by_id('login')
        submit.click()
    
    def admin_log_in_complete(self):
        """
        Includes navigation to the vcb main page
        """
        self.open('/vcb/')
        
        self.admin_logs_in()
    
    def cannot_delete_saved_object(self, name):
        """
        Checks that the context menu for 'name' object has no delete option
        """
        action_div = self.browser.find_element_by_id('action_div')
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box(name)
        
        self.assertTrue(action_div.is_displayed())

        del_obj = self.browser.find_element_by_id('delete_object')

        self.assertFalse(del_obj.is_displayed())
        
        # click outside of the svg to verify the action menu closes
        admin_header = self.browser.find_element_by_id('admin_canvas_heading')
        admin_header.click()
        
        unload_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.ID, 'action_div')))
    
    def check_admin_class_modal(self):
        """
        Check the Admin modal that pops up with "Add Class" or "Modify Existing Class"
        options
        """
        create_class_btn = self.browser.find_element_by_class_name('nav-admin')
        create_class_btn.click()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
        
        # Check that modal is present and rendered appropriately
        self.assertTrue(self.check_exists_by_id('class_form'))
        
        self.assertTrue(self.check_exists_by_id('add_class'))
        self.assertTrue(self.check_exists_by_id('add_semester'))
        self.assertTrue(self.check_exists_by_id('class_dropdown'))
        
        modal_background = self.browser.find_element_by_class_name('modal-backdrop')
        self.assertTrue(modal_background.is_displayed())
        
        self.assertTrue(self.check_exists_by_id('add_class'))
        self.assertTrue(self.check_exists_by_id('add_semester'))
        self.assertTrue(self.check_exists_by_id('class_dropdown'))
        
        add_class_btn = self.browser.find_element_by_id('add_class')
        add_class_btn.click()
        
        self.assertTrue(self.check_exists_by_id('class_name'))
        self.assertTrue(self.check_exists_by_id('class_number'))
        self.assertTrue(self.check_exists_by_id('obj_bank_id'))
        self.assertTrue(self.check_exists_by_id('semester'))
        self.assertTrue(self.check_exists_by_id('new_class'))
        
        existing_class_btn = self.browser.find_element_by_id('dropdown_trigger')
        existing_class_btn.click()
        
        self.assertTrue(self.check_exists_by_class_name('open'))
        
        semester_btn = self.browser.find_element_by_id('semester_trigger')
        semester_btn.click()
        
        self.assertTrue(self.check_exists_by_class_name('open'))
        
    def check_for_links(self, link_text):
        """
        Helper function to check links on a page for certain text
        """
        links = self.browser.find_elements_by_tag_name('a')
        self.assertIn(link_text, [link.text for link in links])
 
    def check_exists_by_class_name(self, class_name):
        """
        Helper function to determine if a DOM element exists via class_name. From:
        http://seleniumwebdriverfaq.blogspot.in/2012/03/how-can-i-check-presence-of-webelement_5206.html
        """
        try:
            self.browser.find_element_by_class_name(class_name)
        except NoSuchElementException:
            return False
        return True
    
    def check_exists_by_id(self, id):
        """
        Helper function to determine if a DOM element exists via ID. From:
        http://seleniumwebdriverfaq.blogspot.in/2012/03/how-can-i-check-presence-of-webelement_5206.html
        """
        try:
            self.browser.find_element_by_id(id)
        except NoSuchElementException:
            return False
        return True
    
    def check_exists_by_xpath(self, xpath):
        """
        Helper function to determine if a DOM element exists via xpath. From:
        http://seleniumwebdriverfaq.blogspot.in/2012/03/how-can-i-check-presence-of-webelement_5206.html
        """
        try:
            self.browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
        
    def check_number_svg_nodes(self, number):
        """
        Checks the number of nodes drawn on the current tree matches the given number
        """
        nodes = self.browser.find_elements_by_class_name('node')
        self.assertTrue(len(nodes) == number)
    
    def check_svg_text(self, query_string):
        """
        Helper function to determine if a string of text exists in an SVG element
        http://stackoverflow.com/questions/14592213/selenium-webdriver-clicking-on-elements-within-an-svg-using-xpath
        """
        nodes = self.browser.find_elements_by_class_name('node')
        self.assertIn(query_string, [node.text for node in nodes])
    
    def check_test_activity_video_playing(self):
        """
        Helper function that checks that the test activity video is correctly
        configured to play in the video player. Does not actually check the status
        of the player
        """
        subject = self.browser.find_element_by_id('subject')
        self.assertEqual('test activity', subject.text)

        sharelink = self.browser.find_element_by_id('sharelink')
        self.assertIn('/vcb/dashboard/?jumpto=', sharelink.text)

    def check_video_metadata_present(self):
        """
        Helper function to check that a video's metadata is present and toggles
        """
        powertip = self.browser.find_element_by_id('powerTip')
        self.assertFalse(powertip.is_displayed())

        toggle_metadata = self.browser.find_element_by_class_name('toggle-metadata')

        builder = ActionChains(self.browser)
        hover = builder.move_to_element(toggle_metadata)
        hover.perform()

        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.ID, 'powerTip')))

        self.assertTrue(powertip.is_displayed())

        builder = ActionChains(self.browser)
        mouseout = builder.move_to_element(toggle_metadata) \
                          .move_by_offset(-100, -100)
        mouseout.perform()

        unload_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.ID, 'powerTip')))
        self.assertFalse(powertip.is_displayed())

    def click_svg_box(self, box_text, will_expand=True):
        """
        Clicks a web element in the SVG that is the box you want to click, where
        the text matches box_text
        # Ideally this would pause somehow...but I can't figure out how to
        # 'wait' for an SVG element to appear or change color...
        """
        nodes = self.browser.find_elements_by_class_name('node')
        number_nodes = len(nodes)
        for node in nodes:
            if node.text == box_text:
                click_object = node
            else:
                pass
        click_object.click()

        if 'activity' not in box_text and 'new' not in box_text and will_expand:
            new_number_nodes = number_nodes + 1
            new_xpath = '//*[@class="node"][' + str(new_number_nodes) + ']'
            load_wait = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, new_xpath)))
        
        if 'activity' in box_text and 'new' not in box_text:
            wait = WebDriverWait(self.browser, 3).until(
                EC.text_to_be_present_in_element((By.ID, 'subject'), box_text)
            )
            #self.assertTrue(self.check_exists_by_class_name('spinner'))
            #spinner = self.browser.find_element_by_class_name('spinner')
            #
            #loaded_wait = WebDriverWait(self.browser, 3).until(
            #        EC.staleness_of(spinner))
        
    
    def right_click_svg_box(self, box_text):
        """
        Right clicks (i.e. context click) a web element in the SVG that 
        is the box you want to click, where the text matches box_text
        """
        nodes = self.browser.find_elements_by_class_name('node')
        for node in nodes:
            if node.text == box_text:
                click_object = node
            else:
                pass
        builder = ActionChains(self.browser)
        
        right_click = builder.move_to_element(click_object) \
                             .context_click()
        right_click.perform()
        
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.ID, 'action_div')))
        
    def click_modal_okay(self):
        """
        Click the okay button when adding a new objective or activity
        """
        ok_modal_btn = self.browser.find_element_by_link_text('OK')
        ok_modal_btn.click()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'bootbox')))
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'modal-backdrop')))
                    
        self.assertFalse(self.check_exists_by_class_name('modal-backdrop'))
        
        admin_status_box = self.browser.find_element_by_id('admin_status_box')
        
        self.assertEqual(
            admin_status_box.text,
            '')
    
    def click_modal_cancel(self):
        """
        Click the cancel button when adding a new objective or activity
        """
        cancel_modal_btn = self.browser.find_element_by_link_text('Cancel')
        cancel_modal_btn.click()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'bootbox')))
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'modal-backdrop')))
              
        self.assertFalse(self.check_exists_by_class_name('modal-backdrop'))
    
    def close_modified_map(self):
        """
        Close a modified class map
        """
        cancel_btn = self.browser.find_element_by_id('cancel_map')
        cancel_btn.click()
        
        modal_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
        modal_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'modal-backdrop')))
        
        modal_body = self.browser.find_element_by_class_name('modal-body')
        self.assertEqual(
            'Really throw away all of your un-saved work?',
            modal_body.text)
        
        self.check_for_links('No!')
        self.check_for_links('Yes')
    
    def admin_check_dashboard(self):
        """
        Checks that the admin dashboard looks correct
        """
        class_name = self.new_class_session.class_name
        
        side_nav_menu = self.browser.find_elements_by_class_name('nav-header')
        self.assertTrue(class_name, [nav_header.text for nav_header in side_nav_menu])
        
        # Check the top navbar links and search field
        search_bar = self.browser.find_element_by_class_name('search-query')
        self.assertEqual(
            search_bar.get_attribute('placeholder'),
            'Search')
        
        user_icon = self.browser.find_element_by_class_name('dropdown-toggle')
        user_icon.click()
        self.check_for_links('Logout')
        self.check_for_links('Profile')

        # Check the left-hand nav bar links
        self.check_for_links('View by Topic')
        self.check_for_links('View by Class')
        self.check_for_links('Recently Viewed')
        self.check_for_links('Create / Modify Classes')
        self.check_for_links('AMPS: Parse XML File')
        self.check_for_links('Download Click Log')
        self.check_for_links('Help')
        self.check_for_links('Logout')
        
        nav_headers = self.browser.find_elements_by_class_name('nav-header')
        
        self.assertIn(
                'TEST CLASS, SPRING 2012',
                [header.text for header in nav_headers])
        self.assertIn(
                'ADMINISTRATIVE',
                [header.text for header in nav_headers])
        
        # Footer links
#        self.check_for_links('Muhammad Usman')
        self.check_for_links('MIT OEIT')
#        self.check_for_links('Charisma')
        
        # Video veiwer pane and concept map pane
        pane_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertTrue('Video Player',
                [pane_header.text for pane_header in pane_headers])
        self.assertTrue('Concept Tree',
                [pane_header.text for pane_header in pane_headers])
        video_metadata = self.browser.find_element_by_class_name('toggle-metadata')
        self.assertIn('Video Metadata', video_metadata.text)
                
        # Check the help modal is present but not viewable
        help_modal = self.browser.find_element_by_id('help_modal')
        self.assertEqual(
            help_modal.get_attribute('display'),
            None)
        modal_headers = self.browser.find_elements_by_tag_name('h3')
        self.assertTrue('About this Site',
                [modal_header.text for modal_header in modal_headers])
        self.assertTrue('Using this Site',
                [modal_header.text for modal_header in modal_headers])
        self.assertTrue('Questions or Problems?',
                [modal_header.text for modal_header in modal_headers])
                
        box_header_id = 'concept-box-header'
        tree_heading = 'Concept Tree - test class, Spring 2012'
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.text_to_be_present_in_element((By.ID, box_header_id), tree_heading))
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn(tree_heading, [header.text for header in h2_headers])
        
        tree = self.browser.find_element_by_id('tree')
        
        self.assertTrue(tree.is_displayed())
                
    def admin_updates_map(self):
        """
        Admin user makes changes to a class map
        """
        self.add_objective_to_root()
        
        self.click_modal_okay()

        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        self.check_svg_text('new learning objective')
        
        self.add_activity_wrapper('learning objective')
        
        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        self.check_svg_text('new learning objective')
        self.check_svg_text('sub learning objective')
        self.check_svg_text('test activity')
        self.check_svg_text('Demo 1')
        self.check_svg_text('Demo 2')
        self.check_svg_text_not_present('test sub activity')
    
    def admin_updates_and_saves_map(self):
        """
        Admin user adds an objective and two activities to a map, then saves it
        """
        self.admin_updates_map()
        
        save_btn = self.browser.find_element_by_id('save_map')
        save_btn.click()
        
        success_text = 'super successfully created new activity Demo 1 locally;' + \
                ' super successfully created a new Class Session Lecture 1 locally;' + \
                ' super successfully mapped activity Demo 1 to Lecture 1 locally;' + \
                ' super successfully created new activity Demo 2 locally;' + \
                ' super successfully mapped activity Demo 2 to Lecture 1 locally;' + \
                ' Successfully mapped objective new learning objective to MC3;' + \
                ' Saved objective new learning objective;' + \
                ' and saved test class, Spring 2012'

        admin_div = self.browser.find_element_by_id('admin_div')
        save_wait = WebDriverWait(self.browser, 3).until(
                EC.staleness_of(admin_div))
        
        main_status_box = self.browser.find_element_by_id('main_status_box')
        
        self.assertEqual(
            success_text,
            main_status_box.text)
    
    def admin_login_and_open_recently_viewed_with_activities(self):
        """
        Helper function to log in the admin and open the list of recently viewed videos
        """
        self.admin_log_in_complete() 
        self.open_recently_viewed_with_activities()
                
    def admin_login_and_open_session_tree(self):
        """
        Helper function to log in the admin and open the session tree
        """
        self.admin_log_in_complete() 
        self.open_session_tree()
        
    def admin_login_and_open_topic_tree_with_activities(self):
        """
        Helper function to log in the admin and open the topic tree
        """
        self.admin_log_in_complete() 
        self.open_topic_tree_with_activities()
    
    def admin_login_and_open_existing_class_edit(self):
        """
        Helper function to log in the admin and open a class to edit
        """
        self.admin_log_in_complete()
        
        search_bar = self.browser.find_element_by_class_name('search-query')
        
        self.check_admin_class_modal()
        
        existing_class_btn = self.browser.find_element_by_id('dropdown_trigger')
        existing_class_btn.click()
        
        test_class = self.browser.find_element_by_xpath('//div[@id="class_dropdown"]/ul[@class="dropdown-menu"]/li[@class="text-left select-class"][1]/a')
        test_class.click()
        
        text_wait = WebDriverWait(self.browser, 3).until(
                EC.text_to_be_present_in_element_value((By.ID,'class_name'), 'test class'))
        
        class_name = self.browser.find_element_by_id('class_name')
        obj_bank_id = self.browser.find_element_by_id('obj_bank_id')
        semester = self.browser.find_element_by_id('semester')
        
        self.assertEqual(
            class_name.get_attribute('value'),
            'test class')
        # This is a hack...replacing \n with nothing because the value in javascript/html
        # automatically strips out the newlines--hence why the actual code uses the
        # "data" element. Except Selenium has no way to read in data element attributes
        self.assertEqual(
            obj_bank_id.get_attribute('value'),
            self.obj_bank_id.replace('\n',''))
        self.assertEqual(
            semester.get_attribute('value'),
            'Spring 2012')
        
        ok_modal_btn = self.browser.find_element_by_partial_link_text('OK')
        ok_modal_btn.click()
        
        modal_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'bootbox')))
        search_wait = WebDriverWait(self.browser, 3).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'search-query')))
                
        self.assertFalse(search_bar.is_displayed())
    
    def delete_activity(self, name):
        """
        Delete the activity with 'name' name
        """
        action_div = self.browser.find_element_by_id('action_div')
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box(name)
                                
        self.assertTrue(action_div.is_displayed())
        add_obj = self.browser.find_element_by_id('add_object')
        add_act = self.browser.find_element_by_id('add_activity')
        del_obj = self.browser.find_element_by_id('delete_object')
        
        self.assertFalse(add_obj.is_displayed())
        self.assertFalse(add_act.is_displayed())
        self.assertTrue(del_obj.is_displayed())
        
        del_obj.click()
        
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
                
        obj_name_modal = self.browser.find_element_by_xpath(
                '//div[@class="bootbox modal fade in"]')
        modal_background = self.browser.find_element_by_class_name('modal-backdrop')

        self.assertTrue(obj_name_modal.is_displayed())
        self.assertTrue(modal_background.is_displayed())       
        
        modal_body = self.browser.find_element_by_class_name('modal-body')
        
        self.assertIn(
            'Delete ' + name + '?',
            modal_body.text)
            
    def delete_objective(self, name):
        """
        Delete the objective with 'name' name
        """
        action_div = self.browser.find_element_by_id('action_div')
        self.assertFalse(action_div.is_displayed())
        
        self.right_click_svg_box(name)
                                
        self.assertTrue(action_div.is_displayed())
        add_obj = self.browser.find_element_by_id('add_object')
        add_act = self.browser.find_element_by_id('add_activity')
        del_obj = self.browser.find_element_by_id('delete_object')
        
        self.assertTrue(add_obj.is_displayed())
        self.assertTrue(add_act.is_displayed())
        self.assertTrue(del_obj.is_displayed())
        
        del_obj.click()
        
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME,'bootbox')))
                
        obj_name_modal = self.browser.find_element_by_xpath(
                '//div[@class="bootbox modal fade in"]')
        modal_background = self.browser.find_element_by_class_name('modal-backdrop')

        self.assertTrue(obj_name_modal.is_displayed())
        self.assertTrue(modal_background.is_displayed())       
        
        modal_body = self.browser.find_element_by_class_name('modal-body')
        
        self.assertIn(
            'Delete ' + name + '?',
            modal_body.text)
    
    def fill_activity_form(self):
        """
        Fill in the session and timetag information for a new video
        """
        session = self.browser.find_element_by_id('class_session')
        recorded_date = self.browser.find_element_by_id('recorded_date')
        pubdate = self.browser.find_element_by_id('pubdate')
        subject_01 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"]/td[2]/input')
        timetag_01 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"]/td[3]/input')
            
        add_row_btn = self.browser.find_element_by_id('add-row')
        
        session.send_keys('Lecture 1')
        recorded_date.send_keys('2013-12-31')
        recorded_date.send_keys(Keys.TAB)
        pubdate.send_keys('2013-12-31')
        pubdate.send_keys(Keys.TAB)
        subject_01.send_keys('Demo 1')
        timetag_01.send_keys('00:01:00')
        
        search_wait = WebDriverWait(self.browser, 3).until(
                EC.element_to_be_clickable((By.ID,'add-row')))
        
        add_row_btn.send_keys(Keys.RETURN)
        
        self.assertTrue(self.check_exists_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[2]/input'))
        self.assertTrue(self.check_exists_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[3]/input'))
        
        subject_02 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[2]/input')
        timetag_02 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[3]/input')
        
        subject_02.send_keys('Demo 2')
        timetag_02.send_keys('00:02:00')
        
        del_row_02 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[1]/i')
        
        del_row_02.click()
        
        self.assertFalse(self.check_exists_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[2]/input'))
        self.assertFalse(self.check_exists_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[3]/input'))
        
        add_row_btn.send_keys(Keys.RETURN)
        
        subject_02 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[2]/input')
        timetag_02 = self.browser.find_element_by_xpath(
            '//form[@id="video_metadata"]/table/tbody/tr[@class="timetag-row"][2]/td[3]/input')
        
        subject_02.send_keys('Demo 2')
        timetag_02.send_keys('00:02:00')
        
        
    
    def fill_activity_form_xml(self):
        """
        Fill in the session and timetag information for a new video via an XML file
        """
        session = self.browser.find_element_by_id('class_session')
        recorded_date = self.browser.find_element_by_id('recorded_date')
        pubdate = self.browser.find_element_by_id('pubdate')
        
        session.send_keys('Lecture 1')
        recorded_date.send_keys('2013-12-31')
        recorded_date.send_keys(Keys.TAB)
        pubdate.send_keys('2013-12-31')
        pubdate.send_keys(Keys.TAB)
        
        file_input = self.browser.find_element_by_id('xml_file')
        file_location = '/Users/cjshaw/Documents/Projects/i2002/3.032/Lecture01/F00038.XML'
        file_input.send_keys(file_location)
        
        process_btn = self.browser.find_element_by_id('process')
        process_btn.send_keys(Keys.RETURN)
        
        click_wait = WebDriverWait(self.browser, 3).until(
                EC.presence_of_element_located((By.ID,'sub_row5')))
                
        
                
        table_body = self.browser.find_element_by_id('table_body')
        rows = table_body.find_elements_by_tag_name('tr')
        expected_offsets = ['00:03:20','00:22:00','00:24:44','00:26:32','00:26:38','00:32:15','00:38:26','00:40:39','00:43:03','00:47:02']
        expected_subjects = ['Administration and Overview','Introduction','Mechanical Behavior','Review','Forces','Moments','Free body diagrams','Equilibrium','Units','Questions']
        expected_rows = 10 # 10 data plus 1 empty
        
        row_count = -1 #start at -1 to take into account the empty header row
        for row in rows:
            if row_count >= 0:
                offset_string = "return $('#tag_row" + str(row_count) + "').val();"
                subject_string = "return $('#sub_row" + str(row_count) + "').val();"
                offset = self.browser.execute_script(offset_string)
                subject = self.browser.execute_script(subject_string)
                
                self.assertEqual(
                        offset,
                        expected_offsets[row_count])
                self.assertEqual(
                        subject,
                        expected_subjects[row_count])
            row_count += 1
        
        self.assertEqual(
                expected_rows,
                row_count)
    
    def open_recently_viewed_with_activities(self):
        """
        Open the recently viewed table
        """
        recently_viewed_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[4]/a[@class="view-recent"]')
        recently_viewed_link.click()
        
        load_wait = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, 'recent_table')))
        
        recent_table = self.browser.find_element_by_id('recent_table')
        tree = self.browser.find_element_by_id('tree')
        
        self.assertTrue(recent_table.is_displayed())
        self.assertFalse(tree.is_displayed())
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn('Recently Viewed', [header.text for header in h2_headers])
        
        table_headers = self.browser.find_elements_by_xpath(
                '//table[@id="recent_table"]/thead/td')
        
        self.assertIn('Views', [header.text for header in table_headers])
        self.assertIn('Video Subject', [header.text for header in table_headers])
    
        table_rows = self.browser.find_elements_by_xpath(
                '//table[@id="recent_table"]/tbody/tr')
        
        self.assertIn('0 test activity', [row.text for row in table_rows])
        self.assertIn('0 test sub activity', [row.text for row in table_rows])
        
    def open_session_tree(self):
        """
        Opens the session tree by clicking on the left-hand nav menu
        """
        session_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[3]/a[@class="view-tree"]')
        session_link.click()
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn('Concept Tree - test class, Spring 2012', [header.text for header in h2_headers])
        
        self.open_session_tree_one_level_with_activities()
        
    def open_session_tree_one_level_with_activities(self):
        """
        Helper function to open the session-based tree one level, with click
        """ 
        svg_id = 'tree_svg'
        load_wait = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, svg_id)))
        session_tree_exists = self.check_exists_by_id(svg_id)
        
        self.assertTrue(session_tree_exists)
        
        self.check_svg_text('test class')
        self.check_svg_text('Lecture 0')
        
        self.check_number_svg_nodes(2)
        
        self.click_svg_box('Lecture 0')
        
        self.check_svg_text('test class')
        self.check_svg_text('Lecture 0')
        self.check_svg_text('test activity')
        self.check_svg_text('test sub activity')
        
        self.check_number_svg_nodes(4)
    
    def open_topic_tree_with_activities(self):
        """
        Open the topic tree
        """
        topic_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[2]/a[@class="view-tree"]')
        topic_link.click()
        
        box_header_id = 'concept-box-header'
        tree_heading = 'Concept Tree - test class, Spring 2012'
        load_wait = WebDriverWait(self.browser, 3).until(
                EC.text_to_be_present_in_element((By.ID, box_header_id), tree_heading))
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn(tree_heading, [header.text for header in h2_headers])
        
        tree = self.browser.find_element_by_id('tree')
        
        self.assertTrue(tree.is_displayed())
        
        self.open_topic_tree_one_level_with_activities()
    
    def open_topic_tree_one_level_with_activities(self):
        """
        Helper function to open the topic-based tree one level, with click
        """ 
        svg_id = 'tree_svg'
        load_wait = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.ID, svg_id)))
        topic_tree_exists = self.check_exists_by_id(svg_id)
        
        self.assertTrue(topic_tree_exists)
        
        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        
        self.check_number_svg_nodes(2)
        
        self.click_svg_box('learning objective')
        
        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        self.check_svg_text('sub learning objective')
        self.check_svg_text('test activity')
        
        self.check_number_svg_nodes(4)
       
    def open_new_admin_tree(self):
        """
        Helper function to open the admin tree one level, with click
        """ 
        svg_id = 'tree_svg'
        load_wait = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, svg_id)))
        topic_tree_exists = self.check_exists_by_id(svg_id)
        
        self.assertTrue(topic_tree_exists)
        
        self.check_svg_text('test class 2')
        
        nodes = self.browser.find_elements_by_class_name('node')

        self.assertTrue(len(nodes) <= 1)
    
    def search_for_activities(self, query_text):
        """
        Helper function to add input to search bar
        """
        search_bar = self.browser.find_element_by_class_name('search-query')
        search_bar.send_keys(query_text)
        return search_bar
        
    #Student helper functions
     
    def student_logs_in(self):
        """
        Helper function that logs the student user into the page
        """
        email_tab = self.browser.find_element_by_link_text('Login with Email')
        email_tab.click()
        
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('student')
        
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('learner')
        password_field.send_keys(Keys.RETURN)
    
    def student_log_in_complete(self):
        """
        Includes navigation to the vcb main page
        """
        self.open('/vcb/')
        
        self.student_logs_in()
            
    def student_login_and_open_recently_viewed_with_activities(self):
        """
        Helper function to log in the student and open the list of recently viewed videos
        """
        self.student_log_in_complete() 
        self.open_recently_viewed_with_activities()
                
    def student_login_and_open_session_tree_with_activities(self):
        """
        Helper function to log in the student and open the session tree
        """
        self.student_log_in_complete() 
        session_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[3]/a[@class="view-tree"]')
        session_link.click()
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn('Concept Tree - test class, Spring 2012', [header.text for header in h2_headers])
        
        self.open_session_tree_one_level_with_activities()
        
    def student_login_and_open_topic_tree_with_activities(self):
        """
        Helper function to log in the student and open the topic tree
        """
        self.student_log_in_complete() 
        self.open_topic_tree_with_activities()
            
    def student_login_and_open_recently_viewed_without_activities(self):
        """
        Helper function to log in the student and open the list of recently viewed videos
        """
        self.student_log_in_complete() 
        self.open_recently_viewed_without_activities()
                
    def student_login_and_open_session_tree_without_activities(self):
        """
        Helper function to log in the student and open the session tree
        """
        self.student_log_in_complete() 
        session_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[3]/a[@class="view-tree"]')
        session_link.click()
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn('Concept Tree - test class, Spring 2012', [header.text for header in h2_headers])
        
        self.open_session_tree_one_level_without_activities()
        
    def student_login_and_open_topic_tree_without_activities(self):
        """
        Helper function to log in the student and open the topic tree
        """
        self.student_log_in_complete() 
        self.open_topic_tree_without_activities()
    
    def open_recently_viewed_without_activities(self):
        """
        Open the recently viewed table
        """
        recently_viewed_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[4]/a[@class="view-recent"]')
        recently_viewed_link.click()
        
        load_wait = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, 'recent_table')))
        
        recent_table = self.browser.find_element_by_id('recent_table')
        tree = self.browser.find_element_by_id('tree')
        
        self.assertTrue(recent_table.is_displayed())
        self.assertFalse(tree.is_displayed())
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn('Recently Viewed', [header.text for header in h2_headers])
        
        table_headers = self.browser.find_elements_by_xpath(
                '//table[@id="recent_table"]/thead/td')
        
        self.assertIn('Views', [header.text for header in table_headers])
        self.assertIn('Video Subject', [header.text for header in table_headers])

        table_rows = self.check_exists_by_xpath(
                '//table[@id="recent_table"]/tbody/tr')
        
        self.assertFalse(table_rows)
        
    def open_session_tree_one_level_without_activities(self):
        """
        Helper function to open the session-based tree one level, with click
        """ 
        svg_id = 'tree_svg'
        load_wait = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, svg_id)))
        session_tree_exists = self.check_exists_by_id(svg_id)
        
        self.assertTrue(session_tree_exists)
        
        self.check_svg_text('test class')
        self.check_svg_text('Lecture 0')
        
        self.click_svg_box('Lecture 0', False)
        
        self.check_svg_text('test class')
        self.check_svg_text('Lecture 0')
        self.check_svg_text_not_present('test activity')
        self.check_svg_text_not_present('test sub activity')
    
    def open_topic_tree_without_activities(self):
        """
        Open the topic tree
        """
        topic_link = self.browser.find_element_by_xpath(
                '//ul[@class="nav"]/li[2]/a[@class="view-tree"]')
        topic_link.click()
        
        h2_headers = self.browser.find_elements_by_tag_name('h2')
        self.assertIn('Concept Tree - test class, Spring 2012', [header.text for header in h2_headers])
        
        tree = self.browser.find_element_by_id('tree')
        
        self.assertTrue(tree.is_displayed())
        
        self.open_topic_tree_one_level_without_activities()
    
    def open_topic_tree_one_level_without_activities(self):
        """
        Helper function to open the topic-based tree one level, with click
        """ 
        svg_id = 'tree_svg'
        load_wait = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, svg_id)))
        topic_tree_exists = self.check_exists_by_id(svg_id)
        
        self.assertTrue(topic_tree_exists)
        
        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        
        self.click_svg_box('learning objective', True) # True because will expand for sub learning obj
        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        self.check_svg_text('sub learning objective')
        self.check_svg_text_not_present('test activity')

    
    def check_svg_text_not_present(self, query_string):
        """
        Helper function to determine if a string of text is NOT in an SVG element
        http://stackoverflow.com/questions/3283310/assert-that-a-webelement-is-not-present
        """
        nodes = self.browser.find_elements_by_class_name('node')
        self.assertFalse(query_string in [node.text for node in nodes])
    
    def log_in_wrong_user(self):
        """
        Navigates to the homepage, tries a wrong login
        """
        self.open('/vcb/')
        
        email_tab = self.browser.find_element_by_link_text('Login with Email')
        email_tab.click()
        
        username = self.browser.find_element_by_name('username')
        username.send_keys('me@name.com')
        
        password = self.browser.find_element_by_name('password')
        password.send_keys('password')
        
        submit = self.browser.find_element_by_id('login')
        submit.click()
        
        error_message = self.browser.find_element_by_class_name('logintxt')
        self.assertIn('Incorrect username and/or password.', error_message.text)
    
    def fill_out_right_registration_info(self):
        """
        A student fills out the right registration information
        """
        fname_field = self.browser.find_element_by_name('fname')
        self.assertEqual(
            fname_field.get_attribute('placeholder'),
            'First Name')
        fname_field.send_keys('A')
        
        lname_field = self.browser.find_element_by_name('lname')
        self.assertEqual(
            lname_field.get_attribute('placeholder'),
            'Last Name')
        lname_field.send_keys('Student')
        
        email_field = self.browser.find_element_by_name('email')
        self.assertEqual(
            email_field.get_attribute('placeholder'),
            'Email')
        email_field.send_keys('me@name.com')
        
        classes = self.browser.find_elements_by_class_name('class_code')
        for oneClass in classes:
            oneClass.send_keys('1.001xxx')
        
        pwd = self.browser.find_element_by_name('passwd')
        self.assertEqual(
            pwd.get_attribute('placeholder'),
            'Password')
        test_passwd = 'password'
        pwd.send_keys(test_passwd)
        
        pwd_conf = self.browser.find_element_by_name('conpasswd')
        self.assertEqual(
            pwd_conf.get_attribute('placeholder'),
            'Re-enter Password')
        pwd_conf.send_keys(test_passwd)
        
        tos = self.browser.find_element_by_name('tos')
        tos.click()
        
        self.check_for_links('Terms of Service')
        self.check_for_links('Privacy Policy')
        
        signup_form = self.browser.find_element_by_tag_name('form')
        signup_form.submit()
        
        self.assertIn('Dashboard', self.browser.title)
        # The right classes that Jane signed up for are listed on the left-hand menu
        
        class_name = self.new_class_session.class_name
        semester = self.new_class_session.semester
        
        class_selector = self.browser.find_element_by_id('s2id_class_selector')
        selected_class = class_selector.find_element_by_class_name('select2-chosen')
        self.assertIn(
            class_name + ', ' + semester,
            selected_class.text)