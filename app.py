from flask import Flask, flash, render_template, request, redirect
from werkzeug.utils import secure_filename
from pymsgbox import *
import sys
import os
import urllib.request
import subprocess

UPLOAD_FOLDER = '/Volumes/un/Test/UPLOADS'
RESULT_FOLDER = '/Volumes/un/Test/uploads/results'
PROBLEM_FOLDER = '/Volumes/un/Test/TestCases/test_data'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['PROBLEM_FOLDER'] = PROBLEM_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['py', 'txt'])


class TestStructure:
        def __init__(self):
                self.name = ""
                self.scriptName = ""
                self.script = ""
                self.output = ""
                self.error = ""


class Test:
        def __init__(self):
                self.testCase = ""
                self.code = ""
                self.output = ""

class Student:
        def __init__(self):
                self.name = ""
                self.tests = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    testcases = os.listdir(app.config['PROBLEM_FOLDER'])
    return render_template('index.html', Testcases=testcases)


@app.route('/admin/')
def admin_page():
        students = os.listdir(app.config['UPLOAD_FOLDER'])
        studentList = []
        for studentName in students:
                student = Student()
                student.name = studentName
                testPath = os.path.join(app.config['UPLOAD_FOLDER'], studentName)
                codePath = os.path.join(testPath, 'CODE')
                if not os.path.isdir(codePath):
                        continue
                scripts = os.listdir(codePath)
                
                for script in scripts:
                        test = Test()
                        test.code = open(os.path.join(codePath, script)).read()
                        outputPath = os.path.join(testPath, 'OUTPUT')
                        output = script.replace('.py', '.output')
                        test.output = open(os.path.join(outputPath, output)).read()
                        test.testCase = script.rsplit('.', 1)[0]
                        student.tests.append(test)
                
                studentList.append(student)
       
        return render_template('dropdown.html', studentArr=studentList)
        


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        print(request.files['file'].filename, file=sys.stderr)
        if 'file' not in request.files:
            return "Nothing files"

        file = request.files['file']
        if file and allowed_file(file.filename):
            username = request.form['Name']
            print(request.form['Test'], file=sys.stderr)
            folderpath = os.path.join(app.config['UPLOAD_FOLDER'], username)
            if os.path.isdir(folderpath) == False:
                os.makedirs(folderpath)

            codepath = os.path.join(folderpath, 'CODE')
            if os.path.isdir(codepath) == False:
                os.makedirs(codepath)
            uploadfile = request.form['Test'] + '.py'
            uploadfile = secure_filename(uploadfile)
            file.save(os.path.join(codepath, uploadfile))

            script = os.path.join(codepath, uploadfile)
            shell = "python3 " + script
            proc = subprocess.Popen(shell, stdout=subprocess.PIPE, shell=True)
            (output, err) = proc.communicate()
            output_file = uploadfile.rsplit('.', 1 )[0] + '.output'

            outputpath = os.path.join(folderpath, 'OUTPUT')
            if os.path.isdir(outputpath) == False:
                os.makedirs(outputpath)
            open(os.path.join(outputpath, output_file), 'wb').write(output)
            return (output, err)
            # return "successfuly"
        #alert('You can upload only *.py, *.txt!', 'Please upload python script file.')
        return redirect('/')


@app.route('/run')
def run_script():
    script = os.path.join(app.config['UPLOAD_FOLDER'], "myscript.py")
    shell = "python3 " + script
    proc = subprocess.Popen(shell, stdout=subprocess.PIPE, shell=True)
    #output = proc.stout.read()
    (output, err) = proc.communicate()
    return (output, err)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
