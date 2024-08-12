from flask import Flask, render_template, request, redirect, url_for, flash
from flask_oidc import OpenIDConnect
from flask_graphql import GraphQLView
import datetime
import base64
from models import Todo as TodoModel, session
from graphql_schema import schema
from keycloak import KeycloakOpenID

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instances/todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'  # Set a secret key for flash messages

# Keycloak configuration
app.config.update({
    'SECRET_KEY': 'XlBGtHzPOefRKjiEB9yTcQS0WBHllAcx',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'todo_realm',
    'OIDC_SCOPES': ['openid'],
    'OIDC_TOKEN_TYPE_HINT': 'access_token',
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
})

keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                        client_id="todo_client",
                        realm_name="todo_realm",
                        client_secret_key="4U36Pyx5O28RRGLMvM3N6JyzGyCQOzKn",
                        verify=True)

oidc = OpenIDConnect(app)

@app.route("/")
@oidc.require_login
def index():
    todos = session.query(TodoModel).all()
    todos_with_images = []
    for todo in todos:
        if todo.images:
            image_base64 = base64.b64encode(todo.images).decode('utf-8')
            todos_with_images.append({**todo.__dict__, 'images': image_base64})
        else:
            todos_with_images.append({**todo.__dict__, 'images': None})
    return render_template("index.html", todos=todos_with_images)

def user_has_pro_role():
    user_info = oidc.user_getinfo(['roles'])
    return 'pro' in user_info.get('roles', [])

@app.route("/add", methods=["GET"])
@oidc.require_login
def add_task():
    return render_template("add.html",user_has_pro_role=user_has_pro_role())

@app.route("/add", methods=["POST"])
@oidc.require_login
def add():
    title = request.form.get('title').strip()
    description = request.form.get('description').strip()
    time = request.form.get('time').strip()

    try:
        images = []
        if 'images' in request.files:
            if user_has_pro_role():
                files = request.files.getlist('images')
                for file in files:
                    if file and file.filename:
                        file_data = file.read()
                        images.append(file_data)
            else:
                flash('You need a Pro license to upload images.', 'warning')

        new_todo = TodoModel(
            title=title,
            description=description,
            time=datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M'),
            images=b''.join(images) if images else None
        )
        session.add(new_todo)
        session.commit()
        flash('Todo added successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@oidc.require_login
def edit(id):
    todo = session.query(TodoModel).get(id)
    if not todo:
        flash('Todo not found.', 'warning')
        return redirect(url_for('index'))

    if request.method == "POST":
        title = request.form.get('title').strip()
        description = request.form.get('description').strip()
        time = request.form.get('time').strip()

        try:
            images = []
            if  'images' in request.files:
                if user_has_pro_role():
                    files = request.files.getlist('images')
                    for file in files:
                        if file and file.filename:
                            file_data = file.read()
                            images.append(file_data)
                else:
                    flash('you need a Pro license to upload images','warning')

            todo.title = title
            todo.description = description
            todo.time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M')
            todo.images = b''.join(images) if images else todo.images
            session.commit()
            flash('Todo updated successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for("index"))

    else:
        images_base64 = base64.b64encode(todo.images).decode('utf-8') if todo.images else None
        return render_template("edit.html", todo=todo, images_base64=images_base64, user_has_pro_role=user_has_pro_role())

@app.route('/check/<int:id>', methods=['GET','POST'])
@oidc.require_login
def check(id):
    todo = session.query(TodoModel).get(id)
    if todo:
        todo.done = not todo.done
        session.commit()
        flash('Todo status updated!', 'success')
    else:
        flash('Todo not found.', 'warning')
    return redirect(url_for("index"))

@app.route('/delete/<int:id>')
@oidc.require_login
def delete(id):
    todo = session.query(TodoModel).get(id)
    if todo:
        session.delete(todo)
        session.commit()
        flash('Todo deleted successfully!', 'success')
    else:
        flash('Todo not found.', 'warning')
    return redirect(url_for("index"))

@app.route('/authorize')
def authorize():
    if oidc.user_loggedin:
        return redirect(url_for('index'))
    else:
        return "Login failed", 401

@app.route('/logout')
def logout():
    refresh_token = oidc.get_refresh_token()
    oidc.logout()
    keycloak_openid.logout(refresh_token)
    return redirect(url_for('index'))

class AuthenticatedGraphQLView(GraphQLView):
    def __init__(self, *args, **kwargs):
        self.oidc = kwargs.pop('oidc', None)
        super().__init__(*args, **kwargs)

    def dispatch_request(self, *args, **kwargs):
        if not self.oidc.user_loggedin:
            return redirect(url_for('authorize'))
        return super().dispatch_request(*args, **kwargs)

# Add GraphQL endpoint
app.add_url_rule('/graphql', view_func=AuthenticatedGraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))

if __name__ == '__main__':
    app.run(debug=True)