"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from datetime import datetime

from models import db, connect_db, Message, User

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

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_messages_show(self):
        """Can user view a message?"""

        message = Message.query.one()
        response = self.client.get(f'/messages/{message.id}')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test message content', response.data)
