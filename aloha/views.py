import datetime
import logging
import pdb
import csv
import time
import hmac
import urllib
import binascii
import json
import pytz
import boto
import re

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.utils.timezone import make_aware
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.views.decorators.cache import never_cache

from hashlib import sha1

from copy import deepcopy

from pytz import timezone, utc

from vcb.models import Classes, ClassMC3Map, MC3Activities, MC3Objectives, ClassSessions, SessionsMC3Map, ObjectiveParentMap, set_obj_bank, Links, Clicks
from vcb.vcb_utils import *

from dlkit.services.learning import LearningManager
from dlkit.services.repository import RepositoryManager
from dlkit.services.type_ import TypeManager
from dlkit.services.osid_errors import NotFound, IllegalState
from dlkit.primitives import Id

@never_cache
def index(request):
    redirect = request.GET.get('next')
    is_touchstone = check_is_touchstone(request)
    state = ''
    # Handle jumpto from the root URL
    try:
        if not redirect:
            if is_touchstone:
                redirect = reverse('vcb:touchstone:dashboard')
            else:
                redirect = reverse('vcb:dashboard')
            redirect = add_jumpto(request, redirect)
            if redirect:
                logging.info('Jumping to ' + redirect)
                return HttpResponseRedirect(redirect)
            else:
                raise KeyError
        else:
            return render(request, 'vcb/index.html', {
                'next':redirect,
                'state': state})
    except:
        if not redirect:
            if is_touchstone:
                redirect = reverse('vcb:touchstone:dashboard')
                # redirect = reverse('vcb:dashboard')
                # Keep this as the touchstone redirect, because
                # we can't clean up the cookie anyways...so if someone
                # tries to log out of Touchstone, they
                # still need to close the browser
                state = 'Note: To log out completely from Touchstone, ' + \
                        'you need to close your browser and delete your cookies.'
            else:
                redirect = reverse('vcb:dashboard')
        return render(request, 'vcb/index.html', {
            'next':redirect,
            'state': state})

@login_required
@user_passes_test(lambda u: u.is_active)
def record_view(request, tag_id):
    # When a user clicks on a video tag, the app records which tag they clicked on
    # returns the information for the video so it can be displayed (i.e. viddate, classnum, 
    #   speaker, branch)
    # ===================
    # updated Feb 9, 2013, cshaw
    #  * adjusted to records last_view in utc time, according to suggestions here:
    #     https://docs.djangoproject.com/en/dev/topics/i18n/timezones/
    # updated Feb 26, 2013, pwilkins
    #  * added 'recorddate' to information panel
    # updated Apr 6, 2013, maby
    # * added click logging via a log file + certificate identification
    # August 2013, cshaw--will need to do this via MC3
    # updated Sept 17, 2013, cshaw
    # * Do NOT use dlkit here. It required knowing the bank id, which would mean
    #        getting all the same information as just getting it locally...
    #
    message = {
        'allow_download': False,
        'allow_sharing': False,
        'allow_transcripts': False,
        "branch": "",
        "classnum": "", 
        "classcode": "",
        'course': '',
        "fullname": "",
        'pubdate': "",
        "recorddate": "",
        'semester': '',
        "sharelink": "",
        "speaker": "",
        "subbranch": "", 
        "subject": "",
        "techtvtimesecs": "",
        "topiccode": "",
        'transcript_url': '',
        "url":"",
        "viddate": "",
        "views": "",
    }
    
    tag_id = urllib.unquote(tag_id).replace(':', '%3A').replace('@','%40')
    bookmark = MC3Activities.objects.get(mc3_id = tag_id)
    bookmark.views += 1
    bookmark.last_view = datetime.datetime.utcnow().replace(tzinfo = utc)
    
    obj = MC3Objectives.objects.get(mc3_id = bookmark.mc3_objective_id)
    session_map = SessionsMC3Map.objects.get(mc3_activity_id = tag_id)
    session = ClassSessions.objects.get(pk = session_map.session_id)
    umbrella_class = Classes.objects.get(pk = session.umbrella_class_id)

    # Return nothing if the user is not part of the class
    if user_in_class(request.user, umbrella_class):
        bank_id = umbrella_class.obj_bank_id
        # put in blank parentId and sessionName since they won't be used
        # Need bankId to update the views and last_view in the extension record

        bookmark.save(bank_id,'','')

        message['allow_download'] = umbrella_class.allow_download
        message['allow_sharing'] = umbrella_class.allow_sharing
        message['allow_transcripts'] = umbrella_class.allow_transcripts
        message['viddate'] = bookmark.viddate
        message['classnum'] = session.session_name
        message['course'] = umbrella_class.class_name
        message['branch'] = obj.name
        message['pubdate'] = convert_to_date_only(bookmark.pub_date)
        message['semester']= umbrella_class.semester
        message['subbranch'] = ''
        message['subject'] = bookmark.subject
        message['speaker'] = bookmark.speaker
        message['recorddate'] = convert_to_date_only(bookmark.recorddate)
        message['views'] = bookmark.views
        message['urls'] = []
        message['techtvtimesecs'] = bookmark.techtvtimesecs

        urls_list = bookmark.video_urls.all().order_by('resolution_order')

        sharelink = build_base_share_link(request, umbrella_class)

        objs = []
        objs.append(bookmark.mc3_id)
        objs.append(obj.mc3_id)
        child = deepcopy(obj)
        found_root = False
        while not found_root:
            try:
                parent = ObjectiveParentMap.objects.get(
                    child_mc3_id = child.mc3_id)
                child = MC3Objectives.objects.get(
                    mc3_id = parent.parent_mc3_id,
                    is_active = True)
                objs.append(child.mc3_id)
            except:
                found_root = True

        objs = objs[::-1] #reverse it

        for obj in objs:
            sharelink += '&objs=' + obj
        if message['allow_sharing']:
            message['sharelink'] = sharelink

        #Add click logging
        username = request.user.username
        if username == '':
            username = 'anonymous'

        try:
            click_log = Clicks.objects.create(user = request.user, activity = bookmark)
            umbrella_class.clicks.add(click_log)
        except:
            pass
            #message['subject'] = 'load failure'
        for obj in urls_list:
            new_obj = {
                'url': str(obj.url)
            }
            if obj.label:
                new_obj['label'] = obj.label
            message['urls'].append(new_obj)
        message['success'] = True
    else:
        message['success'] = False
    return HttpResponse(json.dumps(message, cls = DjangoJSONEncoder),
            mimetype = 'application/json')

