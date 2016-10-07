from __future__ import absolute_import

import unittest

import sqlalchemy

from slimewoman import database


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.session = database.connect()
