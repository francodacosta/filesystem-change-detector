import argparse
import sys
import os
import sqlite3
import hashlib

def error(txt):
    msg("\t ===> ERROR: %s" % txt)

def success(txt):
    msg("\t ===> %s" % txt)

def msg(txt):
    print txt

class FilesystemChangeDetectorCli(object):

    def initDatabase (self, dbPath):
        dbPath=os.path.abspath(dbPath)
        msg("creating database at %s" % dbPath)
        if os.path.isfile(dbPath) :
            error("File exists, please remove it first")
            sys.exit(1)
        conn = sqlite3.connect(dbPath)
        conn.execute('CREATE TABLE meta(version text);')
        conn.execute('INSERT INTO meta (version) VALUES ("0.0.1")')
        conn.execute('CREATE TABLE files (path text unique, crc text, added integer);')
        conn.commit()
        success('created')

        return dbPath

    def addFile(self, file, dbPath):
        dbPath=os.path.abspath(dbPath)
        file=os.path.abspath(file)

        if not os.path.isfile(dbPath) :
            self.initDatabase(dbPath)

        msg("adding file %s" % file )
        if not os.path.isfile(file) :
            error("File does not exist")
            sys.exit(1)

        crc = self.computeCRC(file)
        conn = sqlite3.connect(dbPath)
        conn.execute ('INSERT OR REPLACE INTO files (path, crc) VALUES("%s", "%s")' % (file, crc))
        conn.commit()

        success("%s: %s" %(file, crc))

    def addFolder(self, folder, dbPath):
        fileList = []
        for root, folders, files in os.walk(folder):
            for file in files:
                self.addFile(os.path.join(root, file), dbPath)

    def computeCRC(self, file):
        return hashlib.md5(open(file, 'rb').read()).hexdigest()

    def removeFile(self, file, dbPath):
        dbPath=os.path.abspath(dbPath)
        file=os.path.abspath(file)
        if not os.path.isfile(dbPath) :
            error("FCD database not found (%s)" % dbPath)
            sys.exit(1)

        msg("removing %s from db %s" % (file, dbPath))

        conn = sqlite3.connect(dbPath)
        conn.execute('DELETE FROM files WHERE path="%s"' % file)
        conn.commit()

        success('removed')

    def listFiles(self, dbPath):
        dbPath=os.path.abspath(dbPath)
        if not os.path.isfile(dbPath) :
            error("FCD database not found (%s)" % dbPath)
            sys.exit(1)

        conn = sqlite3.connect(dbPath)
        for file in conn.execute('SELECT * FROM files'):
            success("%s: %s" % (file[0], file[1]))

    def checkKnownFiles(self, dbPath):
        msg('Checking files added to FSC db %s' % dbPath)
        if not os.path.isfile(dbPath) :
            error("FCD database not found (%s)" % dbPath)
            sys.exit(1)

        conn = sqlite3.connect(dbPath)
        filesData = conn.execute('SELECT path, crc from files')
        print

        for data in filesData:
            file = os.path.abspath(data[0])
            dbCrc = data[1]

            if not os.path.isfile(file) :
                error("%s: DELETED" % file)
                continue

            crc = self.computeCRC(file)
            if dbCrc != crc:
                error("%s CRC MISMATCH (%s: %s)" % (file, dbCrc, crc))


    def checkFolder(self, folder, dbPath):
        dbPath=os.path.abspath(dbPath)
        folder=os.path.abspath(folder)

        if not os.path.isfile(dbPath) :
            error("FCD database not found (%s)" % dbPath)
            sys.exit(1)

        msg('checking folder %s ...' %folder)
        conn = sqlite3.connect(dbPath)

        fileList = []
        for root, folders, files in os.walk(folder):
            for file in files:
                fileList.append(os.path.join(root, file))

        success("filesystem has %s files" % len(fileList))

        filesInDb = []
        tmp = conn.execute('SELECT path from files where path like "%s%%"' % folder).fetchall()

        for f in tmp:
            filesInDb.append(f[0])

        success("FCD knows of %s files" % len(filesInDb))
        print ""

        deletedFiles = list(set(filesInDb) - set(fileList))

        for f in deletedFiles:
            error("%s: DELETED" % f)

        for file in fileList:
            cursor = conn.execute('SELECT path, crc from files where path="%s"' % file)
            dbFile = cursor.fetchone()

            if dbFile is None:
                error("%s:  NOT IN DB" % file)
                continue

            dbCrc = dbFile[1]
            crc = self.computeCRC(file)

            if dbCrc != crc:
                error("%s: CRC MISMATCH (%s: %s)" % (file, dbCrc, crc))



parser = argparse.ArgumentParser(description='Filesystem Change Detector')

parser.add_argument('--init',         dest='init_db',      action="store_const", default=False,         const=True, help='creates a new FCD database')
parser.add_argument('--db',           dest='db_path',      action="store",       default='/etc/fsd.db', help='path to the FCD database')
parser.add_argument('--add',          dest='add',          action="store",       default=False,         help='add a file to monitor')
parser.add_argument('--remove',       dest='remove_file',  action="store",       default=False,         help='remove a monitored file from the FCD db')
parser.add_argument('--add-folder',   dest='add_folder',   action="store",       default=False,         help='add a file to monitor')
parser.add_argument('--list',         dest='list',         action="store_const", default=False,         const=True, help='list all files known to FCD')
parser.add_argument('--check-folder', dest='check_folder', action="store",       default=False,         help='check a folder for changed files')
parser.add_argument('--check-all',    dest='check_all',    action="store_const", default=False,         const=True,  help='check a folder for changed files')

options = parser.parse_args()

cli= FilesystemChangeDetectorCli()

print

if options.init_db :
    cli.initDatabase(options.db_path)

elif options.list :
    cli.listFiles(options.db_path)

elif options.add is not False :
    cli.addFile(options.add, options.db_path)

elif options.add_folder is not False :
    cli.addFolder(options.add_folder, options.db_path)

elif options.check_folder is not False :
    cli.checkFolder(options.check_folder, options.db_path)

elif options.remove_file is not False :
    cli.removeFile(options.remove_file, options.db_path)

elif options.check_all is not False :
    cli.checkKnownFiles(options.db_path)
    
else:
    cli.checkKnownFiles(options.db_path)

print
