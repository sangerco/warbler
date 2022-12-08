"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup("testuser","test@test.com","testuser",None)

        testuser_id = 1111
        self.testuser.id = testuser_id

        db.session.commit()

        self.message = Message(
                        text="testtesttest",
                        timestamp="2022-12-07 12:08:53.522807",
                        user_id=self.testuser.id
        )

        message_id = 1111
        self.message.id = message_id

        db.session.add(self.message)
        db.session.commit()

        self.like = Likes(
                        user_id=self.testuser.id,
                        message_id=self.message.id
        )

    def tearDown(self):
        
        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.get(1)
            self.assertEqual(msg.text, "Hello")

    def test_add_message_without_authentication(self):
        """ can you add a message without being logged in? """

        with self.client as c:
            res = c.post("/messages/new", data={"text": "testtesttest"}, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_add_message_wrong_user(self):
        """ can you add a message from user a's account when logged in as user b? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 123456

            res = c.post("/messages/new", data={"text": "testtesttest"}, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)           
        
    def test_view_message(self):
        """ test message page """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            url = f"/messages/{self.message.id}"
            res = c.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("testtesttest", html)

    def test_delete_message(self):
        """ delete message """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get(f"/messages/{self.message.id}/delete", follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertNotIn("testtesttest", html)

    def test_delete_message_without_authentication(self):
        """ delete message without being logged in? """

        with self.client as c:
            res = c.get(f"/messages/{self.message.id}/delete", follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_delete_other_users_message(self):
        """ can user a delete user b's message? """

        user2 = User.signup("testuser2", "test2@test.com", "password", None)

        user2_id = 2222
        user2.id = user2_id

        db.session.commit()

        message2 = Message(
                    text='testtesttest',
                    user_id=self.testuser.id
        )

        message2_id = 2222
        message2.id = message2_id

        db.session.add(message2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user2_id

            res = c.get(f"/messages/{message2_id}/delete", follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)