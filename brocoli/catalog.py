import os
import shutil
from datetime import datetime

from six import print_


class Catalog(object):
    """
    Base class for catalog objects. All methods have to be overridden by
    sub-classes.
    """
    def lstat(self, path):
        """
        Returns a dictionary of informations about specified path.
        """
        raise NotImplementedError

    def listdir(self, path):
        """
        Returns directory contents (only filenames, not absolute paths).
        """
        raise NotImplementedError

    def isdir(self, path):
        """
        Returns wether the specified path is a directory.
        """
        raise NotImplementedError

    def join(self, *args):
        """
        Performs the equivalent of os.path.join() in the context of the
        Catalog object.
        """
        raise NotImplementedError

    def download_files(self, pathlist, destdir):
        """
        Downloads files from the catalog pathlist to local destdir.
        """
        raise NotImplementedError

    def download_directories(self, pathlist, destdir):
        """
        Downloads directories contents to local destdir.
        """
        raise NotImplementedError

    def upload_files(self, files, path):
        """
        Uploads local files to catalog destination path (a directory).
        """
        raise NotImplementedError

    def upload_directories(self, dirs, path):
        """
        Uploads local directories content to catalog destination path (a
        directory).
        """
        raise NotImplementedError

    def delete_files(self, files):
        """
        Deletes catalog files.
        """
        raise NotImplementedError

    def delete_directories(self, directories):
        """
        Recusively deletes catalog directories.
        """
        raise NotImplementedError

    def mkdir(self, path):
        """
        Creates a new catalog directory.
        """
        raise NotImplementedError

    @classmethod
    def config_fields(cls):
        """
        Returns a dictionary of form.FormField objects for catalog object
        configuration.
        """
        raise NotImplementedError

class OSCatalog(Catalog):
    """
    Presents contents from local filesystem. Useful for debugging.
    """
    def lstat(self, path):
        stats = os.lstat(path)

        ret = {}

        ret['user'] = stats.st_uid
        ret['size'] = stats.st_size
        ret['mtime'] = datetime.fromtimestamp(stats.st_mtime)

        return ret

    def listdir(self, path):
        return os.listdir(path)

    def isdir(self, path):
        return os.path.isdir(path)

    def join(self, *args):
        return os.path.join(*args)

    def download_files(self, pathlist, destdir):
        number = len(pathlist)
        i = 0
        for path in pathlist:
            shutil.copy2(path, destdir)
            i += 1
            yield i, number

    def download_directories(self, pathlist, destdir):
        number = len(pathlist)
        i = 0
        for path in pathlist:
            # shutil.copytree needs a fresh new destination directory
            ddir = os.path.join(destdir, os.path.basename(path))
            if os.path.exists(ddir):
                shutil.rmtree(ddir)
            shutil.copytree(path, ddir)
            i += 1
            yield i, number

    def upload_files(self, files, path):
        number = len(files)
        i = 0
        for f in files:
            shutil.copy2(f, path)
            i += 1
            yield i, number

    def upload_directories(self, dirs, path):
        number = len(dirs)
        i = 0
        for d in dirs:
            # shutil.copytree needs a fresh new destination directory
            ddir = os.path.join(path, os.path.basename(d))
            if os.path.exists(ddir):
                shutil.rmtree(ddir)

            shutil.copytree(d, ddir)
            i += 1
            yield i, number

    def delete_files(self, files):
        number = len(files)
        i = 0
        for f in files:
            os.unlink(f)
            i += 1
            yield i, number


    def delete_directories(self, directories):
        number = len(directories)
        i = 0
        for d in directories:
            shutil.rmtree(d)
            i += 1
            yield i, number

    def mkdir(self, path):
        os.mkdir(path)

    @classmethod
    def config_fields(cls):
        return {}

