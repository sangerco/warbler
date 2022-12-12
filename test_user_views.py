"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test2"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        user1 = User.signup("user1", "test@test.com", "password", None)

        user1_id = 111
        user1.id = user1_id

        user2 = User.signup("user2", "test2@test.com", "password", None)

        user2_id = 222
        user2.id = user2_id

        user3 = User.signup("user3", "test3@test.com", "password", None)

        user3_id = 333
        user3.id = user3_id

        user4 = User.signup("user4", "test4@test.com", "password", None)

        user4_id = 444
        user4.id = user4_id          

        db.session.commit()

        self.user1 = user1
        self.user2 = user2
        self.user3 = user3
        self.user4 = user4

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp 

    def test_home_page(self):
        """ test home page without logged in"""

        with self.client as c:
            url = ('/')
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Sign up', html)


    def test_user_home(self):
        """ test user home page """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            url = ('/')
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('@user1', html)

    def test_user_index(self):
        """ test user list page """

        with self.client as c:

            url = ('/users')
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('@user2', html)
            self.assertIn('@user3', html)
            self.assertIn('@user4', html)

    def test_edit_user(self):
        """ test to edit user """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            user = {"username": "Edited", "password":"password"}
            res = c.post("/users/profile", data = user, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Edited", html)

    def test_user_page(self):
        """ test user detail page """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            url = (f"/users/{self.user1.id}")
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("@user1", html)
            self.assertIn("Edit Profile", html)
            self.assertIn("Delete Profile", html)

    def test_following_page(self):
        """ test user following page """

        f1 = Follows(user_being_followed_id=222, user_following_id=111)
        f2 = Follows(user_being_followed_id=333, user_following_id=111)
        f3 = Follows(user_being_followed_id=444, user_following_id=111)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            url = (f"/users/{self.user1.id}/following")
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("@user2", html)
            self.assertIn("@user3", html)
            self.assertIn("@user4", html)

    def test_followers_page(self):
        """ test user followers page """
        f1 = Follows(user_being_followed_id=111, user_following_id=222)
        f2 = Follows(user_being_followed_id=111, user_following_id=333)
        f3 = Follows(user_being_followed_id=111, user_following_id=444)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            url = (f"/users/{self.user1.id}/followers")
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("@user2", html)
            self.assertIn("@user3", html)
            self.assertIn("@user4", html)

    def test_user_likes(self):
        """ test user likes """

        m1 = Message(text="hello", user_id=self.user2.id)
        m1_id = 111
        m1.id = m1_id
        m2 = Message(text="hi", user_id=self.user3.id)
        m2_id = 222
        m2.id = m2_id

        db.session.add_all([m1,m2])
        db.session.commit()

        l1 = Likes(user_id=self.user1.id, message_id=111)
        l2 = Likes(user_id=self.user1.id, message_id=222)

        db.session.add_all([l1,l2])
        db.session.commit()


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            url = (f"/users/{self.user1.id}/likes")
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("hello", html)
            self.assertIn("hi", html)
            self.assertIn("@user2", html)

    def test_signup_view(self):
        """ test user signup page """

        with self.client as c:

            url = ("/signup")
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Join Warbler today.", html)
            self.assertIn('<button class="btn btn-primary btn-lg btn-block">Sign me up!</button>', html)

    def test_signup(self):
        """ test signup page """
        with self.client as c:

            u5 = {'username':'user5', 'email': 'test5@test.com', 'password':'password', 'image_url':None}
            res = c.post('/signup', data = u5, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('@user5', html)

    def test_delete_user(self):
        """ test delete user page """

        user6 = User.signup("user6", "test6@test.com", "password", None)
        user6_id = 666
        user6.id = user6_id

        db.session.commit()

        self.user6 = user6

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user6.id  

            url = ('/users/delete')  
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 302)
