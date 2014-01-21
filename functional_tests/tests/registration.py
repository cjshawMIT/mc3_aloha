# NOTE: Have to disable the Django Debug Toolbar FIRST!
# In settings.py comment out the INTERNAL_IPS or set DEBUG = FALSE

from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User

from selenium import webdriver

from vcb.test import create_data, clearMC3Bank
from functional_tests.test import SeleniumTestCase

# Make sure your class inherits from your base class
class Registration(SeleniumTestCase):
    def setUp(self):
        # setUp is where you setup call fixture creation scripts
        # and instantiate the WebDriver, which in turns loads up the browser.
        result = create_data(0,0, False)
        self.new_class_session = result['new_class_session']
        self.new_obj = result['new_obj']
        self.new_sub_obj = result['new_sub_obj']
        self.new_activity = result['new_activity']
        self.new_sub_activity = result['new_sub_activity']
        self.new_session = result['new_session']

        self.obj_bank_id = self.new_class_session.obj_bank_id

        # Instantiating the WebDriver will load your browser
        self.browser = webdriver.Chrome(settings.SELENIUM_WEBDRIVER)
#        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        # Don't forget to call quit on your webdriver, so that
        # the browser is closed after the tests are ran
        self.browser.quit()
        clearMC3Bank(self.obj_bank_id)

    def test_homepage_renders_correctly(self):
        # A student enrolled in 2.002 or equivalent at MIT wants to check out the new
        # Video Concept browser. She navigates to the homepage.
        self.open(reverse('vcb:index'))

        # The student (Jane) checks the page title and header to verify she is at the 
        # right site.
        self.assertIn('OEIT Video Concept Browser', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('OEIT Video Concept Browser', header_text)

        touchstone_div = self.browser.find_element_by_id('touchstone_div')
        self.assertTrue(touchstone_div.is_displayed())

        self.assertTrue(self.check_exists_by_class_name('touchstone-login'))

        email_div = self.browser.find_element_by_id('email_div')
        self.assertFalse(email_div.is_displayed())

        self.check_for_links('Touchstone')
        self.check_for_links('Login with Email')

        email_tab = self.browser.find_element_by_link_text('Login with Email')
        email_tab.click()

        # The login block appears centered on the page and asks Jane to fill in
        # her email and password
        signin_btn = self.browser.find_element_by_id('login')
        email_div = self.browser.find_element_by_id('email_div')
        window_width = self.browser.get_window_size()['width']
        self.assertAlmostEqual(
            (signin_btn.location['x'] + email_div.location['x'])/2,
            window_width / 2,
            delta=100)

        username = self.browser.find_element_by_name('username')
        self.assertEqual(
            username.get_attribute('placeholder'),
            'E-mail')

        password = self.browser.find_element_by_name('password')
        self.assertEqual(
            password.get_attribute('placeholder'),
            'Password')

        # She is invited to login, register, or login via MIT Touchstone
        signin_btn_text = signin_btn.text
        self.assertIn('Sign in', signin_btn_text)

        links = self.browser.find_elements_by_tag_name('a')
        self.check_for_links('Register')
        self.check_for_links('Login via MIT Touchstone')
        self.check_for_links('MIT Office of Educational Innovation and Technology (OEIT).')

    def test_can_click_register_link(self):
        # A student enrolled in 2.002 or equivalent at MIT wants to check out the new
        # Video Concept browser. She navigates to the homepage.
        self.open(reverse('vcb:index'))

        email_tab = self.browser.find_element_by_link_text('Login with Email')
        email_tab.click()

        # Jane creates a new account and supplies her name and contact information
        # She also signs up for 2.002, Mechanics and Materials
        register_link = self.browser.find_element_by_id('register_link')
        register_link.click()
        self.assertIn('Register', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Sign Up For Access', header_text)

    def test_student_can_submit_registration_form(self):
        # A student can use the provided form to register
        self.open(reverse('vcb:register'))

        self.fill_out_right_registration_info()

    def test_wrong_user_login(self):
        self.log_in_wrong_user()

    def test_wrong_class_code(self):

        self.open(reverse('vcb:register'))

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
            oneClass.send_keys('1.001foo')

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

        signup_form = self.browser.find_element_by_tag_name('form')
        signup_form.submit()

        error_message = self.browser.find_element_by_class_name('error')
        self.assertIn(
                'Your class codes is invalid for test class. Please try again.', 
                error_message.text)

    def test_form_validation(self):
        """
        Check form validation. At least one class is required, TOS agreed to,
        e-mail is present, and password / confirmation match
        """
        self.open(reverse('vcb:register'))

        signup_form = self.browser.find_element_by_tag_name('form')
        signup_form.submit()

        errors = self.browser.find_elements_by_class_name('help-inline')
        error_count = 0
        for error in errors:
            error_count += 1

        # 10 because two per input--one is the input field, the second is the
        # error message
        num_expected = 10

        self.assertEqual(
                error_count,
                num_expected)

    def test_duplicate_email(self):
        student = User.objects.create_user(username='student',
                                 password='learner',
                                 email='you@mit.edu')

        self.open(reverse('vcb:register'))

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
        email_field.send_keys('you@mit.edu')

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

        signup_form = self.browser.find_element_by_tag_name('form')
        signup_form.submit()

        error_message = self.browser.find_element_by_class_name('error')
        self.assertIn('E-mail already exists. Please try again.', error_message.text)

    def test_register_after_wrong_login(self):
        """
        Make sure the registration page still comes up if the user tries a wrong login first
        """
        self.log_in_wrong_user()
        register_link = self.browser.find_element_by_id('register_link')
        register_link.click()
        self.assertIn('Register', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Sign Up For Access', header_text)
        self.fill_out_right_registration_info()