def get_client_ip(request):
    # to get the client ip for click logging
    # cshaw Feb 9, 2013
    # from http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
def isInstructor(user):
    return user.groups.filter(name = 'Instructors').count() != 0

@login_required
def draw_tree(request):
    # When the main page is loaded, the visual content map tree needs
    #  to be drawn. The D3.js javascript library is used.
    #  A JSON file with the node information needs to be returned.
    #  In the Tags model, this uses the Branch field to determine what
    #  goes where...trunk (root node) is "3D Continuum Mechanics"

    # first make indexes of each individual lecture / recitation
    # then roll those up into the branches
    # finally connect the branches to the trunk

    # ================
    # updated jan 3, 2013, cshaw
    #  - only 2 levels deep. use a default "root" node that will be 
    #     hidden in the GUI (so really 3 levels). Eliminate the "class"
    #     level
    # updated jan 19, 2013, cshaw
    #  - modified query to only include things whose "pub_date" has passed
    #     so students can only view videos after a certain date / time
    #     NOTE: this means the uploaded video file needs to have the
    #     correct information in the pub_date field
    # updated jan 31, 2013, cshaw
    #  - Semi-redundant view with "Lecture" / class level...
    # updated feb 4, 2013, cshaw
    #  - new tree based on lecture; old tree based on new subbranch attribute
    #     tree[0] will be based on subbranch, tree[1] will be based on lecture
    # updated feb 12, 2013, cshaw
    #  - if user is logged in, they get the full tree without date limitations
    # updated apr 29, 2013, maby
    #	- if authenticated user belongs to 'instructors' group, they get the full tree without date limitations
    #	- added click logging capability
    # major change / update, july 12, 2013 cshaw
    #  - takes two parameters from the AJAX call (in video-app.js):
    #		tree-type = by topic or by class session
    #		class-name = which class the user wants to use (i.e. 2.002, 3.032)
    #  - if user.is_staff(), then let them see the whole tree
    #  - not sure how click logging was implemented here, so might get taken out accidentally?
    # July 23, 2013 cshaw
    #  - For now, if the class name is Chemistry Bridge, link to MC3
    # August 6, 2013, cshaw
    #  - Now 2.002 data is in MC3
    try:
        tree_type = request.GET.get('tree-type' , 'topics')
        classname = request.GET.get('class-name', '')
        semester = request.GET.get('semester', '')
        username = request.user.username
        
        get_all = request.GET.get('get_all', False)
        
        tree = []
        tree.append({
            "children":[],
            "item_class": "root",
            "name":classname,
        })
        
        class_handle = Classes.objects.get(class_name = classname, semester = semester)
        obj_bank_id = class_handle.obj_bank_id
    
        is_class_staff = request.user.is_staff;
        tree[0]['source'] = 'mc3'
        if get_all:
            tree[0]['children'] = json.loads(class_handle.get_entire_class(tree_type, is_class_staff))
        else:
            if tree_type == 'topics':
                tree[0]['children'] = json.loads(class_handle.get_root_objectives())
            elif tree_type == 'session':
                session_nodes = json.loads(class_handle.get_sessions(is_class_staff))
                tree[0]['children'] = session_nodes
        logging.info(username + ' retrieved tree: ' + json.dumps(tree))
    except Exception as ex:
        template = "An exception of type {0} occured in draw_tree. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.info(message)
        tree = message
        logging.info(username + ' had an error in getting tree for ' +
                     classname + ' ' + semester + '.')
    finally:
        return HttpResponse(json.dumps(tree), mimetype='application/json')

def logout_page(request):
    """
    Log users out and re-direct them back to /vcb
     """
    logout(request)
    return HttpResponseRedirect(reverse('vcb:index'))

def login_page(request):
    """
    Log in users, according to 
    https://docs.djangoproject.com/en/dev/topics/auth/default/#auth-web-requests
    """
    username = request.POST['username']
    password = request.POST['password']
    redirect_url = request.POST['next']
    
    user = authenticate(username = username, password = password)
    if user is not None:
        if user.is_active:
            login(request, user)
            if user.is_authenticated():
                if redirect_url.find('/touchstone/') >= 0:
                    redirect_url = redirect_url.replace('/vcb/touchstone/', '/vcb/')
                    
                return HttpResponseRedirect(redirect_url)
            else:
                state = "Login error."
                logging.info('User not authenticated: ' + username)
        else:
            state = "Your account is not active."
            logging.info('Not an active user: ' + username)
    else:
        state = "Incorrect username and/or password."
        logging.info('Incorrect username / password: ' + username)

    return render(request, 'vcb/index.html', {'state' : state,'next':redirect_url})

