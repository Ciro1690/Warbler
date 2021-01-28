"""User model tests."""

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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertIn('testuser, test@test.com>', u.__repr__())

    def test_following(self):
        """Does following a user work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        u.following.append(u2)
        db.session.commit()

        self.assertEqual(len(u.following), 1)
        self.assertEqual(len(u2.following), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u2.followers), 1)

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_bad_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email#email.com", "", None)

    def test_authenticate_user(self):

        u = User.authenticate(self.u1.username, "12345")
        self.assertIsNotNone(u)
        self.assertEqual(u.id,self.u1id)

    def test_bad_username(self):
        self.assertFalse(User.authenticate("fake", None))
    
    def test_bad_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "132345"))

    