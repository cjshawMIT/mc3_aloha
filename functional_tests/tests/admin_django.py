# NOTE: Have to disable the Django Debug Toolbar FIRST!
# In settings.py comment out the INTERNAL_IPS or set DEBUG = FALSE
# Abandon for now--assume these work via internal Django tests...
# Failing on setting users to staff. 
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.conf import settings

from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from vcb.test import create_data, clearMC3Bank
from functional_tests.test import SeleniumTestCase

class AdminDjango(SeleniumTestCase):
    def setUp(self):
        User.objects.create_superuser(username='vcb',
                                      password='rock5!',
                                      email='me@name.edu')
        User.objects.create_user(username='teaching',
                                 password='assistant',
                                 email='ta@name.edu')
        result = create_data(0,0, False)
        self.new_class_session = result['new_class_session']
        self.obj_bank_id = self.new_class_session.obj_bank_id
        
        self.browser = webdriver.Chrome(settings.SELENIUM_WEBDRIVER)
        #self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        self.browser.set_page_load_timeout(20)
    
    def tearDown(self):
        clearMC3Bank(self.obj_bank_id)
        self.browser.quit()
        
    def check_for_links(self, link_text):
        """
        Helper function to check links on a page for certain text
        """
        links = self.browser.find_elements_by_tag_name('a')
        self.assertIn(link_text, [link.text for link in links])
    
    def admin_logs_in(self):
        """
        Helper function that logs the admin user into the page
        """
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('vcb')
        
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('rock5!')
        password_field.send_keys(Keys.RETURN)
    
    def admin_log_in_complete(self):
        """
        Includes navigation to the admin page
        """
        self.open('/admin/')
        self.admin_logs_in()
    
    def test_admin_can_login(self):
        """
        Admin user can log into the Django admin interface
        """
        self.open('/admin/')
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('VCB Administration', body.text)
        
        self.admin_logs_in()
        
        # her username and password are accepted, and she is taken to
        # the Site Administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)
    
    def test_admin_page_renders_properly(self):
        """
        The admin page should have at least two fields:
         - Users
         - Classes
        Admins may have to add staff status to users, and they may have to
        adjust the MC3 bank information for a class
        """
        self.admin_log_in_complete()
        
        self.check_for_links('Users')
        self.check_for_links('Groups')
        self.check_for_links('Classess')
    
    def test_admin_can_make_a_user_staff(self):
        """
        Admin users can add staff status to existing users
        """
        self.admin_log_in_complete()
        page_links = self.browser.find_elements_by_tag_name('a')
        
        for link in page_links:
            if link.text == 'Users':
                user_link = link
        
        user_link.click()
        
        headers = self.browser.find_elements_by_tag_name('h1')
        self.assertIn('Select user to change', 
                [header.text for header in headers])
        
        users = self.browser.find_elements_by_xpath('//table[@id="result_list"]/tbody/tr/th/a')
        
        row_count = 1
        for user in users:
            xpath = '//table[@id="result_list"]/tbody/tr[' + str(row_count) + ']/td[5]/img'
            # check first that this user is not a staff
            staff_icon = self.browser.find_element_by_xpath(xpath)
            is_staff = staff_icon.get_attribute('alt')
            
            if is_staff == 'false':
                user.click()
                user_headers = self.browser.find_elements_by_tag_name('h1')
                self.assertTrue('Change user', 
                        [userHeader.text for userHeader in user_headers])
            
                # Are the right fields present in the user's form?
                form_headers = self.browser.find_elements_by_tag_name('h2')
                self.assertIn('Personal info', 
                        [form_header.text for form_header in form_headers])
                self.assertIn('Permissions', 
                        [form_header.text for form_header in form_headers])
                self.assertIn('Important dates', 
                        [form_header.text for form_header in form_headers])
            
                # Form looks properly rendered, now click the 'Staff status'
                # checkbox and submit it
                is_staff_checkbox = self.browser.find_element_by_id('id_is_staff')
                is_staff_checkbox.click()
                # Save the form
                save_btn = self.browser.find_element_by_css_selector('input[value="Save"]')
                save_btn.click()
                # Returns you to the admin page
                message_box = self.browser.find_element_by_class_name('info')
                self.assertIn('successfully', message_box.text)
                
                # Check that staff status changed
                staff_icon = self.browser.find_element_by_xpath('//table[@id="result_list"]/tbody/tr[' + str(row_count) + ']/td[5]/img')
                is_staff = staff_icon.get_attribute('alt')
                self.assertEquals(is_staff, 'true')
            row_count += 1
        log_out = self.browser.find_element_by_link_text('Log out')
        log_out.click()
        
    def test_admin_can_change_a_class_obj_bank_id(self):
        """
        Admin users can change a class's MC3 objective bank id
        """
        self.admin_log_in_complete()
        page_links = self.browser.find_elements_by_tag_name('a')
        
        for link in page_links:
            if link.text == 'Classess':
                classes_link = link
        
        classes_link.click()
        
        headers = self.browser.find_elements_by_tag_name('h1')
        self.assertIn('Select classes to change', 
                [header.text for header in headers])
        
        the_class = self.browser.find_element_by_xpath(
                '//table[@id="result_list"]/tbody/tr[1]/th/a')
        the_class.click()
        
        headers = self.browser.find_elements_by_tag_name('h1')
        self.assertIn('Change classes',
                [header.text for header in headers])
        
        class_number = self.browser.find_element_by_id('id_class_number')
        class_number.send_keys('New Num!')
        
        save_btn = self.browser.find_element_by_css_selector('input[value="Save"]')
        save_btn.click()
        
        message_box = self.browser.find_element_by_class_name('info')
        self.assertIn('successfully', message_box.text)
            
    def test_logging_out_redirects_to_login_page(self):
        """
        Logging out of the admin page should redirect to the main page
        """
        self.admin_log_in_complete()
        log_out = self.browser.find_element_by_link_text('Log out')
        log_out.click()
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('VCB Administration', body.text)