@login_required
def get_classes(request):
    """
    Get all the classes that the user is a part of
    Used for the administrative form
    """
    users_classes = request.user.groups.values_list('name', flat=True)
    
    class_names = []
    semesters = []
    
    try:
        for one_class in users_classes:
            class_names.append(one_class.split(',')[0].strip())
            semesters.append(one_class.split(',')[1].strip())
    except:
        pass
    
    class_choices = []
    index = 0
    
    try:
        for class_name in class_names:
            semester = semesters[index]
            object = Classes.objects.get(class_name = class_name, semester = semester)
            class_choices.append(object)
            index += 1
    except:
        pass
    
    return HttpResponse(serializers.serialize('json', class_choices), 
            mimetype='application/json')

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_class(request):
    """
    Create a new class (i.e. objective bank), new user group
    Called by the admin template, "Add Class" button
    ==========
    Updates:
    * Sept 16, 2013, cshaw
        * Added semester request--have to check if this semester exists for the class.
            If it does not, then create the class with the specified semester.
            If the semester does exist, then copy everything under this semester and
              create a new class.
    """
    created_class = False
    
    new_class_name = request.GET.get('class_name')
    new_class_number = str(request.GET.get('class_number'))
    old_semester = request.GET.get('old_semester')
    new_semester = request.GET.get('new_semester')
    
    username = request.user.username
    
    logging.info(username + ' attempted to create a new class ' +
                 new_class_name + ', ' + new_semester)
    
    if request.user.is_superuser:
        try:
            old_class = Classes.objects.get(
                    class_name = new_class_name, 
                    class_number = new_class_number,
                    semester = old_semester
            )

            new_class_semester = Classes(
                    class_name = new_class_name, 
                    class_number = new_class_number,
                    semester = new_semester
            )
            
            new_class_semester.save()
            try:
                copy_success = old_class.copy_to(new_class_semester.obj_bank_id)
                if copy_success:
                    group_name = new_class_semester.class_name + ', ' + new_class_semester.semester
                    new_group, created = Group.objects.get_or_create(name = group_name)
                    user = User.objects.get(username = username)
                    user.groups.add(new_group)
                    
                    logging.info(username + ' copied the class ' + new_class_name + ' from ' + \
                            old_semester + ' into a new class for ' + new_semester + '.'
                    )
                    obj_bank_id = new_class_semester.obj_bank_id
                    new_access_code = new_class_semester.access_code
                    message = 'Congratulations, the class was' + \
                            ' successfully copied to a new semester. Your access' + \
                            ' code is: ' + new_access_code
                else:
                    logging.info('Error copying ' + new_class_name + ' from ' + \
                            old_semester + ' into a new class for ' + new_semester + '.'
                    )
                    obj_bank_id = ''
                    message = 'Error copying into a new semester'
            except:
                logging.info('Error creating a new class. New semester exists.')
                message = 'Error: The new semester you entered already exists.'
                obj_bank_id = ''
        except:
            new_class = Classes(
                class_name = new_class_name, 
                class_number = new_class_number,
                semester = old_semester
            )
            new_class.save()
            logging.info('New class ' + new_class.class_name + 
                    ' successfully created by ' + request.user.email + 
                    ' with ID ' + str(new_class.id)
            )
            group_name = new_class.class_name + ', ' + new_class.semester
            new_group, created = Group.objects.get_or_create(name = group_name)
            user = User.objects.get(username = username)
            user.groups.add(new_group)
            obj_bank_id = new_class.obj_bank_id
            new_access_code = new_class.access_code
            message = 'Congratulations, the class was' +  \
                   ' successfully loaded. Your access code is: ' + \
                   new_access_code
    else:
        logging.info(username + ' is not authorized to create classes. Class not created.')
        message = 'Sorry, you are not authorized to create classes. Class not created.'
        obj_bank_id = ''
    
    result = {
        'code': new_access_code,
        'created': created_class,
        'message': message,
        'obj_bank_id': obj_bank_id
    }
    
    return HttpResponse(json.dumps(result), mimetype='application/json')

def register(request):
    """
    To populate the registration form with available classes
    """
    class_choices = Classes.objects.all()

    return render(request, 'vcb/register.html', {'class_choices': class_choices})

def success(request):
    """
    Save user data to database and associate with groups (i.e. classes + semesters)
    """
    
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        passwd = request.POST['passwd']
        
        classes = []
        class_choices = Classes.objects.all()
        for one_class in class_choices:
            code_field = 'class_code' + str(one_class.id)
            user_code = request.POST[code_field]
            expected_code = one_class.access_code

            if user_code != '' and expected_code != user_code:
                return render(request, 'vcb/register.html', 
                        {'class_choices': class_choices,
                         'error': 'Your class codes is invalid for ' + one_class.class_name + \
                                  '. Please try again.' }
                )
            else:
                classes.append(user_code)
        
        if not User.objects.filter(email = email).exists():
            if Classes.objects.filter(access_code__in=classes).exists():
                user = User.objects.create_user(email, email, passwd)
                user.is_active = True
                user.first_name = fname
                user.last_name = lname
                user.save()
                
                picked_classes = Classes.objects.filter(access_code__in=classes)
                for one_class in picked_classes:
                    class_name = one_class.class_name
                    semester = one_class.semester
                    new_name = class_name + ', ' + semester
                    new_group, created = Group.objects.get_or_create(name = new_name)
                    user.groups.add(new_group)
                user = authenticate(username=email, password=passwd)
                login(request, user)
                return HttpResponseRedirect(reverse('vcb:dashboard'))
                
            else:
                class_choices = Classes.objects.all()
                return render(request, 'vcb/register.html', 
                        {'error' : 'One of your class codes is invalid. Please try again.',
                         'class_choices': class_choices,}
                )
        else:
            class_choices = Classes.objects.all()
            return render(request, 'vcb/register.html', 
                    {'error' : 'E-mail already exists. Please try again.', 
                     'class_choices': class_choices,}
            )
            
    return render(request, 'vcb/register.html')

@login_required
@user_passes_test(lambda u: u.is_active)
def pick_classes(request):
    """
    Render the pick_classes template
    """
    class_choices = Classes.objects.all()
    # Handle a jumpto link with tag  
    try:
        jumpto = request.GET['jumpto']
        objs = request.GET.getlist('objs')
    except:
        jumpto = None
        objs = None
    finally: 
        return render(request, 'vcb/pick_classes.html', 
                {'class_choices': class_choices, 
                 'user_classes':'xyz',
                 'jumpto': jumpto,
                 'objs': json.dumps(objs),
                }
        )

