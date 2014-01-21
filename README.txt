Jan 5, 2013
README.txt for foosite
This website allows users to search for video tags from MIT Tech TV.

==================
Installation
==================
* All required Django plugins should be listed in the requirements.txt. I don't know if a virtualenv / pip install will work, since the libraries never link correctly on my machine...

* I tested this with a PostgreSQL database. You will need to modify the settings.py file to match your database configuration.

* For django-csvimport, I had to make one change in the code to make it work properly: line 364 of ./csvimport/management/commands/csvimport.py, I had to put 'utf-8' and 'replace' directly in to the line.encode() arguments instead of pass them in as variables, as in the original code. This should already be changed in the files here, but if you re-install from requirements.txt, not sure if that will get overwritten or if you will have the same problems.

=================
Running the demo
=================
1) You will need to upload a csv file with all of the video "tags" and fields filled out. Example file (for the 2.002 Spring 2012 class) is aggregate3.csv and is included in this folder. This was created as an export from Excel. You can modify this to change tag locations, dates, etc. 
* Required fields are viddate, classnum, videoid, branch, subject, and techtvtimesecs. Others are optional.
* To change where tags show up on the graphical search-tree, you need to change the "branch" field for the row.
* Note: if you open or edit this file in Excel, the three date-related columns will automatically have their formats changed to an unacceptable format. viddate, pub_date, and last_view need to be in yyyy-mm-dd format to import into the database. However, Excel opens them as mm-dd-yy. You can change this by highlighting all the rows, right-click, change to a Custom format, and in the box type "yyyy-mm-dd".

2) Navigate to the foosite/ directory.

3) Run the server $python manage.py runserver

4) Open a browser and go to 127.0.0.1:8000/admin/

5) Log in and click on "Add CSV Import"

6) Under Model name:, pick "tags:Tag"

7) Under Upload file:, select the *.csv file created in step 1)

8) Click "Save" in the bottom right corner...the page should load and think for awhile. When it is completed, you can check that everything went okay by navigating to the csv imports page (127.0.0.1:8000/admin/csvimport/csvimport/) and clicking the new import. Errors will be located in the "Error log html:" section if present.

9) You can now use the search site! Navigate to 127.0.0.1:8000/tags/. A text search box and a visual tree search are both available (not simultaneously). Currently "seek to" does not function, so each video will start at the beginning of the lecture...ideally each tag would seek to the specific timestamp in the video.

10) You can manually change the tags in the /admin interface or drop the table (from an external DB management interface), edit the *.csv file, and repeating the above steps. Note that the second option erases the view counters.
