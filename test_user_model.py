"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
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

        new_user = User.signup("user_one", "one@user.com", "password", None)
        new_user.id = 1111

        new_user_two = User.signup(
            "user_two", "two@user.com", "password", None)
        new_user_two.id = 2222

        db.session.commit()

        user_one = User.query.get(1111)
        user_two = User.query.get(2222)

        self.user_one = user_one
        self.user_two = user_two

        self.user_one_id = 1111
        self.user_two_id = 2222

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

    # test to see if user following correctly works
    def test_user_follows(self):
        # add user two to user one following
        self.user_two.following.append(self.user_one)
        db.session.commit()

        self.assertEqual(len(self.user_one.followers), 1)
        self.assertEqual(len(self.user_two.following), 1)

        self.assertEqual(self.user_one.followers[0].id, self.user_two.id)
        self.assertEqual(self.user_two.following[0].id, self.user_one.id)

    # test to check if is_following function is accurate
    def test_is_following(self):
        # append user two to user one following
        self.user_one.following.append(self.user_two)
        db.session.commit()

        # check accuracy
        self.assertTrue(self.user_one.is_following(self.user_two))
        self.assertFalse(self.user_two.is_following(self.user_one))

    # test to check if is_followed is accurate
    def test_is_followed_by(self):
        self.user_one.following.append(self.user_two)
        db.session.commit()

        self.assertTrue(self.user_two.is_followed_by(self.user_one))
        self.assertFalse(self.user_one.is_followed_by(self.user_two))

    ####
    #
    # Signup Tests
    #
    ####
    # test to check is user signup occurs correctly
    def test_valid_signup(self):
        # sign up new user
        user_signup = User.signup(
            "testuser", "test@user.com", "password", None)
        user_signup.id = 12345
        db.session.commit()

        # retrieve newly signed up user
        user_test = User.query.get(12345)
        # test validity of retrieval with newly signed up user
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, "testuser")
        self.assertEqual(user_test.email, "test@user.com")
        self.assertNotEqual(user_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(user_test.password.startswith("$2b$"))

    # check invalid signup with no username during signup
    def test_invalid_username_signup(self):
        # invalid signup with no username(nullable=false)
        invalid_signup = User.signup(None, "test@user.com", "password", None)
        invalid_signup.id = 111111

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    # check invalid signup with no email during signup
    def test_invalid_email_signup(self):
        # invalid signup with no email(nullable=false)
        invalid_signup = User.signup("invaliduser", None, "password", None)
        invalid_signup.id = 222222

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    # check invalid signup with no password during signup
    def test_invalid_password_signup(self):
        # invalid signup with empty string as password
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)

        # invalid signup with password as None(nullable=false)
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    ####
    #
    # Authentication Tests
    #
    ####
    # test User authenticate function to validate user with valid password
    def test_valid_authentication(self):
        user = User.authenticate(self.user_one.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, 1111)

    # test invalid user
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    # test valid user with invalid password
    def test_wrong_password(self):
        self.assertFalse(User.authenticate(
            self.user_one.username, "incorrectpassword"))
