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
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("testuser", "testuser@testuser.com", "password", None)
        user1_id = 1111
        user1.id = user1_id

        user2 = User.signup("testuser2", "testuser2@test.com", "password", None)
        user2_id = 2222
        user2.id = user2_id

        db.session.commit()

        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)

        self.user1 = user1
        self.user1_id = user1_id

        self.user2 = user2
        self.user2_id = user2_id

        self.client = app.test_client()


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

    def test_is_following(self):
        """ does following functionality work? """

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertNotEqual(self.user2.following[0].id, self.user1.id)

    def test_is_followed_by(self):
        """ does followers functionality work? """

        self.user2.following.append(self.user1)
        db.session.commit()

        self.assertEqual(self.user1.followers[0].id, self.user2.id)
        self.assertNotEqual(self.user2.followers[0].id, self.user1.id)

    def test_user_create(self):
        """ does signup functionality work? """

        user3 = User.signup(username="testuser3", 
                            email="test3@test.com", 
                            password="password", 
                            image_url="http://testimage.com/test.jpg")
        user3_id = 3333
        user3.id = user3_id

        db.session.commit() 

        user3 = User.query.get(user3_id)

        self.assertEqual(user3.username, "testuser3")
        self.assertEqual(user3.email, "test3@test.com")
        self.assertEqual(user3.image_url, "http://testimage.com/test.jpg")

    def test_bad_username_create(self):
        """ test signup with no username """
        user4 = User.signup(username=None,
                            email="test4@test.com",
                            password="password",
                            image_url="http://testimage.com/test.jpg")

        user4_id = 4444
        user4.id = user4_id

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_bad_email_create(self):
        """ test signup with no email """
        user6 = User.signup(username="testuser6",
                            email="test6@test.com",
                            password=None,
                            image_url="http://testimage.com/test.jpg")

        user6_id = 6666
        user6.id = user6_id

        with self.assertRaises(ValueError) as context:
            db.session.commit()

    def test_bad_email_create(self):
        """ test signup with no password """
        user6 = User.signup(username="testuser6",
                            email=None,
                            password="password",
                            image_url="http://testimage.com/test.jpg")

        user5_id = 5555
        user5.id = user5_id

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_user_authenticate(self):
        """ test user authentication method """

        user1 = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(user1)
        self.assertEqual(user1.id, self.user1_id)

    def test_bad_username(self):
        """ test if wrong or invalid username """

        self.assertFalse(User.authenticate("user5", "password"))

    def test_bad_password(self):
        """ test if wrong or invalid password """

        self.assertFalse(User.authenticate("user1", "asdfaefda"))

        