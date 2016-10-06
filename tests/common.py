import os
import tempfile
import unittest

import sqlalchemy

import models


class BaseTest(unittest.TestCase):

    def setUp(self):
        """Setup a test SQLite database.

        """

        self.temp_file_handle, self.temp_file_path = tempfile.mkstemp()
        engine = sqlalchemy.create_engine(
            'sqlite:///' + self.temp_file_path
        )
        self.session = sqlalchemy.orm.sessionmaker(bind=engine)()
        models.Base.metadata.create_all(engine)

    def tearDown(self):
        os.close(self.temp_file_handle)
        os.unlink(self.temp_file_path)
