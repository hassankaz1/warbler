from app import app
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

# setting an environmental variable

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

#import app

# creating our tables
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 50000
        image = "https://i.pinimg.com/custom_covers/222x/85498161615209203_1636332751.jpg"
        u = User.signup(
            username="Unit",
            email="unit@test.com",
            password="password",
            image_url=image)
        # add trial user to database
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message(self):
        """Test to see if new messages are created"""

        new_message = Message(
            text="trial message",
            user_id=self.uid
        )
        # add trial message to database
        db.session.add(new_message)
        db.session.commit()

        # check to see if user's first message is the trial message
        self.assertEqual(self.u.messages[0].text, "trial message")

    def test_message_likes(self):
        # creating another trial message
        new_message_two = Message(
            text="trial message two",
            user_id=self.uid
        )
        # creating new user
        trial_user_two = User.signup(
            username="alsoatest",
            email="also@test.com",
            password="password",
            image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSd5d998SgnfhxPMQ9-S5AIcZdtL4qbjhEn1g&usqp=CAU")
        # create a user id so we can assign this number to the trial user (intended for easier retrieval)
        user_id = 888

        trial_user_two.id = user_id

        db.session.add_all([new_message_two, trial_user_two])
        db.session.commit()
        # add the message to the trial user's likes
        trial_user_two.likes.append(new_message_two)

        db.session.commit()

        # retrieve the like by trial user two
        like_retrieval = Likes.query.filter(
            Likes.user_id == trial_user_two.id).first()
        # retrieve the message from the like_retrieval
        message_retrival = Message.query.get(like_retrieval.message_id)
        # test to check if message retrieved is same as the one created
        self.assertEqual(like_retrieval.message_id, new_message_two.id)
        self.assertEqual(message_retrival.text, "trial message two")
