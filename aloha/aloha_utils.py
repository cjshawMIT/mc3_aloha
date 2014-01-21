import json
import boto
import logging
import pdb
# to create random IDs as backups in case mc3 fails
import string
import random

from django.conf import settings
from django.db.models import Max

from HTMLParser import HTMLParser

from pytz import timezone as py_timezone

from mc3_learning_adapter_py.mc3_http import get_activity_extension, put_activity_extension, get_obj_bank_extension, put_obj_bank_extension

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def add_jumpto(request, url):
    ret_val = url
    try:
        jumpto = request.GET['jumpto']
        objs = request.GET.getlist('objs')
        ret_val += '?jumpto=' + jumpto
        for obj in objs:
            ret_val += '&objs=' + obj
    except:
        ret_val = None
    finally:
        return ret_val

def add_transcript_to_activity(url, act):
    from .models import Transcripts
    new_transcript, created = Transcripts.objects.get_or_create(
        url = url
    )
    act.transcripts.add(new_transcript)

def add_urls_to_activity(url_list, act):
    from .models import Links
    for index, url in enumerate(url_list):
        newlink, created = Links.objects.get_or_create(
            vtype = url['vtype'],
            url = url['url'],
            resolution_order = index + 1
        )
        if 'label' in url:
            newlink.label = url['label']
            newlink.save()
        act.video_urls.add(newlink)

def build_base_share_link(request, course):
    if check_is_touchstone(request):
        base_url = request.build_absolute_uri().split('touchstone/')[0]
        # This is needed for a Touchstone-logout-email-login sequence,
        # because the browser thinks that is_touchstone is True
        if base_url.find('dashboard/'):
            base_url = base_url.split('dashboard/')[0]
    else:
        base_url = request.build_absolute_uri().split('dashboard/')[0]
    if course:
        return base_url + '?jumpto=' + course.obj_bank_id
    else:
        return base_url

def check_is_touchstone(request):
    try:
        touchstone = request.META['REMOTE_USER']
        return True
    except:
        return False

def truncate_name(fullname):
    """
    Used to truncate displayed names in the tree, so they don't run outside of the boxes
    """
    if len(fullname) > 30:
        displayname = fullname[:30] + '...'
    else:
        displayname = fullname
    return displayname

def cap_string(s):
    # From:
    # http://stackoverflow.com/questions/1549641/how-to-capitalize-the-first-letter-of-each-word-in-a-string-python
    return ' '.join(word[0].upper() + word[1:] for word in s.split())

def clean_classnames(dict):
    ret_val = {}
    for key, value in dict.iteritems():
        new_key = cap_string(key.replace('_', ' '))
        ret_val[new_key] = value
        if 'children' in value:
            ret_val[new_key]['children'] = clean_classnames(value['children'])
    return ret_val

def clean_filesizes(dict):
    for key, value in dict.iteritems():
        if 'size' in value:
            dict[key]['size'] = sizeof_fmt(value['size'])
        if 'children' in value:
            dict[key]['children'] = clean_filesizes(value['children'])
    return dict

def clean_html(name):
    parser = HTMLParser()
    return parser.unescape(parser.unescape(name)).replace('<br>','').strip()

def clean_str(input):
    """
    Remove all non-words from a string
    """
    output = re.sub(r'[^\w]', '_', input)
    return output

def construct_group_name(course):
    class_name = course.class_name
    semester = course.semester
    group_name = class_name + ', ' + semester
    return group_name

def construct_init_class(request, handle, videos):
    if handle:
        return {
            'allow_download': handle.allow_download,
            'allow_sharing': handle.allow_sharing,
            'allow_transcripts': handle.allow_transcripts,
            'local_id': handle.pk,
            'metadata': handle.get_full_name(),
            'sharelink': build_base_share_link(request, handle),
            'video': videos
        }
    else:
        return {
            'allow_download': False,
            'allow_sharing': False,
            'allow_transcripts': False,
            'local_id': 0,
            'metadata': {
                'class_name': '',
                'class_number': '',
                'semester': ''
            },
            'sharelink': build_base_share_link(request, None),
            'video': ''
        }

