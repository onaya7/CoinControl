import unittest
from coincontrol.extensions import db
from coincontrol.models import Users
from coincontrol import create_app
from flask_jwt_extended import create_access_token
from coincontrol.tokens import generate_confirmation_token


"""
Code Analysis

Main functionalities:
The Register and Login route is responsible for handling user registration and logging in process. It receives user data and validates it on submit using the RegistrationForm class, and creates a new user in the Users table of the database and logs the user into the system.
Methods:
- post: receives user data, validates it using RegistrationForm, creates a new user in the database, and returns a response with a status code and a message and logs in the user .

Fields:
- None.
"""

class Test_Register_Login(unittest.TestCase):
    def create_app(self):
        # Creating a test flask application
        # It takes in a parameter called testing which is passed as an argument to the config_name variable
        app = create_app(config_name="testing")
        return app

    def setUp(self):
        # Creating and configuring the test database
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        # Cleaning up the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
             
    """ Test empty form submission """     
    def test_empty_form_submission(self):
        tester = self.client
        response = tester.post("/register", data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"This field is required.", response.data)
    
    """ Test invalid form submission """     
    def test_invalid_form_submission(self):
        username = "testuser"
        email = "invalid-email",
        password = "pass",
        confirm_password = "password"
        
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }
        
        tester = self.client
        response = tester.post("/register", json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid email address.", response.data)
        self.assertIn(b"Password must match confirm password", response.data)
        self.assertIn(b"Password must include at least one uppercase letter, one lowercase letter, one number, and one special character", response.data)
        
    """ Tests that a user cannot register with an existing email """
    def test_existing_email(self):
        username="testuser1" 
        email="samuelayano6+1@gmail.com"
        password = "Test1$"
        confirm_password = "Test1$"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }
        
        tester = self.client
        response = tester.post("/register", json=data, follow_redirects=True) 
        
        user = Users.query.filter_by(email=email).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email) 
        self.assertEqual(user.username, username) 
        response = tester.post("/register", json=data, follow_redirects=True) 
        self.assertIn(b"This email is taken. Please choose a different one", response.data)

        
    """ Testing registration data flow with valid data """
    def test_successful_registration_(self):
        """ Adding user to the database """
        username="testuser" 
        email="samuelayano6@gmail.com"
        password = "Test1$"
        confirm_password = "Test1$"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }
        tester = self.client
        response = tester.post("/register", json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'A confirmation email has been sent to your email address.', response.data) 

        
        """  Tests that 'unconfirmed' page is rendered when user is logged in and not verified"""
        response = tester.get("/unconfirmed", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        """ Tests that user is redirected to home page when already verified. """
        user = Users.query.filter_by(email=email).first()
        user.verified = True
        db.session.commit()
        response = tester.get("/unconfirmed", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has already been verified. Please login.', response.data)
        
        """ Tests that user is redirected to home page when an error occurs. """
        user.verified = None
        db.session.commit()
        response = tester.get("/unconfirmed", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'An error occurred while processing your request. Please try again later.', response.data)
        
        """Tests that a user can successfully login with correct email and password"""
        response = tester.post(
            "/login", json={"email": email, "password": password}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged in successfully', response.data)

        """Tests that an error message is displayed when user enters incorrect email"""
        response = tester.post(
                '/login',
                data=dict(email='wrong@test.com', password='password'),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login Unsuccessful. Please check username and password', response.data)

        
class TestConfirmToken(unittest.TestCase):
    def create_app(self):
        # Creating a test flask application
        # It takes in a parameter called testing which is passed as an argument to the config_name variable
        app = create_app(config_name="testing")
        return app

    def setUp(self):
        # Creating and configuring the test database
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        # Cleaning up the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_confirm_token(self):
        # Testing token confirmation process
        username = "testuser"
        password = "testpassword"
        email = "testemail@gmail.com"
        user = Users(username=username, password=password, email=email)
        user.generate_password_hash(password)
        db.session.add(user)
        db.session.commit()

        # To send a confirmation token to a user
        user = Users.query.filter_by(email=email).first()
        user_id = user.user_id
        
        # generate a confirmation_token
        token = create_access_token(identity=user_id)

        # perform token verification
        with self.app.test_request_context():
            from flask_jwt_extended import decode_token

            decoded_token = decode_token(token)
      
        tester = self.client
        response = tester.get(f'/confirm/{token}', follow_redirects=True)
        
        # verify the decoded token
        self.assertEqual(decoded_token["sub"], user_id)
        self.assertEqual(response.status_code, 200)
        
class TestResendConfirmation(unittest.TestCase):
    def create_app(self):
        # Creating a test flask application
        # It takes in a parameter called testing which is passed as an argument to the config_name variable
        app = create_app(config_name="testing")
        return app

    def setUp(self):
        # Creating and configuring the test database
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        # Cleaning up the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    """ Tests that the user is logged in before resending confirmation"""   
    def test_resend_confirmation_logged_in(self):
        tester = self.client
        response = tester.get('/resend-token', follow_redirects=True)
        self.assertIn(b'Please log in to access this page.', response.data)
        
             
        
class TestLogin(unittest.TestCase):
    def create_app(self):
        # Creating a test flask application
        # It takes in a parameter called testing which is passed as an argument to the config_name variable
        app = create_app(config_name="testing")
        return app

    def setUp(self):
        # Creating and configuring the test database
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        # Cleaning up the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_login(self):
        # Testing user login process
        username = "testuser"
        email = "test@gmail.com"
        password = "testpassword"
        user = Users(username=username, email=email, password=password)
        user.generate_password_hash(password)
        db.session.add(user)
        db.session.commit()

        # login
        tester = self.client
        response = tester.post(
            "/login", json={"email": email, "password": password}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        # log out
        response = tester.post("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
class TestForgotpassword(unittest.TestCase):
    def create_app(self):
        # Creating a test flask application
        # It takes in a parameter called testing which is passed as an argument to the config_name variable
        app = create_app(config_name="testing")
        return app

    def setUp(self):
        # Creating and configuring the test database
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        # Cleaning up the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_valid_email(self):
        """creating a test user"""  
        username = "testuser"
        email="samuelayano6@gmail.com"
        password= "Testuser1$"
        
        user = Users(username=username, email=email)
        user.generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        
        data = {
        "email": email,
        }
        tester = self.client
        response = tester.post("/forgotpassword", json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)





    
        
        



if __name__ == "__main__":
    unittest.main()
