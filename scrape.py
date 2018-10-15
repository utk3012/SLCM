from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import mechanize
import cookielib

app = Flask(__name__)
CORS(app)
cj = cookielib.LWPCookieJar()
br = mechanize.Browser()
br.set_handle_robots(False)

@app.route('/', methods=['GET'])
def index():
    return "Hello World"

def getPage(username, password):
	br.open("http://slcm.manipal.edu/loginForm.aspx")
	br.select_form(nr=0)
	br['txtUserid'] = request.json['username']
	br['txtpassword'] = request.json['password']
	br.set_cookiejar(cj)
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36')]
	br.submit()
	br.open("http://slcm.manipal.edu/Academics.aspx")
	raw = br.response().read()
	soup = BeautifulSoup(raw, "html.parser")
	return soup

@app.route('/attendance', methods=['POST'])
def attendance():
	if not request.json or not 'username' in request.json or not 'password' in request.json:
		return (jsonify({"msg": "invalid request or missing parameters in request", "success": 0}), 400)
	try:
		soup = getPage(request.json['username'], request.json['password'])
		table = soup.find("table" ,id="tblAttendancePercentage")
		if not table:
			return (jsonify({"msg": "Attendance has not been uploaded.", "success": 0}), 400)	
		rows = table.findChildren(['th', 'tr'])
		name = soup.find("span", id="ContentPlaceHolder1_lblAttenName").string
		reg_no = soup.find("span", id="ContentPlaceHolder1_lblAttenEnrollNo").string
		roll_no = soup.find("span", id="ContentPlaceHolder1_lblAttenRollNo").string
		sem = soup.find("span", id="ContentPlaceHolder1_lblAttenSem").string
		att = []
		row_name = ["", "sub_name", "sub_code", "", "total", "present", "absent", "percent"]
		for row in rows:
			cells = row.findChildren('td')
			subj = {}
			if len(cells) > 0:
				for ind, cell in enumerate(cells):
					if ind not in [0, 3]:
						value = cell.string
						subj[row_name[ind]] = value
				att.append(subj)
	except:
		return (jsonify({"msg": "Cannot access SLCM at the moment. Try again later!", "success": 0}), 200)
	else:
		return (jsonify({"name": name, "reg_no": reg_no, "roll_no": roll_no, "sem": sem, "no_of_subs": len(att), "attendance": att}), 200)

@app.route('/marks', methods=['POST'])
def marks():
	if not request.json or not 'username' in request.json or not 'password' in request.json:
		return (jsonify({"msg": "invalid request or missing parameters in request", "success": 0}), 400)
	try:
		soup = getPage(request.json['username'], request.json['password'])
		table = soup.find("table" ,id="tblAttendancePercentage")
		if not table:
			return (jsonify({"msg": "Attendance has not been uploaded.", "success": 0}), 400)
		rows = table.findChildren(['th', 'tr'])
		subj = []
		vals = []
		for row in rows:
			cells = row.findChildren('td')
			if len(cells) > 0:
				vals = []
				for ind, cell in enumerate(cells):
					if ind in [1, 2]:
						value = cell.string
						vals.append(value)
					elif ind > 2:
						continue
				subj.append(vals)
		marks = []
		for sub in subj:
			vals = {}
			vals['Subject'] = sub[0]
			subDiv = soup.find("div", id=sub[1].replace(' ',''))
			subTd = subDiv.find_all("td")
			if not subTd:
				vals['avl'] = False
			else:
				vals['avl'] = True
			vals['Marks'] = []
			for ind, cell in enumerate(subTd):
				vals['Marks'].append(cell.string)
			marks.append(vals)
	except:
		return (jsonify({"msg": "Cannot access SLCM at the moment. Try again later!", "success": 0}), 200)
	else:
		return (jsonify({"marks": marks}), 200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)