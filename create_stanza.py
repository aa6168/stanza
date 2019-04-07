#!/usr/bin/env python3
# encoding: utf-8
'''
create_stanza -- Creates stanza file for users.

Created on 4 Apr 2019

@author: Amaurys Ávila Ibarra
'''
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sqlite3
import sys, os

__version__ = 0.1
__date__ = '2019-04-04'
__updated__ = '2019-04-07'
__database__ = "myquotas.db"
__min_python_ver__ = (3, 5)

 
def create_stanza_content(users_limits):
    """
    Create stanza file.
    
    users_limits -- Limits for all users.
    
    return stanza file content
    """
    f_content = []
    for a_dev in users_limits:
        for uname in users_limits[a_dev]:
            limits = users_limits[a_dev][uname]
            blockQuota = "{}{}".format(limits[0], limits[2])
            blockLimit = "{}{}".format(limits[1], limits[2])
            blockGrace = "{}{}".format(limits[3], limits[4])
                                       
            filesQuota = "{}{}".format(limits[5], limits[7])
            filesLimit = "{}{}".format(limits[6], limits[7])
            filesGrace = "{}{}".format(limits[8], limits[9])
            
            f_content.append("%quota:")
            f_content.append("\tdevice={}".format(a_dev))
            f_content.append("\tcommand=setquota")
            f_content.append("\ttype=USR")
            
            f_content.append("\tid={}".format(uname))
            
            f_content.append("\tblockQuota={}".format(blockQuota))
            f_content.append("\tblockLimit={}".format(blockLimit))
            f_content.append("\tblockGrace={}".format(blockGrace))
            
            f_content.append("\tfilesQuotaa={}".format(filesQuota))
            f_content.append("\tfilesLimit={}".format(filesLimit))
            f_content.append("\tfilesGrace={}".format(filesGrace))
            f_content.append("\n")

    return f_content


def create_stanza_file(f_content, fname):
    """
    Create stanza file
    
    f_content -- Content of the stanza file.
    fname -- name of the file.
    """
    
    out_file = open(fname, 'w')
    
    for a_line in f_content:
        out_file.write("{}\n".format(a_line))
    out_file.close()
    
    return


def get_users_limits(ids_usrs, my_cursor):
    """
    Get all limits for users.
    
    ids_usrs -- list of ids and user names.
    my_cursor -- cursor pointing to sqlite database
    
    return limits for all users 
    """
    
    my_limts = {}
    
    for id_usr in ids_usrs:
        my_cursor.execute('''select * from limits where usr_id=?''', (id_usr[0],))
        usr_limits = my_cursor.fetchall()
        for a_lim in usr_limits:
            my_dev = a_lim[0]
            usr_name = id_usr[1]
            
            if my_dev in my_limts:
                my_limts[my_dev][usr_name] = a_lim[2:]
            else:
                my_limts[my_dev] = { usr_name: a_lim[2:]}
    return my_limts


def get_users_ids(my_users, my_cursor):
    """
    Get the users from the command line and find the id of those users from
    the users table.
    
    If we find an user name not in the table stop execution.
    
    my_users -- user name(s) from command line
    my_cursor -- cursor pointing to sqlite database
    
    return a list of user ids.
    """

    my_usr_ids = []
    
    if isinstance(my_users, str) or 'all' in my_users:
        my_cursor.execute('''select id, uname from users''')
        all_ids = my_cursor.fetchall()
        for an_id in all_ids:
            my_usr_ids.append((an_id[0], an_id[1]))
    else:
        for usr_name in my_users:
            my_cursor.execute('''select id from users where uname=?''', (usr_name,))
            usr_id = my_cursor.fetchone()
            if usr_id is None:
                sys.stderr.write("Fatal error: User '{}' is not in the database.\n".format(usr_name))
                sys.exit(4)
            else:
                my_usr_ids.append((usr_id[0], usr_name))

    return my_usr_ids


def main(argv=None):
    '''Command line options.'''

    try:
        assert sys.version_info >= __min_python_ver__
    except Exception as e:
        print("We cannot continue.\nWe need python {}.{} "
              "or greater.\n".format(__min_python_ver__[0],
                                     __min_python_ver__[1]))
        print("We found:")
        print(sys.version)
        print("\n")
        return
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    last_update = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, last_update)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]

    program_longdesc = '''%s

  Created on %s.

  Creates stanza files for user(s)
  use 'all' to create it for all users.
  
  Sqlite database file MUST be in the same directory where the script is 
  executed.


USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_longdesc, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        mandatory_options = parser.add_argument_group('mandatory_args')
        mandatory_options.add_argument("-u", "--user-names", dest="usr_names", help="User(s) name to create stanza file for. [default: %(default)s]", metavar="uname", type=str, nargs='+', default="all")
        mandatory_options.add_argument("-o", "--output-file", dest="out_fname", help="File name for stanza file. [default: %(default)s]", metavar="fname", required=True)

        # Process arguments
        args = parser.parse_args()
        
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    try:
        my_db = sqlite3.connect(__database__)
        my_cursor = my_db.cursor()
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  Fatal error: Could not access database '{}'\n".format(__database__))
        return 3

    my_usrIDs = get_users_ids(args.usr_names, my_cursor)
    
    users_limits = get_users_limits(my_usrIDs, my_cursor)
    
    my_fcontent = create_stanza_content(users_limits)
    
    create_stanza_file(my_fcontent, args.out_fname)

    my_db.close()
    
    return


if __name__ == "__main__":
    # If no arguments is given show help.
    if len(sys.argv) is 1:
        sys.argv.append("-h")
    sys.exit(main())

