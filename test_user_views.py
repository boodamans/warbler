from flask import session
from models import db, User
from app import app, CURR_USER_KEY
from unittest import TestCase

# Set up the testing configuration
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'

# Create the tables and initialize the database
db.create_all()

class UserViewTestCase(TestCase):
    """Test views and routes for users."""

    def setUp(self):
        """Create test client, add sample data."""
        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.remove()
        db.drop_all()
        db.create_all()



    def test_signup(self):
        """Does the signup class method create a new user?"""
        user = User.signup("newuser", "newuser@test.com", "password", None)
        db.session.commit()

        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@test.com")
        self.assertTrue(user.password.startswith('$2b$'))

    def test_logout_route(self):
        user = User.signup("testuser", "testuser@test.com", "password", None)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user.id

            response = c.get('/logout', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You have been logged out.', response.data)
            self.assertNotIn(CURR_USER_KEY, session)