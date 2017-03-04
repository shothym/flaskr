import sqlite3
from contextlib import closing
from flask import (Flask,
                   request,
                   session,
                   g,
                   redirect,
                   url_for,
                   abort,
                   render_template,
                   flash)


# 各種設定
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'developmentkey'
USERNAME = 'admin'
PASSWORD = 'default'


# アプリ作成
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTING', silent=True)


# DB接続
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# コントローラ（djangoでいうview）
# DBに保存されているエントリーの一覧ページ
@app.route('/')
def show_entries():
    cur = g.db.execute('SELECT title, text FROM entries ORDER BY id DESC')
    entries = [dict(title=row[0], text=row[1],) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


# エントリー追加ページ
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('新しいエントリーが追加されました。')
    return redirect(url_for('show_entries'))


# ログイン・ログアウト
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = u'ユーザ名が間違っています。'
        elif request.form['password'] != app.config['PASSWORD']:
            error = u'パスワードが間違っています。'
        else:
            session['logged_in'] = True
            flash(u'ログインしました。')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'ログアウトしました')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
