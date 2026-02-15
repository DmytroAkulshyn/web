from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_login import LoginManager, UserMixin,logout_user, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'd2288sosiska'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

connection = sqlite3.connect('sqlite.db', check_same_thread=False)
cursor = connection.cursor()



class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    user = cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user is not None:
        return User(user[0], user[1], user[2])
    return None

def close_db(connection=None):
    if connection is not None:
        connection.close()

@app.teardown_appcontext
def close_connection(exception):
    close_db()

@app.route("/")
def index():
    cursor.execute('SELECT * from post JOIN user ON post.author_id = user.id')
    result = cursor.fetchall()
    print(result)
    posts = []
    for post in reversed(result):
        posts.append(
            {'id': post[0], 'title': post[1], 'content': post[2], 'author_id': post[3], 'username': post[5]}
        )
    context = {'posts': posts}
    return render_template('blog.html', **context)

@app.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        cursor.execute(
            'INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)',
            (title, content, current_user.id)
        )
        connection.commit()
        return redirect(url_for("index"))
    return render_template('add_post.html',)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cursor.execute(
                'INSERT INTO user (username, password_hash) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            connection.commit()
            print('Регистрация пользователя прошла успешно')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', message='Username already exists!')
    return render_template('register.html')

@app.route('/post/<post_id>')
def post(post_id):
    print(post_id)
    result = cursor.execute(
        'SELECT * FROM post WHERE id = ?', (post_id,)
    ).fetchone()
    post_dict = {'id': result[0], 'title': result[1], 'content': result[2]}
    return render_template('blog.html', post=post_dict)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = cursor.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user and User(user[0], user[1], user[2]).check_password(password):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = cursor.execute('SELECT * FROM post WHERE id = ?',(post_id,)).fetchone()
    if post and post[3] == current_user.id:
        cursor.execute('DELETE FROM post WHERE id = ?', (post_id))
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

def user_is_liking(user_id, post_id):
    like = cursor.execute(
        'SELECT * FROM like WHERE user_id = ? AND post_id = ?',
        (user_id, post_id)).fetchone()
    return bool(like)

@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    post = cursor.execute('SELECT * FROM post WHERE id = ?',
                          (post_id,)).fetchone()
    if post:
        if user_is_liking(current_user.id, post_id):
            cursor.execute(
                'DELETE FROM like WHERE user_id = ? AND post_id = ?',
                (current_user.id, post_id))
            connection.commit()
            print('You unliked this post.')
        else:
            cursor.execute(
                'INSERT INTO like (user_id, post_id) VALUES (?, ?)',
                (current_user.id, post_id))
            connection.commit()
            print('You liked this post')
            return redirect(url_for('index'))
    return 'Post not found', 404

if __name__ == "__main__":
    app.run()