def touchstone(request):
    """
    To handle logging in via MIT credentials
    On the first time for logging in, create a local user account and ask for
    classes they want to participate in
    """
    remoteUser = request.META['REMOTE_USER']
    try:
        redirect_url = request.GET['next']
    except:
        redirect_url = reverse('vcb:touchstone:dashboard')
        logging.info('Next not found!')

    if redirect_url.find('/touchstone/') < 0:
        redirect_url = redirect_url.replace('/dashboard/', '/touchstone/dashboard/')
        
    kerberos = remoteUser.split('@')[0]

    cur_user = request.user
    classes_list = cur_user.groups.values_list('name',flat=True)
    user_fname = cur_user.first_name
    if user_fname == '':
        cur_user.first_name = kerberos
        cur_user.save()

    if not classes_list:
        # redirect to a new page asking for their classes
        logging.info('No classes for ' + remoteUser + '. Redirecting to pick_classes.')
        return HttpResponseRedirect(reverse('vcb:touchstone:pick_classes'))
    else:
        logging.info(remoteUser + ' logged in; redirecting to ' + redirect_url + '.')
        return HttpResponseRedirect(redirect_url)

@login_required
@user_passes_test(lambda u: u.is_active)
def class_management(request):
    """
    Returns the management data for a specific class
    This means things like if sharing is allowed,
    is downloading allowed, and who the
    course contacts are
    """
    classname = request.GET['classname']
    semester = request.GET['semester']
    try:
        handle = Classes.objects.get(class_name = classname,
                                     semester = semester,
                                     is_active = True)
        metadata = handle.get_management_data()
    except Exception as ex:
        log_error('class_management()', ex)
        metadata = ''
    finally:
        return HttpResponse(json.dumps(metadata), mimetype='application/json')

@login_required
@user_passes_test(lambda u: u.is_active)
def class_metadata(request):
    """
    Returns the metadata for a specific class
    """
    class_id = request.GET['id']
    handle = Classes.objects.get(pk = class_id)
    metadata = handle.get_full_name()
    
    return HttpResponse(json.dumps(metadata), mimetype='application/json')
    
@login_required
@user_passes_test(lambda u: u.is_active)
def classes_picked(request):
    """
    Save the user's classes into the local database, from pick_classes.html
    """
    user = request.user
    classes = []
    class_choices = Classes.objects.all()
    for one_class in class_choices:
        code_field = 'class_code' + str(one_class.id)
        user_code = request.POST[code_field]
        expected_code = one_class.access_code
        
        if user_code != '' and expected_code != user_code:
            class_choices = get_all_classes()
            all_classes = get_user_classes(request.user)
            return render(request, 'vcb/pick_classes.html', 
                    {'class_choices': class_choices,
                     'user_classes': all_classes,
                     'already_registered': True,
                     'error': 'Your class code is invalid for ' + one_class.class_name + \
                              '. Please try again.' }
            )
        else:
            if expected_code == user_code:
                classes.append(user_code)
                group_name = construct_group_name(one_class)
                new_group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(new_group)

    unpicked_classes = Classes.objects.exclude(access_code__in = classes)
    for one_class in unpicked_classes:
        group_name = construct_group_name(one_class)
        group_obj, created = Group.objects.get_or_create(name = group_name)
        user.groups.remove(group_obj)

    try:
        touchstone = request.META['REMOTE_USER']
        final_url = reverse('vcb:touchstone:dashboard')
    except:
        final_url = reverse('vcb:dashboard')
    finally:
        # Handle a jumpto link with tag
        try:
            jumpto = request.POST['jumpto']
            objs = request.POST['objs']
            final_url += '?jumpto=' + jumpto
            for obj in objs:
                final_url += '&objs=' + obj
        except:
            pass
        finally:
            return HttpResponseRedirect(final_url)
        
@login_required
@user_passes_test(lambda u: u.is_active)
def dashboard(request):
    """
    User dashboard where they can view the classes they are signed up for
    """
    cur_user = request.user
    
    user_classes = request.user.groups.values_list('name', flat=True)
    user_fname = cur_user.first_name
    user_is_superuser = cur_user.is_superuser
    
    all_classes = []
    for user_class in user_classes:
        class_name = user_class.split(',')[0].strip()
        semester = user_class.split(',')[1].strip()
        class_handle = Classes.objects.get(class_name = class_name, semester = semester)
        try:
            first_session = ClassSessions.objects.filter(
                umbrella_class_id = int(class_handle.pk)).order_by(
                'sequence_order')[:1].get()
            acts = SessionsMC3Map.objects.filter(
                session = first_session).values_list(
                'mc3_activity_id', flat=True)
            first_act = MC3Activities.objects.filter(
                mc3_id__in = acts).order_by('sequence_order')[:1].get()
            video = get_video_urls(first_act)
        except:
            video = []
        tmp_obj = construct_init_class(request, class_handle, video)
        all_classes.append(tmp_obj)
    message = ''
    # Handle a jumpto link with tag  
    try:
        try:
            jumpto = request.session['jumpto']
            objs = json.loads(request.session['objs'])
            del request.session['jumpto']
            del request.session['objs']
        except:
            jumpto = request.GET['jumpto']
            objs = request.GET.getlist('objs')
        finally:
            jump_class = Classes.objects.get(obj_bank_id = jumpto)
            group_name = jump_class.class_name + ', ' + jump_class.semester
            if group_name in user_classes:
                act_id = objs[-1]
                act = MC3Activities.objects.get(mc3_id = act_id)
                video = get_video_urls(act)
                init_class = construct_init_class(request, jump_class, video)
            else:
                request.session['jumpto'] = jumpto
                request.session['objs'] = json.dumps(objs)
                message = 'You are not enrolled in that class. ' + \
                          'Please sign up via your profile settings.'
                raise LookupError
    except:
        objs = []
        if len(all_classes) > 0:
            init_class = all_classes[0]
        else:
            init_class = construct_init_class(request, None, None)

    return render(request, 'vcb/dashboard.html', 
            {'init_class': json.dumps(init_class),
             'user_fname' : user_fname, 
             'user_is_superuser': user_is_superuser,
             'objs': json.dumps(objs),
             'message': message}
    )

