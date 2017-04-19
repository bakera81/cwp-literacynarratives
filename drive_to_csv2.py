from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import csv
import yaml
import pdb


# FOLDER IDS
with open("folder_ids.yml", 'r') as stream:
    try:
        credentials = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

CWPPRESERVE = credentials['CWPPRESERVE']
ORIGINALS = credentials['ORIGINALS']
WORDDOCS = credentials['WORDDOCS']
TEXTDOCS = credentials['TEXTDOCS']
ARCHIVE = credentials['ARCHIVE']
GOOGLEDOCS = credentials['GOOGLEDOCS']
#folder mimeType: application/vnd.google-apps.folder

def initialize():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def parse_name(filename):
    return filename[filename.rfind('_')+1:filename.rfind('.')]


def parse_year(filename):
    return filename[0:4]


def match_id(data, name, year):
    """ @param data: dict. k=2tuples of id, name; v=2tuples of year, text.
        @param name: string, author name.
        @param year: int (?)
        @return: if an match is found, a tuple of id, name; else False
    """
    print("Attempting to match id...")
    for id_name, year_text in data.items(): # The dict is unordered, which causes tests to fail.
        old_id = id_name[0]
        old_name = id_name[1]
        old_year = year_text[0]

        pdb.set_trace()

        if name == old_name and abs(int(year) - int(old_year)) <= 4: # searching user ids in reverse chronological order may be more accurate
            return (int(old_id), old_name)

    return False


def create_google_docs(drive):
    print("Creating Google Docs...")
    folder_list = [f['id'] for f in drive.ListFile({'q': "'{0}' in parents".format(ARCHIVE)}).GetList() if f['mimeType'] == 'application/vnd.google-apps.folder']
    # for folder in folder_list[]:
    if True:
        folder = folder_list[0]
        # print('title: %s, id: %s' % (file1['title'], file1['id']))
        file_list = drive.ListFile({'q': "'{0}' in parents".format(folder)}).GetList()
        for file1 in file_list:
            try:
                #download as native file extension
                print('Downloading %s, id: %s' % (file1['title'], file1['id']))
                file1.GetContentFile(file1['title'], mimetype=file1['mimeType'])
                #upload as google doc
                print('Uploading %s, id: %s' % (file1['title'], file1['id']))
                file2 = drive.CreateFile({'title': file1['title'], 'parents': [{'kind': 'drive#fileLink', 'id': '0B9f5eskwOURiTjhwOWF4UThVc0E'}]})
                # file2 = drive.CreateFile({'title': file1['title']})
                file2.SetContentFile(file1['title'])
                file2.Upload({'convert': True})
                print('Removing local copy...')
                os.remove(file1['title'])
            except Exception as err:
                print("ERROR in {0}".format(file1['title']))
                print(err)
    print("Done.")


def create_table(drive):
    print("Creating table...")
    output = []

    file_list = drive.ListFile({'q': "'{0}' in parents".format(GOOGLEDOCS)}).GetList()
    for i, file1 in enumerate(file_list):
        try:
            # pdb.set_trace()
            row = {}
            row['id'] = i
            # row['author_id'] =
            row['name'] = parse_name(file1['title'])
            row['year'] = parse_year(file1['title'])
            row['text'] = file1.GetContentString(mimetype = 'text/plain')
        except Exception as err:
            print("Error in {0}".format(file1['title']))
            print(err)

        output.append(row)


    # add author_id
    author_id = 1
    output2 = {} #k=2tuple of author_id, name; v=list of 2tuples of year, text
    for author in output:
        #if name not in author_names:
        if not author['name'] in [t[0] for t in output2.keys()]:
            output2[(author_id, author['name'])] = [(author['year'], author['text'])]
            author_id += 1
        else: #if there is an instance of the name already in the author_ids
            match_result = match_id(output2, author['name'], author['year'])
            if match_result == False: #no suitable match found (user is new)
                output2[(author_id, author['name'])] = [(author['year'], author['text'])]
                author_id += 1
            else: #there is an instance and the author is returning so use the correct id
                output2[match_result].push((author['year'], author['text']))

    return output2