def convert_to_date_only(timestamp):
    try:
        fmt = '%Y-%m-%d'
        return timestamp.strftime(fmt)
    except:
        return timestamp

def convert_to_eastern(timestamp):
    fmt = '%Y-%m-%d, %I:%M %p'
    eastern = timestamp.astimezone(py_timezone('US/Eastern'))
    return eastern.strftime(fmt)
# From
# http://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
def getSec(s):
    l = s.split(':')
    try:
        result = int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])
    except:
        result = int(l[0]) * 3600 + int(l[1]) * 60
    return result

def get_all_classes():
    from .models import Classes
    all_classes = Classes.objects.all()
    class_choices = []
    for one_class in all_classes:
        class_object = {
            'id': one_class.id,
            'class_name': one_class.class_name,
            'class_number': one_class.class_number,
            'semester': one_class.semester,
            'access_code': one_class.access_code,
            'fullname': one_class.class_name + ', ' + one_class.semester
        }
        class_choices.append(class_object)
    return class_choices

def get_class_handle(classname, semester):
    from .models import Classes
    return Classes.objects.get(class_name = classname,
                               semester = semester)

def get_s3_bucket_size(bucket):
    # From:
    # http://www.quora.com/Amazon-S3/What-is-the-fastest-way-to-measure-the-total-size-of-an-S3-bucket
    # http://stackoverflow.com/questions/17375127/how-can-i-get-list-of-only-folders-in-amazon-3-using-python-boto
    # Manually filter out logs and test folders--we don't need to show those to anyone
    c = boto.connect_s3(settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY)
    b = c.lookup(bucket)
    dirs = list(b.list("", "/"))
    ret_val = {}
    for folder in dirs:
        bytes = 0
        files = list(b.list(folder.name, ''))
        blacklist = ['logs', 'test', 'sandbox']
        if not (lambda folder=folder, blacklist=blacklist:
                any(item in folder.name for item in blacklist))():
            logging.info('Finding size of bucket: ' + folder.name)
            for file in files:
                bytes += b.get_key(file).size
            display_name = folder.name.replace('/', '')
            ret_val[display_name] = {
                'size': bytes
            }
    return ret_val

def get_user_classes(user):
    user_classes = user.groups.all()
    all_classes = []
    for user_class in user_classes:
        all_classes.append(user_class.name)
    return all_classes

def get_video_urls(vid):
    video = []
    for url in vid.video_urls.all().order_by('resolution_order'):
        new_obj = {
            'url': str(url.url)
        }
        if url.label:
            new_obj['label'] = url.label
        video.append(new_obj)
    return video

def flatten_contacts_list(contacts):
    ret_obj = []
    for contact in contacts:
        flat = {
            'email': contact.email,
            'fname': contact.first_name,
            'lname': contact.last_name,
            'role': contact.role
        }
        ret_obj.append(flat)
    return ret_obj

def log_error(module, ex):
    template = "An exception of type {0} occurred in {1}. Arguments:\n{2!r}"
    message = template.format(type(ex).__name__, module, ex.args)
    logging.info(message)

def sizeof_fmt(num):
    # Courtesy of:
    # http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def sum_dict_size(my_dict):
    total = 0
    for key, value in my_dict.iteritems():
        total += value['size']
    return total

def text_bean(text):
    """
    To structure a text bean for MC3 with language specifications
    """
    bean = {
        'text': text,
        'scriptTypeId': '15924%3ALatin%40ISO',
        'languageTypeId': '639-2%3AEnglish%40ISO',
        'formatTypeId': 'Text+Formats%3Aplain%40okapia.net'
    }

    return bean

def record_extension_bean(key, value, activity_id):
    """
    To structure a record extension property bean
    """
    record_bean = {
        'value': value,
        'displayName': text_bean(key),
        'description': text_bean(key),
        'displayLabel': text_bean(key),
        'associatedId': activity_id
    }

    return record_bean

def set_class_contacts(handle, contacts):
    from .models import Contacts
    handle.contacts.clear()
    for contact in contacts:
        new_contact, created = Contacts.objects.get_or_create(
            first_name = contact['fname'],
            last_name = contact['lname'],
            email = contact['email'],
            role = contact['role']
        )
        handle.contacts.add(new_contact)

