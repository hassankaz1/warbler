
# Warbler 

A twitter clone, users are able to create and like other users posts. Users are also allowed to follow one another. This project was assigned by Springboard during my time as a Software Engineering fellow. 


## Tech Stack

HTML, CSS, Python, PostgreSQL, Flask 
## Quick Start

To run this project on your local machine. Clone the repository and run the following commands.

```bash
    python3 -m venv venv
    source venv/bin/activate`
    pip install -r requirements.txt
```
Setup the database. Run the seed file, this will generate users and messages.
 
```bash
    createdb warbler
    python seed.py
```

Start the server.
```bash
    flask run
```


## Demo

When user first enters the site, they are prompted to the sign up page where they may create an account.

![into](https://i.imgur.com/YiXl0lF.gif)

Users are able to edit their profile through a form found in their profile page 
![form-edit](https://awesomescreenshot.s3.amazonaws.com/image/3287719/26827349-bc3a4a2e6ef9699bffd37dd9b87ba7a6.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJSCJQ2NM3XLFPVKA%2F20220508%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220508T141929Z&X-Amz-Expires=28800&X-Amz-SignedHeaders=host&X-Amz-Signature=1bc0a6732554e34a83048a015e9e6d9b4fad5eedc2ae29402483e61b99c8ca81)

![form-out](https://awesomescreenshot.s3.amazonaws.com/image/3287719/26827371-f30a65190b6c8dc19b104530fb893f22.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJSCJQ2NM3XLFPVKA%2F20220508%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220508T141805Z&X-Amz-Expires=28800&X-Amz-SignedHeaders=host&X-Amz-Signature=93a945226fdd3d29933a17160cf3c0ad265f97d1ae5873977ba94915e96e926c)

Users can then search for users and follow them. 

![search](https://i.imgur.com/0QQhe44.gif)

On the home screen, users can view all the messages of those the user follows sorted by newest. There is functionality to like and unlike messages. User can also post messages.

![message](https://i.imgur.com/YmLp5tA.gif)