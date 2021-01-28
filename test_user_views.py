"""User views tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from app import signup, app, CURR_USER_KEY
from models import db, connect_db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()

        self.client = app.test_client()
       
        self.user = User.signup(username="test",
                                email="test@email.com",
                                password="password",
                                image_url=None)
        self.user_id = 1111
        self.user.id = self.user_id
       
        self.user2 = User.signup(username="test2",
                                email="test2@email.com",
                                password="password",
                                image_url=None)
        self.user2_id = 22222
        self.user2.id = self.user2_id

        db.session.commit()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_list_users(self):
        """Can you see the follow pages once logged in?"""
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test', html)
            self.assertIn('test2', html)
 
    def test_search(self):
        with app.test_client() as client:
            resp = client.get("/users?q=test")     
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test', html)
            self.assertIn('test2', html)
        
    def find_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.code, 200)
            self.assertIn('test', html)

    def set_up_follows(self):
        f1 = Follows(user_being_followed_id=self.user.id, user_following_id=self.user2.id)
        f2 = Follows(user_being_followed_id=self.user2.id, user_following_id=self.user.id)

        db.session.add_all([f1, f2])
        db.session.commit()

    def test_following_user_pages(self):
        self.set_up_follows()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id
            resp = client.get(f'/users/{self.user.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test2', html)

    def test_followed_user_pages(self):
        self.set_up_follows()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id
            resp = client.get(f'/users/{self.user.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test2', html)




