from flask import Flask, render_template, request, render_template_string
import sqlite3
from datetime import *
import time as sleeptime

app = Flask(__name__)


@app.route('/add', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        tm = {'error': False, 'txtError': ''}
        return render_template('add.html', context=tm)

    if request.method == 'POST':
        rf = dict(request.form)
        name = rf['Name']
        surname = rf['Surname']
        con = sqlite3.connect("DateBase.db")
        cur = con.cursor()
        a = cur.execute('''SELECT name, surname FROM teens''').fetchall()
        error = False
        txtError = ''
        for i in a:
            if name == i[0] and surname == i[1]:
                error = True
                txtError = 'Подросток с такими ФИ уже зарегистрирован '
                break
            elif datetime.today().weekday() != 6:
                error = True
                txtError = 'Регистрировать подростков можно только по воскресеньям'
                break
        if not error:
            cur.execute('INSERT INTO Teens(name, surname, first_date, attendance)  VALUES(?, ?, ?, ?)', (name, surname, datetime.today().isoformat()[:10], '1'))
        con.commit()
        con.close()
        return render_template('add.html', txtError=txtError, error=error)

@app.route('/', methods=['POST', 'GET'])
@app.route('/note', methods = ['GET', 'POST'])
def note():
    if request.method == 'GET':
        con = sqlite3.connect("DateBase.db")
        cur = con.cursor()
        a = cur.execute('''SELECT name, surname, attendance FROM teens''').fetchall()
        con.close()
        return render_template('note.html', teens=list(a))

    if request.method == 'POST':

        rf = dict(request.form)
        print(rf)
        if 'submit_button' in rf:
            sq = rf['search query']
            con = sqlite3.connect("DateBase.db")
            cur = con.cursor()
            a = cur.execute('''SELECT name, surname, attendance FROM teens''').fetchall()
            res = []
            if sq == '':
                return render_template('note.html', teens=a)
            for i in a:
                for j in sq.split():
                    if j.lower() in i[0].lower() or j.lower() in i[1].lower():
                        res.append(i)
                        break
            con.close()
            return render_template('note.html', teens=res)

        else:
            print(0)
            if (datetime.weekday(datetime.now()) != 6 or not (datetime.isoformat(
                datetime.combine(datetime.date(datetime.today()), time(hour=8, minute=30))) <= datetime.isoformat(
                datetime.today())[:-7] <= datetime.isoformat(
                datetime.combine(datetime.date(datetime.today()), time(hour=13, minute=00))))):
                spec_status = 'Нельзя отмечать не во время собраний'
            else:
                spec_status = 'Отметить не получилось'
                full_name = list(rf)[0][3:].split('_')
                con = sqlite3.connect("DateBase.db")
                cur = con.cursor()
                current = cur.execute('''SELECT attendance FROM teens WHERE name = ? and surname = ?''', (full_name[0], full_name[1])).fetchall()
                if current[0][0][-1] == "0":
                    if datetime.isoformat(
                datetime.combine(datetime.date(datetime.today()), time(hour=8, minute=30))) <= datetime.isoformat(
                datetime.today())[:-7] <= datetime.isoformat(
                datetime.combine(datetime.date(datetime.today()), time(hour=11, minute=00))):
                        result = str(current[0][0][:-1]) + '1'
                        cur.execute('''UPDATE Teens SET attendance = ? WHERE name = ? and surname = ? ''', (result, full_name[0], full_name[1]))
                        spec_status = full_name[0] + ' ' + full_name[1]
                    else:
                        print(current[0][0])
                        result = str(current[0][0][:-1]) + '2'
                        print(result, full_name)
                        cur.execute('''UPDATE Teens SET attendance = ? WHERE name = ? and surname = ? ''',
                                    (result, full_name[0], full_name[1]))
                        spec_status = full_name[0] + ' ' + full_name[1]
                elif current[0][0][-1] == "1":
                    if datetime.isoformat(
                            datetime.combine(datetime.date(datetime.today()),
                                             time(hour=11, minute=00))) <= datetime.isoformat(
                        datetime.today())[:-7] <= datetime.isoformat(
                        datetime.combine(datetime.date(datetime.today()), time(hour=13, minute=00))):
                        result = current[0][0] + '|'
                        cur.execute('''UPDATE Teens SET attendance = ? WHERE name = ? and surname = ?''',
                                    (result, full_name[0], full_name[1]))
                        spec_status = full_name[0] + ' ' + full_name[1]
                    else:
                        spec_status = 'Уже отметили'
                else:
                    spec_status = 'Уже отметили'
                con.commit()
                con.close()
            con = sqlite3.connect("DateBase.db")
            cur = con.cursor()
            a = cur.execute('''SELECT name, surname, attendance FROM teens''').fetchall()
            con.close()
            return render_template('note.html', teens=a, spec_status=spec_status)

        return render_template('note.html', )

if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
    while True:
        if datetime.weekday(datetime.now()) == 6 and datetime.isoformat(
                datetime.combine(datetime.date(datetime.today()), time(hour=8, minute=30))) == datetime.isoformat(
                datetime.today())[:-7]:
            sleeptime.sleep(2)
            con = sqlite3.connect("DateBase.db")
            cur = con.cursor()
            a = cur.execute('''SELECT attendance, name, surname FROM teens''').fetchall()
            for i in a:
                cur.execute('''UPDATE Teens SET attendance = ? WHERE name = ? and surname = ?''', (i[0] + '0', i[1], i[2]))