"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
from datetime import datetime

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Create a test user
        user = User.signup("testuser", "testuser@test.com", "password", None)
        db.session.commit()

        self.user_id = user.id

        # Create a test message
        message = Message(text="Test message content", user_id=self.user_id, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_messages_add(self):
        """Can user create a new message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            response = c.post('/messages/new', data={'text': 'New test message'}, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'New test message', response.data)
