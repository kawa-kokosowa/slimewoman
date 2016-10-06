"""Test slimemom.py

"""

from __future__ import absolute_import

#import sqlalchemy

from tests import common
from slimewoman import slimewoman


def test_create_from_dir():
    slimewoman.create_quest_db_from_dir("sample_project")


if __name__ == '__main__':
    unittest.main()
