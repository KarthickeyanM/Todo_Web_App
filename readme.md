Due to time constraints, I haven't been able to integrate the 'Buy Pro License' feature into my application.

# Flask To-Do List Application

Overview
This project is a To-Do List web application built with Flask, featuring GraphQL for API interactions and Keycloak for authentication. The application supports basic CRUD operations on To-Dos and integrates Stripe for Pro license payments, allowing users to upload images with a Pro license.

Features
User Authentication: Users must log in using Keycloak to access the application.
To-Do Management: Create, view, edit, delete, and mark To-Dos as done.
Image Upload: Available only for users with a Pro license.
GraphQL API: Access and manage To-Dos via a GraphQL API.
Stripe Integration: Purchase a Pro license to enable image uploads. # Due to time constraints, I haven't been able to integrate this feature into my application.
GraphiQL Interface: For testing GraphQL queries, protected by Keycloak authentication.
Installation
Clone the repository:

bash
Copy code
git clone <repository_url>
cd <repository_name>
Set up a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure Keycloak:

Ensure that you have a Keycloak server running and configured with the following details:

client_id
client_secret
realm_name
Update these details in client_secrets.json.



Initialize the database:

bash
Copy code
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
Configuration
Flask Configuration: Adjust settings in app.py for Flask, Keycloak, and Stripe.
Keycloak Configuration: Update the OIDC_CLIENT_SECRETS in app.py to match your Keycloak settings.
Usage
Run the Flask application:

bash
Copy code
python app.py
Access the Application:

Navigate to http://localhost:5000 in your web browser.

GraphQL API:

Access the GraphQL API at http://localhost:5000/graphql. The GraphiQL interface is available if graphiql=True is set in app.py.

Endpoints
/: Display the list of To-Dos.
/add: Add a new To-Do.
/edit/<id>: Edit an existing To-Do.
/check/<id>: Toggle the completion status of a To-Do.
/delete/<id>: Delete a To-Do.
/logout: Log out of Keycloak.
Security
Keycloak: Used for authentication and authorization.
GraphQL: Secured via custom GraphQLView, requiring authentication for all requests.
Contributing
Fork the repository.

Create a new branch:

bash
Copy code
git checkout -b feature/your-feature
Make your changes and commit:

bash
Copy code
git add .
git commit -m "Add your feature"
Push your changes:

bash
Copy code
git push origin feature/your-feature
Create a pull request on GitHub.

License
This project is licensed under the MIT License. See the LICENSE file for details.
