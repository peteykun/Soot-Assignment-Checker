import bottle_session
from bottle import run, post, request, response, get, route, static_file, SimpleTemplate, redirect, app
from bottle.ext import sqlite
import json, os, time, sqlite3
import subprocess32 as subprocess

# install session plugin
app().install(bottle_session.SessionPlugin(cookie_lifetime=600))

conn = sqlite3.connect('submissions.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS submits (name text, suite text, filename text, result text)')
c.execute('CREATE TABLE IF NOT EXISTS failure_message (submit_id integer, message text)')
c.execute('CREATE TABLE IF NOT EXISTS sub_stats (submit_id integer, method text, path_edges_found integer, path_edges_missed integer, path_edges_extra integer, path_edges_dupes integer, leaks_found integer, leaks_missed integer, leaks_extra integer)')
conn.commit()
conn.close()

with open('demo.tpl') as f:
    tpl = SimpleTemplate(f.read())

with open('submits.tpl') as f:
    submits_tpl = SimpleTemplate(f.read())

with open('submit.tpl') as f:
    submit_tpl = SimpleTemplate(f.read())

@route('/')
def index(session):
    logged_in = session.get('username') is not None
    return tpl.render(error='', logged_in=logged_in, username=session.get('username'))

@route('/logout')
def logout(session):
    session['username'] = ''
    redirect('/')

@route('/login', method = 'POST')
def login(session):
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    rows = c.execute("SELECT username FROM users WHERE username = ? AND password = ?", (request.forms.get('name'), request.forms.get('password')))

    for row in rows:
        print row
        session['username'] = row[0]

    conn.commit()
    conn.close()
    redirect('/')

@route('/run', method = 'POST')
def process(session):
    name = request.forms.get('name').replace(' ', '_')
    suite = request.forms.get('suite')
    upload = request.files.get('jar')
    error = None

    if name.strip() == '':
        error = 'No name specified.'
    elif upload is None:
        error = 'No file selected.'
    else:
        filename, ext = os.path.splitext(upload.filename)
        if ext != '.jar':
            error = 'File extension not allowed.'

        save_path = "submissions/{name}".format(name=name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = "{path}/{file}".format(path=save_path, file=filename + '_' + str(int(time.time())) + ext)
        upload.save(file_path)

        conn = sqlite3.connect('submissions.db')
        c = conn.cursor()
        c.execute("INSERT INTO submits VALUES (?, ?, ?, '')", (name, suite, file_path))
        rowid = c.lastrowid
        conn.commit()
        conn.close()

        result = {'name': name, 'suite': suite, 'jar_path': file_path}
        reference_json = "Tests/" + suite + ".json"
        reference_stdout = "Tests/" + suite + ".txt"
        test_jar = "Tests/" + suite + ".jar"

        print ['python2', 'verify.py', reference_json, reference_stdout, file_path, test_jar, str(rowid)]
        subprocess.Popen(['python2', 'verify.py', reference_json, reference_stdout, file_path, test_jar, str(rowid)])

    if error is not None:
        return tpl.render(error=error, logged_in=session.get('username') is not None)
    else:
        redirect('/submission/%d' % rowid)

@route('/submissions', method = 'GET')
def submissions(session):
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    corrects = set()
    for row in c.execute("SELECT rowid, name FROM submits s WHERE (SELECT SUM(path_edges_missed + path_edges_extra + path_edges_dupes + leaks_missed + leaks_extra) from sub_stats t WHERE t.submit_id = s.rowid) == 0"):
        corrects.add(row[0])
    retval = submits_tpl.render(rows=c.execute("SELECT rowid, name, suite FROM submits"), logged_in=session.get('username') is not None, corrects=corrects)
    conn.close()
    return retval

@route('/submission/:id', method = 'GET')
def submission(id, session):
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    rows = c.execute("SELECT name, result FROM submits WHERE rowid = ?", (id,))
    for row in rows:
        if session.get('username') != 'admin' and row[0] != session.get('username'):
            redirect('/')
            return ''
        output = row[1]
    retval = submit_tpl.render(output=output, rows=c.execute("SELECT method, path_edges_found, path_edges_missed, path_edges_extra, path_edges_dupes, leaks_found, leaks_missed, leaks_extra FROM sub_stats WHERE submit_id = ? ORDER BY method", (id,)), logged_in=session.get('username') is not None)
    conn.close()
    return retval

if __name__ == "__main__":
    print "Ready!"
    run(host='0.0.0.0', port=8081, server='paste', debug=True)