def get_extension(associated_id, bank_id, bean_type):
    """
    Turn an entire extension record into a hashmap
    """
    if (bean_type == "activity"):
        mc3_result = get_activity_extension(associated_id, bank_id)
    elif (bean_type == "bank"):
        mc3_result = get_obj_bank_extension(bank_id)

    json_result = json.loads(mc3_result)

    extension_records = json_result['recordProperties']
    extension = {}

    for record in extension_records:
        key = record['displayName']['text']
        value = record['value']

        if key in extension:
            if type(extension[key]) is list:
                extension[key].append(value)
            else:
                tmp_val = extension[key]
                extension[key] = []
                extension[key].append(tmp_val)
                extension[key].append(value)
        else:
            extension[key] = value
    return extension

def get_extension_raw(associated_id, bank_id, bean_type):
    """
    Get the raw extension record for updating
    """
    if bean_type == "activity":
        mc3_result = get_activity_extension(associated_id, bank_id)
    elif bean_type == "bank":
        mc3_result = get_obj_bank_extension(bank_id)

    json_result = json.loads(mc3_result)

    return json_result

def increment_sequence(new_obj):
    """
    Check the sequence numbers and increment it if needed
    Right now hardcoded for ClassSessions (Dec 16, 2013)
    """
    from .models import ClassSessions
    session_type = new_obj.session_name.split()[0].title()
    try:
        try:
            max_sequence = ClassSessions.objects.filter(
                umbrella_class_id = new_obj.umbrella_class_id
            ).filter(
                session_name__contains = session_type
            ).aggregate(
                Max('sequence_order'))
            previous_sequence = max_sequence['sequence_order__max'] + 1
        except:
            # Not found, which means it is the first one of the session types
            # ASSUMPTION: There will never be more than 1000 of a single
            # session type...if there is, need to make this dynamic. But
            # also have to wonder how you would visualize that
            if session_type == 'Lecture':
                previous_sequence = 1
            elif session_type == 'Review':
                previous_sequence = 1001
            elif session_type == 'Problem':
                previous_sequence = 2001
            elif session_type == 'Lab':
                previous_sequence = 3001
            elif session_type == 'Recitation':
                previous_sequence = 4001
            else:
                previous_sequence = 9999
        finally:
            if not previous_sequence:
                previous_sequence = 0
    except Exception as ex:
        log_error('increment_sequence()', ex)
        previous_sequence = 0
    finally:
        sequence_order = previous_sequence + 1
        new_obj.sequence_order = sequence_order
        new_obj.save()

def parse_click_data(click):
    from .models import MC3Objectives
    display_time = convert_to_eastern(click.timestamp)
    act = click.activity
    obj = MC3Objectives.objects.get(mc3_id = act.mc3_objective_id, is_active=True)
    return {
        'obj': obj.name,
        'tag' : click.activity.subject,
        'timetag': display_time,
        'username': click.user.username
    }

def put_extension_raw(extension_raw, associated_id, bank_id, bean_type):
    """
    PUT the raw extension record for updating
    """
    if (bean_type == "activity"):
        return put_activity_extension(extension_raw, associated_id, bank_id)
    elif (bean_type == "bank"):
        return put_obj_bank_extension(extension_raw, bank_id)

def put_extension(extension_hash, associated_id, bank_id, bean_type):
    """
    Convert a hashmap / dict into an extension bean and upload
    to MC3
    """
    extension_bean = {
        'associatedId': associated_id,
        'recordProperties': []
    }

    for key, value in extension_hash.iteritems():
        extension_bean['recordProperties'].append(
            record_extension_bean(key, value, associated_id))

    if (bean_type == "activity"):
        return put_activity_extension(extension_bean, associated_id, bank_id)
    elif (bean_type == "bank"):
        return put_obj_bank_extension(extension_bean, bank_id)

def user_in_class(user, course):
    group_name = construct_group_name(course)
    return user.groups.filter(name=group_name)

def write_click_to_csv(writer, data):
    writer.writerow([data['username'],
                     data['obj'],
                     data['tag'],
                     data['timetag']])