@login_required
@user_passes_test(lambda u: u.is_staff)
def save_class_management(request):
    contacts = json.loads(request.GET['contacts'])
    allow_download = json.loads(request.GET['allow_download'])
    allow_sharing = json.loads(request.GET['allow_sharing'])
    allow_transcripts = json.loads(request.GET['allow_transcripts'])
    classname = request.GET['classname']
    semester = request.GET['semester']
    try:
        handle = get_class_handle(classname, semester)
        handle.allow_download = allow_download
        handle.allow_sharing = allow_sharing
        handle.allow_transcripts = allow_transcripts
        set_class_contacts(handle, contacts)
        handle.save()
        success = True
        logging.info('For class ' + classname + ', ' + semester)
        logging.info('Saved class contacts: ' + json.dumps(contacts))
        logging.info('Saved download option: ' + allow_download)
        logging.info('Saved sharing option: ' + allow_sharing)
    except Exception as ex:
        log_error('save_class_management()', ex)
        success = False
    finally:
        return HttpResponse(success)

@login_required
def search_videos(request):
    """
    Lookup tool to search the MC3Activities table
    Returns video id, subject
    Modified Jul 24 to search across all of your classes. First try MC3 banks, then locally
    if connection to MC3 fails
    """
    query_string = request.GET.get('term', '')
    class_id = request.GET['id']

    is_class_staff = request.user.is_staff

    class_handle = Classes.objects.get(pk = class_id)
    results = class_handle.search_activities(query_string, is_class_staff)

    return HttpResponse(results, mimetype='application/json')

@login_required
def get_children(request):
    """
    Returns the MC3 children of the specified item--objective, activity, or asset...checks two things:
    1) handcar/services/learning/objectivebanks/{objectiveBankId}/objectives/{objectiveId}/children
    2) handcar/services/learning/objectivebanks/{objectiveBankId}/objectives/{objectiveId}/activities
    
    Both are returned. Activities are returned without the empty 'children' = [] array.
    
    If MC3 fails, will also try the local database.
    The item_id is mc3_id
    """
    parent_id = request.GET.get('item_id')
    bank_id = request.GET.get('bank')
    itemClass = request.GET.get('itemClass')

    logging.info('here in get_children view')

    umbrella_class = Classes.objects.get(obj_bank_id = bank_id)
    if user_in_class(request.user, umbrella_class):
        is_class_staff = request.user.is_staff

        if itemClass == 'session':
            session_handle = ClassSessions.objects.get(id = parent_id)

            children = json.loads(session_handle.get_activities(bank_id, is_class_staff))
        elif itemClass == 'objective':
            try:
                objective_handle = MC3Objectives.objects.get(mc3_id = parent_id)
                logging.info('Objective present locally.')
                children = json.loads(objective_handle.get_children(bank_id, is_class_staff))
            except:
                # Since this node doesn't exist locally, it must be an MC3 node.
                # So get the name and type from MC3, then store it locally before
                # calling get_children
                try:
                    source_bank = set_obj_bank(bank_id)
                    mc3_unpickled = pickle.loads(parent_id.encode('latin1'))

                    obj_result = source_bank.get_objective(mc3_unpickled)

                    objective_name = obj_result.display_name.text
                    objective_type = obj_result.genus_type

                    objective_handle = MC3Objectives(
                            name = objective_name,
                            obj_type = objective_type,
                            mc3_id = parent_id
                    )

                    objective_handle.save(bank_id)
                    logging.info('Attempted to read objective ' + parent_id +
                            ', but not present in local database, so created it.')
                    children = json.loads(objective_handle.get_children(bank_id, is_class_staff))
                except:
                    logging.info('Objective does not exist locally or in MC3. No children.')
                    children = []
        else:
            children = []
    else:
        children = []
    return HttpResponse(json.dumps(children), mimetype='application/json')

@login_required
def get_class_sessions(request):
    """
    Gets the class session labels available in the local database for the 
    relevant umbrella class
    First, search Classes for the class ID given the classname
    Second, search ClassSessions for the session_name s for that class ID
    """
    classname = request.GET.get('classname', '' )
    semester = request.GET.get('semester', '')

    class_handle = Classes.objects.get(class_name = classname, semester = semester)

    try:
        sessions = ClassSessions.objects.filter(umbrella_class_id = int(class_handle.id)).order_by('sequence_order')
    except ClassSessions.DoesNotExist:
        sessions = []

    session_name_array = []
    
    for session in sessions:
        session_name_array.append(session.session_name)
    
    return HttpResponse(json.dumps(session_name_array), mimetype='application/json')	

def parse_urls(node_url):
    """
    Create a url_list for the Links model, from the input url
    """
    url_list = []
    if node_url.find('.m3u8') >= 0:
        tmp = {
            'vtype': 'hls',
            'url': node_url
        }
        url_list.append(tmp)
        # THIS IS BRITTLE!
        # RECONSTRUCT THE MP4 ONES FROM M3U8
        # Assumes the format in create_transcoder_job
        filename = node_url.split('/')[-1]
        filename_clean = filename.split('.m3u8')[0]
        vid320 = node_url.replace(filename, '') \
                         .replace('http://', 'https://') \
                         + 'mp4/' \
                         + filename_clean + '/320_' \
                         + filename.replace('.m3u8', '.mp4')
        vid480 = vid320.replace('320', '480p')
        vid1080 = vid320.replace('320', '1080p')

        tmp320 = {
            'vtype': 'mp4',
            'url': vid320,
            'label': '320x240'
        }

        tmp480 = {
            'vtype': 'mp4',
            'url': vid480,
            'label': '480p'
        }

        tmp1080 = {
            'vtype': 'mp4',
            'url': vid1080,
            'label': '1080p'
        }
        url_list.append(tmp1080)
        url_list.append(tmp480)
        url_list.append(tmp320)
    elif node_url.find('.mp4') >= 0:
        tmp = {
            'vtype': 'mp4',
            'url': node_url
        }
        url_list.append(tmp)
    else:
        tmp = {
            'vtype': 'generic video',
            'url': node_url
        }
        url_list.append(tmp)
    return url_list

