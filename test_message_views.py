"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from email import message
from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


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

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

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

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    #
    # check to see if no user logged in, creating messages will not be allowed

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    # check to see if posts are unauthorized for invalid user
    def test_invalid_user(self):
        # not valid user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 5000000

            # try to create new post under invalid user
            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)
            # should get response as unauthorized
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    # test to check if new messages are shown
    def test_message_show(self):
        # creating new messaage
        new_message = Message(
            text="trial message",
            user_id=self.testuser.id
        )

        new_message.id = 300

        db.session.add(new_message)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # retrieve previosuly created message
            message_retrieval = Message.query.get(300)

            # using GET method we retrieve message
            resp = c.get("/messages/300")
            # check validity of response
            self.assertEqual(resp.status_code, 200)
            self.assertIn(new_message.text, str(resp.data))

    # test to check retrieval of invalid message outcomes error
    def test_invalid_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # try to retrieve message that does not exist using GET method
            resp = c.get('/messages/1000000000000')
            # should recieve a 404 error code
            self.assertEqual(resp.status_code, 404)

    # check to see if messages are properly deleted
    def test_delete_message(self):
        # create new message
        trial_message = Message(
            id=321,
            text="trial message",
            user_id=self.testuser.id
        )
        db.session.add(trial_message)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # delete previously deleted message using POST method
            resp = c.post("/messages/321/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # retrieve message that has already been deleted
            message_retrieval = Message.query.get(321)
            # check to see that message no longer exists
            self.assertIsNone(message_retrieval)

    # check to see if unauthorized person can delete other users message
    def test_message_delete_by_unauthorized(self):

        # Create second user
        trial_user = User.signup(
            username="new-user",
            email="new@test.com",
            password="password",
            image_url=None)

        trial_user.id = 666

        # Message is owned by testuser
        new_message = Message(
            id=111,
            text="trial message",
            user_id=self.testuser.id
        )
        db.session.add_all([trial_user, new_message])
        db.session.commit()

        # login with newly created user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 666
            # try to delete message under different user
            resp = c.post("/messages/111/delete", follow_redirects=True)
            # should return access unauthorized
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    # check to see if message can be deleted with no authentication
    def test_message_delete_no_authentication(self):
        # create new message under test user
        new_message = Message(
            id=333,
            text="another trial message",
            user_id=self.testuser.id
        )
        db.session.add(new_message)
        db.session.commit()

        # with no user logged in, check if message can be deleted
        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(333)
            self.assertIsNotNone(m)