def write_file(data, filename):
    with open(filename, 'w') as csvfile:
        fieldnames = ['id', 'name', 'year', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for id_name, year_text_list in data.items():
            author_id = id_name[0]
            author_name = id_name[1]
            for year_text in year_text_list:
                writer.writerow({'id': author_id,
                                 'name': author_name,
                                 'year': year_text[0],
                                 'text': year_text[1]})


###################
#   UNIT TESTING  #
###################

def test_match_id():
    """
     1. read in CSV of name, year pairs.
     2. generate ids for each.
     3. read in CSV of results, confirm match.
    """
    print("testing match_id()...")
    with open('tests/unit_test_1.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = {}
        for row in reader:
            data[(row['id'], row['name'])] = (row['year'], row['text'])

        pdb.set_trace()

        # TODO 2017 - 2014 is still four years, how are ambiguous cases handled? (it should be marked as ambiguous)
        if match_id(data, 'Anthony', '2011') == (1, 'Anthony') \
            and match_id(data, 'Anthony', '2017') == (3, 'Anthony') \
            and match_id(data, 'Anthony', '2013') == (1, 'Anthony') \
            and match_id(data, 'Anthony',  '2015') == (1, 'Anthony'):
            print("TEST PASSED.")
        else:
            print("TEST FAILED.")

def run_tests():
    test_match_id()


# DataFrame:
###########################
# ID # NAME # YEAR # TEXT #
###########################



#TO DO:
# confirm data types (int vs string)
# consider using a more json like (nested dict) data structure
# use tuple constructor?
# create unit test function
# add error reporting for non-unique year, name keys
# package in an executable







        # author_ids.append((name, id))
        #
        #         fields["author_id"] = str(id)
        #
        #     else: #if there is an instance of the name already in the author_ids
        #         if is_new: #the author is new
        #             author_ids.append((name, id))
        #
        #             fields["author_id"] = str(id)
        #
        #         else: #there is an instance and the author is returning so find the correct id
        #             flag = False
        #             for i in reversed(author_ids):
        #                 if name == i[0]:
        #
        #                     fields["author_id"] = str(i[1])
        #
        #                     flag = True
        #
        #             if not flag:
        #                 print('FAILURE: cannot find ID')


    # output_2 = []
    #create a set of tuples containing (name, year)
    # names_and_years = [(r['name'], r['year']) for r in output]
    #create a dict where k=author_id, v=list of (name, year) tuples
    # authors = {}
    #for i, t in enumerate(names_and_years):
        # keys should be name, year
        #if t[0] in [v for _, v in authors] and t[1] in []
        # if name in author names and year within 4 years
            #add it to the pre-existing key
        #else
            #create a new key
            #authors[i] = [t]




# if not name_in_author_ids: #name_not_in_author_ids:
#         author_ids.append((name, id))
#
#         fields["author_id"] = str(id)
#
#     else: #if there is an instance of the name already in the author_ids
#         if is_new: #the author is new
#             author_ids.append((name, id))
#
#             fields["author_id"] = str(id)
#
#         else: #there is an instance and the author is returning so find the correct id
#             flag = False
#             for i in reversed(author_ids):
#                 if name == i[0]:
#
#                     fields["author_id"] = str(i[1])
#
#                     flag = True
#
#             if not flag:
#                 print('FAILURE: cannot find ID')
#
#
#
#
# file_list = drive.ListFile({'q': "'0B9f5eskwOURiWFpjcFB5elFhUnM' in parents"}).GetList()
# for file1 in file_list:
#     print('title: %s, id: %s' % (file1['title'], file1['id']))
#
# test_file = drive.CreateFile({'title': 'testfile.doc'})
# test_file.SetContentFile('Weinstein_College Writing - literacy narrative - chapter 2.doc')
# test_file.Upload({'convert': True})


#For every file in a given folder (and subfolders):
    #download in native format (.doc or .docx) WHAT ELSE IS SUPPORTED?
    #upload to specified folder as google doc
    #remove local copy

#For every google doc in specific folder:
    #download as plain text
    #write to csv
    #remove local copies

#Upload csv to appropriate location
