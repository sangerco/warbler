"""User model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test2"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("testuser1", "testuser1@test.com", "password", None)
        user1_id = 1111
        user1.id = user1_id

        db.session.commit()

        user1 = User.query.get(user1_id)

        self.user1 = user1
        self.user1_id = user1_id

        message1 = Message(
                    text="testtesttest", 
                    timestamp="2022-12-07 12:08:53.522807", 
                    user_id=user1_id)
        message1_id = 1111
        message1.id = message1_id

        db.session.add(message1)
        db.session.commit()

        message1 = Message.query.get(message1_id)
        
        self.message1 = message1
        self.message1_id = message1_id

        self.client = app.test_client()

    def test_create_message(self):
        """ test basic message model """

        msg = Message(
            text="test2test2test2",
            timestamp="2022-12-07 12:23:53.522807",
            user_id=self.user1_id,
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(self.user1.messages[1].text, "test2test2test2")

    def test_message_likes(self):
        """ test if message can get likes """

        like = Likes(user_id = self.user1_id, message_id=self.message1_id)

        db.session.add(like)
        db.session.commit()

        self.assertEqual(Likes.query.get(1).message_id, self.message1_id)

    
