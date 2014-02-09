import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session


def get_passwd(filename):
    """Read the username/passwd from an extra file.

    This is to prevent the password from being committed to the VCS.

    :param filename: The name of the file where the pw is stored.
    :return: The username:password
    """
    pw = ""
    try:
        with open(filename, "r") as f:
            pw = f.read()
    except OSError as e:
        print("Got an oserror: %s!" % e)
    return pw


class Connection(object):
    def __init__(self):
        self._connection_string = self._default_connection()
        self._engine = None
        self._metadata = None
        self._session = None

    def _default_connection(self):
        pw_file = os.path.join(os.path.dirname(__file__), "../../", "exma_pw")
        return 'mysql+cymysql://%s@127.0.0.1/exma?charset=utf8' % get_passwd(pw_file)

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(self._connection_string, echo=True)
        return self._engine

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = MetaData(bind=self.engine)
        return self._metadata

    @property
    def session(self):
        if self._session is None:
            self._session = scoped_session(sessionmaker(bind=self.engine))
        return self._session


connection = Connection()