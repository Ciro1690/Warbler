"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("firstuser", "first111@gmail.com", "12345", None)
        u1id = 1111
        u1.id = u1id

        u2 = User.signup("seconduser", "second222@gmail.com", "12345", None)
        u2id = 222
        u2.id = u2id

        db.session.commit()

        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)

        self.u1 = u1
        self.u1id = u1id

        self.u2 = u2
        self.u2id = u2id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="message1",
            user_id=self.u1id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(m.user, self.u1)

    def test_bad_message(self):
        m = Message(
            text=None,
            user_id=self.u1id
        )
        db.session.add(m)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_long_message(self):
        m = Message(
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            user_id=self.u1id
        )
        db.session.add(m)
        with self.assertRaises(exc.DataError) as context:
            db.session.commit()

    def test_bad_user_id(self):
        m = Message(
            text="test message",
            user_id=12324325
        )
        db.session.add(m)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