@login_required
def update_map(request):
    """
    Creates new objectives and video activities in MC3
    """
    children_json = request.POST['children']
    children_array = json.loads(children_json)
#    pdb.set_trace()
    classname = request.POST['classname']
    semester = request.POST['semester']
    mc3_result = ''
    all_okay = True
    message = ''
    username = request.user.username
    
    parent_id = 'root'
    try:
        umbrella_class = Classes.objects.get(class_name = classname, semester = semester, is_active = True)
        umbrella_class_id = umbrella_class.id
        bank_id = umbrella_class.obj_bank_id
    except:
        umbrella_class_id = ''
    
    def parse_children(child_node, parent_id, message):
        node_source = child_node['source']
        node_class = child_node['item_class']
        node_is_active = child_node['is_active']
        node_id = child_node['id']
        node_name = clean_html(child_node['name'])
        node_seq_order = child_node['sequence_order']
        new_message = ''
        
        if node_source != 'user':
            # This node already exists, update its information
            try:
                raise Exception('No children in MC3. Trying local db.')
                # for now don't do anything to MC3 ones...no authorization 
                # implementation yet
            except:
                if node_class == 'objective':
                    obj = MC3Objectives.objects.get(mc3_id = node_id)
                    obj.is_active = node_is_active
                    obj.name = node_name
                    obj.sequence_order = node_seq_order
                    obj.save(bank_id)
                elif node_class == 'asset':
                    act = MC3Activities.objects.get(mc3_id = node_id)
                    act.is_active = node_is_active
                    act.subject = node_name
                    act.sequence_order = node_seq_order
                    act.save(bank_id, umbrella_class_id, '')

                    old_urls = act.video_urls.all().values_list('url', flat=True)
                    new_url = child_node['url']
                    if new_url != '':
                        if new_url not in old_urls:
                            old_url_list = act.video_urls.all()
                            for old_url in old_url_list:
                                act.video_urls.remove(old_url)
                            url_list = parse_urls(new_url)
                            add_urls_to_activity(url_list, act)

        else:
            if node_is_active: # only make the node if it is active
                if (node_class == 'objective'):
                    try:						
                        local_objective = MC3Objectives(
                                name = node_name,
                                obj_type = 'mc3-objective%3Amc3.learning.topic%40MIT-OEIT',
                                sequence_order = node_seq_order)
                        
                        local_objective.save(bank_id)
                        new_local_obj_id = local_objective.mc3_id
                        child_node['id'] = new_local_obj_id
                        
                        if parent_id == 'root':
                            local_mapping, map_created = ClassMC3Map.objects.get_or_create(
                                    umbrella_class_id = umbrella_class_id, 
                                    mc3_objective_id = local_objective.mc3_id
                            )
                            
                            if map_created:
                                logging.info(username + 
                                        ' successfully mapped objective ' + node_name + 
                                        ' to MC3')
                                new_message = 'Successfully mapped objective ' + \
                                        node_name + ' to MC3; '
                            else:
                                logging.info(username +
                                        ' could not map the objective to MC3' +
                                        ' because it is already mapped.')
                                all_okay = False
                                new_message = 'Failed: did not map objective to MC3; '
                        else:
                            new_parent_map = ObjectiveParentMap(
                                    parent_mc3_id = parent_id,
                                    child_mc3_id = new_local_obj_id
                            )
                            
                            new_parent_map.save(bank_id)
                            logging.info(username + 
                                    ' successfully mapped objective ' + node_name + 
                                    ' to parent locally')
                            new_message = 'Successfully mapped objective ' + node_name + \
                                    ' to parent locally; '
                                    
                        new_message += 'Saved objective ' + node_name + '; '
                    except:
                        logging.info(username + 
                                ' could not create objective ' + node_name)
                        all_okay = False
                        new_message = 'Failed: did not create objective ' + node_name + '; '
                elif (node_class == 'asset'):
                    node_url = child_node['url']
                    node_transcript = child_node['transcript_url']
                    node_timetag = child_node['timetag']
                    node_pubdate = child_node['pubdate']
                    recorddate = child_node['recorddate']
                    session_name = child_node['session']
                    
                    # from http://stackoverflow.com/questions/699570/python-testing-for-unicode-and-converting-to-time
                    # need to convert the pubdate and recorddate variables for Django
                    django_pubdate = make_aware(datetime.datetime.strptime(node_pubdate, "%Y-%m-%d"), pytz.utc)
                    django_recorddate = make_aware(datetime.datetime.strptime(recorddate, "%Y-%m-%d"), pytz.utc)
                    
                    # now save the activity locally
                    try:
                        techtvtimesecs = getSec(node_timetag)
                        new_activity = MC3Activities(
                                mc3_objective_id = parent_id, 
                                viddate = recorddate, 
                                recorddate = recorddate, 
                                subject = node_name, 
                                speaker = '', 
                                roughtime = techtvtimesecs,
                                techtvtime = techtvtimesecs,
                                techtvtimesecs = techtvtimesecs, 
                                views = 0, 
                                pub_date = django_pubdate, 
                                last_view = django_pubdate,
                                sequence_order = node_seq_order
                        )
                        new_activity.save(bank_id, parent_id, session_name)
                        url_list = parse_urls(node_url)
                        add_urls_to_activity(url_list, new_activity)
                        add_transcript_to_activity(node_transcript, new_activity)
                        new_id = new_activity.mc3_id
                        logging.info(username + ' successfully created a new ' +
                                'Activity, ' + node_name + ' locally')
                        new_message = username + ' successfully created new activity ' + \
                                node_name + ' locally; '
                    except Exception as ex:
                        template = "An exception of type {0} occured in update_map (when managing urls). "
                        template += "Arguments:\n{1!r}"
                        message = template.format(type(ex).__name__, ex.args)
                        logging.info(message)				
                        new_id = ''
                        logging.info(username + ' failed to create a new ' +
                                'Activity, ' + node_name + ' locally')
                        all_okay = False
                        new_message = username + ' failed to create new activity ' + \
                                node_name + ' locally; '
                    try:
                        new_session, created = ClassSessions.objects.get_or_create(
                                umbrella_class_id = int(umbrella_class_id), 
                                session_date = django_recorddate, 
                                session_name = session_name
                        )
                        if created:
                            increment_sequence(new_session)
                            logging.info(username + ' succesfully created a new Class Session '
                                    + session_name + ' in local database')	
                            new_message += username + ' successfully created a new Class Session ' + \
                                    session_name + ' locally; '
                                    
                        new_session_id = new_session.id
                        new_mc3_map, created = SessionsMC3Map.objects.get_or_create( 
                                session_id = int(new_session_id), 
                                mc3_activity_id = new_id 
                        )
                        if created:
                            logging.info(username + ' successfully mapped activity ' + node_name + \
                                    ' to ' + session_name + ' in local database')	
                            new_message += username + ' successfully mapped activity ' + node_name + \
                                    ' to ' + session_name + ' locally; '
                    except:
                        logging.info(username + ' failed to create a new Class Session ' +
                                session_name + ' in local database')
                        all_okay = 'False'	
                        new_message += username + ' failed to create a new Class Session ' + \
                                session_name + ' locally; '
                    return new_message
                else:
                    pass
                                        
        if 'children' in child_node:
            if child_node['children'] is not None:
                grandchildren = child_node['children']
                new_parent_id = child_node['id']
                for grandchild in grandchildren:
                    message = message + parse_children(grandchild, new_parent_id, new_message)
        return message + new_message
    
    if (umbrella_class_id == ''):
        all_okay = False
        message = 'No new objectives or topics added.'
    else:
        for node in children_array:
            message = parse_children(node, parent_id, message)
    
    result = {
        'all_okay': all_okay,
        'message': message
    }
    return HttpResponse(json.dumps(result), mimetype='application/json')
    
