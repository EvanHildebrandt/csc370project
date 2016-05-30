from flask import Flask, render_template, request, json
from flask.ext.mysql import MySQL
app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ilikepie111'
app.config['MYSQL_DATABASE_DB'] = 'saiddit'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route("/")
def main():
	cursor.execute("show databases")
	tables = cursor.fetchall()
	return render_template('index.html', tables=tables)

if __name__ == "__main__":
	app.run(debug=True)