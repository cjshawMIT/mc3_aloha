# NOTE: Have to disable the Django Debug Toolbar FIRST!
# In settings.py comment out the INTERNAL_IPS or set DEBUG = FALSE
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from vcb.test import create_data, clearMC3Bank
from functional_tests.test import SeleniumTestCase

import pdb
   
class StudentUsageUnpublishedMC3(SeleniumTestCase):
    def setUp(self):
        self.setup_student_user(1, 0, False)
        
        self.browser = webdriver.Chrome(settings.SELENIUM_WEBDRIVER)
        self.browser.implicitly_wait(10)
    
    def tearDown(self):
        self.browser.quit()
        clearMC3Bank(self.obj_bank_id)
        
    def test_student_can_login(self):
        """
        A student with an account can login
        """
        self.open('/vcb/')
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('OEIT Video Concept Browser', body.text)
        
        self.student_logs_in()
        
        # her username and password are accepted, and she is taken to
        # the Site Administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Video Player', body.text)
    
    def test_dashboard_rendered_properly(self):
        """
        The dashboard has a left-hand nav menu, search bar, video pane, and tree pane
        """
        # After registering, Jane is taken to a dashboard where she sees a 
        # search window at the top left, a navigation menu on the left, 
        # a central video pane, and an empty canvas on the right.
        self.student_log_in_complete()
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
        self.check_for_links('Help')
        self.check_for_links('Logout')
        
        nav_headers = self.browser.find_elements_by_class_name('nav-header')
        
        self.assertIn(
                'TEST CLASS, SPRING 2012',
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
    
    def test_search_box_returns_videos(self):
        """
        Typing into the search box will display matching queries in an autocomplete form
        """
        # Jane types 'activity' into the search box. As she types, a list of 
        # concepts appears in a dropdown list. 
        self.student_log_in_complete()  
        search_bar = self.search_for_activities('activity')
        
        dropdown = WebDriverWait(self.browser, 30).until(
                EC.invisibility_of_element_located((By.XPATH,'//li[@class="ui-menu-item"]')))
        search_status = self.browser.find_element_by_xpath('//span[@role="status"]')
        self.assertIn('No search results.',
                search_status.text)
        
    def test_topic_view_opens_properly(self):
        """
        Clicking the topic view on the lefthand menu opens up a topic-based concept
        tree on the right-hand viewing pane
        """
        # Jane then sees some other options for visualizing the video concepts. She clicks
        # a link in the navigation menu, and the right-hand canvas displays a topic-oriented
        # concept map. She drills down in the map until seeing video concepts. Clicking on
        # one of the tags brings up another video in the central pane with its own metadata.
        self.student_login_and_open_topic_tree_without_activities()

        self.click_svg_box('sub learning objective', False)
        
        self.check_svg_text('test class')
        self.check_svg_text('learning objective')
        self.check_svg_text('sub learning objective')
        self.check_svg_text_not_present('test activity')
        self.check_svg_text_not_present('test sub activity')
    
    def test_session_view_opens_properly(self):
        """
        Clicking the session view on the lefthand menu opens up a session-based
        concept tree on the right-hand viewing pane
        """
        # Jane then clicks on the 'view by session' option in the navigation menu. The 
        # right-hand canvas changes to display the topics by class session (i.e. Lecture 1) 
        # instead of by topics. Again, Jane drills down the tree until she sees video
        # concepts.
        self.student_login_and_open_session_tree_without_activities()
 
    def test_recently_viewed_videos_opens_properly(self):
        """
        Clicking the recently viewed link on the lefthand menu opens up a table
        in the right-hand viewing pane with 10 or less recently viewed videos
        """
        # Jane clicks the last option in the manu for her class--see recently viewed videos.
        # The right-hand canvas is replaced by a table showing the most recently viewed
        # videos and how many views they each have.
        self.student_login_and_open_recently_viewed_without_activities()
        # NOTE: This test will fail currently because pub date not supported in MC3
    
    def test_open_recent_table_when_tree_open(self):
        """
        Opening the recently viewed table after a tree is already open replaces the tree on
        the right-hand pane
        """
        self.student_login_and_open_topic_tree_without_activities()
        self.open_recently_viewed_without_activities()
        # NOTE: This test will fail currently because pub date not supported in MC3
        
    def test_open_tree_when_recent_table_open(self):
        """
        Opening a tree after the recently viewed table is already open replaces the table
        in the right-hand pane
        """
        self.student_login_and_open_recently_viewed_without_activities()
        self.open_topic_tree_without_activities()
        
    def test_help_modal_opens_and_closes(self):
        """
        The Help modal opens on click and closes on exit or blur
        """
        # Jane has some questions about the tool and sees a 'help' button in the menu. She
        # clicks it and is shown a window describing the Video Concept browser and a
        # point of contact at OEIT.
        self.student_log_in_complete()
        class_name = self.new_class_session.class_name
        
        side_nav_menu = self.browser.find_elements_by_class_name('nav-header')
        self.assertTrue(class_name, [nav_header.text for nav_header in side_nav_menu])
                
        # Check the help modal is present but not viewable
        help_modal = self.browser.find_element_by_id('help_modal')
        self.assertFalse(help_modal.is_displayed())
        
        help_link = self.browser.find_element_by_class_name('nav-help')
        help_link.click()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.visibility_of_element_located((By.ID,'help_modal')))
        
        self.assertTrue(help_modal.is_displayed())
        modal_background = self.browser.find_element_by_class_name('reveal-modal-bg')
        self.assertTrue(modal_background.is_displayed())
        
        close_modal_link = self.browser.find_element_by_class_name('close-reveal-modal')
        close_modal_link.click()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.ID,'help_modal')))
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'reveal-modal-bg')))
                
        self.assertFalse(help_modal.is_displayed())
        
        # Repeat but test close by clicking outside of the modal
        help_link.click()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.visibility_of_element_located((By.ID,'help_modal')))
                
        self.assertTrue(help_modal.is_displayed())
        self.assertTrue(modal_background.is_displayed())
        
        builder = ActionChains(self.browser)    
        
        click_outside_modal = builder.move_to_element(modal_background) \
                                     .move_by_offset(-500, -300) \
                                     .click()
        
        click_outside_modal.perform()
        
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.ID,'help_modal')))
        modal_wait = WebDriverWait(self.browser, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME,'reveal-modal-bg')))
                        
        self.assertFalse(help_modal.is_displayed())
    
    def test_student_logout_redirects_to_login_page(self):
        """
        Logging out redirects the student to the login page
        """
        # Satisfied, Jane logs out of the tool.
        self.student_log_in_complete()
        log_out = self.browser.find_element_by_link_text('Logout')
        log_out.click()
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('OEIT Video Concept Browser', body.text)
    
    def test_student_can_modify_selected_classes(self):
        """
        Using the profile page, students can pick new classes or de-enroll from
        existing classes
        """
        result = create_data(0, 0, True, 'class 2', '2.001', '2.001xxx')
        self.second_class_session = result['new_class_session']
        self.second_obj_bank_id = self.second_class_session.obj_bank_id
        
        self.student_log_in_complete()
        
        user_icon = self.browser.find_element_by_class_name('dropdown-toggle')
        user_icon.click()
        
        profile_btn = self.browser.find_element_by_link_text('Profile')
        profile_btn.click()
        
        legends = self.browser.find_elements_by_tag_name('legend')
        self.assertIn('Select Your Classes', [legend.text for legend in legends])
        self.assertIn('Select Classes', [legend.text for legend in legends])
        
        self.assertTrue(self.check_exists_by_id('signup'))
        
        table_headers = self.browser.find_elements_by_tag_name('th')
        
        self.assertIn(
                'Class Name / Number',
                [header.text for header in table_headers])
        self.assertIn(
                'Semester',
                [header.text for header in table_headers])
        self.assertIn(
                'Access Code',
                [header.text for header in table_headers])
        
        self.assertTrue(self.check_exists_by_class_name('class_code'))
        code_box = self.browser.find_elements_by_class_name('class_code')
        code_box[0].clear()
        
        tos = self.browser.find_element_by_id('tos')
        tos.click()
        
        self.check_for_links('Terms of Service')
        self.check_for_links('Privacy Policy')
        
        form = self.browser.find_element_by_id('signup')
        form.submit()
        
        errors = self.browser.find_elements_by_class_name('help-inline')
        self.assertIn(
                'Please put in the code for at least 1 class.', 
                [error.text for error in errors])
        
        code_box[1].send_keys('2.001xxx')
        
        form.submit()
        
        submit_wait = WebDriverWait(self.browser, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'sidebar-nav')))
        
        nav_headers = self.browser.find_elements_by_class_name('nav-header')
        self.assertIn('CLASS 2', [nav_header.text for nav_header in nav_headers])
        
        user_icon = self.browser.find_element_by_class_name('dropdown-toggle')
        user_icon.click()
        
        profile_btn = self.browser.find_element_by_link_text('Profile')
        profile_btn.click()
        
        code_box = self.browser.find_elements_by_class_name('class_code')
        code_box[0].send_keys('1.001xxx')
        
        tos = self.browser.find_element_by_id('tos')
        tos.click()
        
        form = self.browser.find_element_by_id('signup')
        form.submit()
        
        submit_wait = WebDriverWait(self.browser, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'sidebar-nav')))
        
        nav_headers = self.browser.find_elements_by_class_name('nav-header')
        self.assertIn('TEST CLASS', [nav_header.text for nav_header in nav_headers])
        self.assertIn('CLASS 2', [nav_header.text for nav_header in nav_headers])
        
        clearMC3Bank(self.second_obj_bank_id)