@login_required
def recent(request):
    """
    Page that returns the 10 most recently viewed videos for a given user
    """
    classname = request.GET.get('class-name', '')
    semester = request.GET.get('semester','')
    
    class_handle = Classes.objects.get(class_name = classname,
                                       semester = semester,
                                       is_active = True)

    recent = class_handle.viewed_recently(request.user)
    
    return HttpResponse(json.dumps(recent), mimetype='application/json')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def clickLog(request):
    """
    Provide click log for download if logged in as a superuser
    """
    try:
        class_id = request.GET['id']
        download = json.loads(request.GET['download'])
        include_staff = json.loads(request.GET['include_staff'])
        class_handle = Classes.objects.get(pk = class_id)
        click_log = class_handle.clicks.all()

        if download:
            timestamp = datetime.datetime.now(utc)
            display_time = convert_to_eastern(timestamp)
            response = HttpResponse(content_type='text/tsv')
            response["Content-Disposition"] = "attachment; filename=clickLog_" + \
                                              clean_str(class_handle.class_name) + "_" + \
                                              clean_str(class_handle.semester) + "_" + \
                                              clean_str(display_time) + ".tsv"
            writer = csv.writer(response, delimiter='\t')
            writer.writerow(['Username', 'Objective', 'Activity Tag', 'Timestamp'])

            for click in click_log:
                data = parse_click_data(click)
                if include_staff:
                    write_click_to_csv(writer, data)
                else:
                    if not click.user.is_staff:
                        write_click_to_csv(writer, data)
        else:
            result = []
            for click in click_log:
                if include_staff:
                    result.append(parse_click_data(click))
                else:
                    if not click.user.is_staff:
                        result.append(parse_click_data(click))
            success = True
            result_data = {
                'data': result,
                'success': success
            }
            response = HttpResponse(json.dumps(result_data), mimetype="application/json")
    except Exception as ex:
        template = "An exception of type {0} occured in clickLog. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.info(message)
        response = HttpResponse('Failed to load file.')
    finally:
        return response

@login_required
def signS3put(request):
#	"""
#	To provide a temporary S3 PUT authorization
#	http://codeartists.com/post/36892733572/how-to-directly-upload-files-to-amazon-s3-from-your
#	https://github.com/yaniv-aknin/django-s3upload
#	"""
    s3_bucket_name = settings.S3_BUCKET_NAME
    s3_access_key = settings.S3_ACCESS_KEY
    s3_secret_key = settings.S3_SECRET_KEY

#    # https://devcenter.heroku.com/articles/s3-upload-python
    object_name = request.GET.get('s3_object_name').lower()
    mime_type = request.GET.get('s3_object_type')

    # fix for transcripts:
    if object_name.find('.vtt') >= 0:
        s3_bucket_name = settings.OUTPUT_BUCKET
        mime_type = 'text/vtt'
        cloudfront = 'https://d2f0wfr3cvoae4.cloudfront.net/%s' % (object_name)
    else:
        filename = object_name.split('/')[-1].lower().replace('mov', 'm3u8')
        classname = object_name.split('/')[0]
        cloudfront = 'https://d2f0wfr3cvoae4.cloudfront.net/%s/%s' % (classname, filename)

    expires = int(time.time()+1500)
    amz_headers = "x-amz-acl:public-read"

    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, s3_bucket_name, object_name)
    
    hashed = hmac.new(s3_secret_key, put_request, sha1)
    signature = binascii.b2a_base64(hashed.digest())
    signature = urllib.quote_plus(signature.strip()).replace('=','%3D').replace('+', '%2B').replace('/', '%2F')
    
    url = 'https://s3.amazonaws.com/%s/%s' % (s3_bucket_name, object_name)

    signed_request = '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, s3_access_key, expires, signature)

    return HttpResponse(json.dumps({
        'signed_request': signed_request,
         'url': url,
         'cloudfront': cloudfront
      }), mimetype='application/json')

@login_required
def create_transcoder_job(request):
#	"""
#	To provide a temporary Amazon Transcoder POST authorization
#	http://docs.aws.amazon.com/elastictranscoder/latest/developerguide/create-job.html
#   http://docs.pythonboto.org/en/latest/ref/boto.html
#	"""
    try:
        username = request.user.username
        output_bucket = settings.OUTPUT_BUCKET
        transcoder_endpoint = settings.TRANSCODER_ENDPOINT
        s3_access_key = settings.S3_ACCESS_KEY
        s3_secret_key = settings.S3_SECRET_KEY
    
        pipeline = settings.PIPELINE_ID
        hls_2m = settings.HLS_2M
        hls_1m = settings.HLS_1M
        hls_400k = settings.HLS_400K
        mp4_1080p = settings.MP4_1080P
        mp4_480p_43 = settings.MP4_480P_43
        mp4_320x240 = settings.MP4_320X240
        
        success = False
        connection = boto.connect_elastictranscoder(s3_access_key, s3_secret_key)
        
    #    # https://devcenter.heroku.com/articles/s3-upload-python
        input_file = request.POST['input_file'].lower()
        
        input = {
            'Key': input_file
        }
        
        outputs = []
        hls_presets = [hls_2m, hls_1m, hls_400k]
        hls_tags = ['2m', '1m', '400k']        
        filename_raw = input_file.split('/')[-1].lower().replace('.mov', '')
        class_raw = input_file.split('/')[0]
        
        output_keys = []
        
        for index, hls in enumerate(hls_presets):
            res = hls_tags[index]
            o_file = 'hls/' + filename_raw + '/' + res + '/' + res + '_' + filename_raw
            output = {
                'Key': o_file,
                'PresetId': hls,
                'ThumbnailPattern': 'hls/' + filename_raw + '/' + res + '/' + res + '_' + filename_raw + '-{count}',
                'SegmentDuration': '10'
            }
            output_keys.append(o_file)
            
            outputs.append(output)
        playlist = {
            'Format': 'HLSv3',
            'Name': filename_raw,
            'OutputKeys': output_keys
        }
        playlists = [playlist]
        
        mp4_presets = {
            '1080p': mp4_1080p,
            '480p': mp4_480p_43,
            '320': mp4_320x240
        }
        
        for res, mp4 in mp4_presets.iteritems():
            o_file = 'mp4/' + filename_raw + '/' + res + '_' + filename_raw + '.mp4'
            output = {
                'Key': o_file,
                'PresetId': mp4,
                'ThumbnailPattern': 'mp4/' + filename_raw + '/' + res + '/' + res + '_' + filename_raw + '-{count}'
            }
            
            outputs.append(output)
        
        output_prefix = class_raw + '/'
        
        results = connection.create_job(pipeline, input, None, outputs, output_prefix, playlists)
        
        logging.info(username + ' successfully created HLS and MP4 Elastic Transcoder jobs.')
        logging.info(results)
        success = True
    except Exception as ex:
        template = "An exception of type {0} occured in create_transcoder_job. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.info(message)
        logging.info(username + ' had an error while creating the Elastic Transcoder jobs.')
    finally:
        return HttpResponse(success, mimetype='text/plain')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def get_s3_size(request):
    input_folders = get_s3_bucket_size(settings.S3_BUCKET_NAME)
    output_folders = get_s3_bucket_size(settings.OUTPUT_BUCKET)
    ret_val = {
        'Input bucket': {
            'children': input_folders,
            'size': sum_dict_size(input_folders)
        },
        'Output bucket': {
            'children': output_folders,
            'size': sum_dict_size(output_folders)
        }
    }
    ret_val = clean_filesizes(ret_val)
    ret_val = clean_classnames(ret_val)

    return HttpResponse(json.dumps(ret_val), mimetype='application/json')

def privacy(request):
    """
    Redirect to the site's Privacy Policy
    """
    return render(request, 'vcb/privacy.html')

@login_required
def profile(request):
    """
    Allow users to manage their own classes and access codes
    """
    class_choices = get_all_classes()
    all_classes = get_user_classes(request.user)
    
    return render(request, 'vcb/pick_classes.html', 
            {'class_choices': class_choices,
             'user_classes': all_classes,
             'already_registered': True}
    )

def tos(request):
    """
    Redirect to the site's Terms of Service
    """
    return render(request, 'vcb/tos.html')

@login_required
@user_passes_test(lambda u: u.is_active)
def user_classes(request):
    """
    Return a user's class choices along with the first video links for each
    """
    user_classes = request.user.groups.values_list('name', flat=True)
    
    all_classes = []
    
    for user_class in user_classes:
        class_name = user_class.split(',')[0].strip()
        semester = user_class.split(',')[1].strip()
        class_handle = Classes.objects.get(class_name = class_name, semester = semester)
        try:
            first_session = ClassSessions.objects.filter(umbrella_class_id = int(class_handle.pk))[:1].get()
            acts = SessionsMC3Map.objects.filter(session = first_session).values_list('mc3_activity_id', flat=True)
            first_act = MC3Activities.objects.filter(mc3_id__in = acts).order_by('sequence_order')[:1].get()
            video = get_video_urls(first_act)
        except:
            video = []
        tmp_obj = construct_init_class(request, class_handle, video)
        all_classes.append(tmp_obj)
    
    return HttpResponse(json.dumps(all_classes, cls = DjangoJSONEncoder), 
            mimetype = 'application/json')

