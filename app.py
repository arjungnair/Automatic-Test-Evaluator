from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import csv
from numpy import genfromtxt
from pathlib import Path
import datetime
import evaluator
from numpy import genfromtxt
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_BINDS'] = {'question':'sqlite:///question.db','test':'sqlite:///test.db'}
app.secret_key = 'hUYF/khi+uGilH1'
db = SQLAlchemy(app)

class Test(db.Model):
    __bind_key__ = 'test'
    test_id = db.Column(db.Integer,primary_key = True)
    test_name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer,primary_key = True)
    question_list = db.Column(db.String(200), nullable=False)

    def __init__(self,test_id,test_name,creator_id,question_list):
        self.test_id = test_id
        self.test_name = test_name
        self.creator_id = creator_id
        self.question_list = question_list

def WriteTestToDb(records):
    for record in records:
        test = Test(record["test_id"],record["test_name"],record["creator_id"],record["question_list"])
        db.session.add(test)
        db.session.commit()

class User(db.Model):
    user_id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    usertype = db.Column(db.Integer,nullable = False)

    def __init__(self,user_id,name,email,password,usertype):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.usertype = usertype
    


def WriteUserToDb(records):
    for record in records:
        user = User(record["user_id"],record["name"],record["email"],record["password"],record["usertype"])
        db.session.add(user)
        db.session.commit()

def DisplayUserFromDb():
    user = User.query.all()
    try:
        app.logger.info(type(user))
    except: 
        app.logger.info("select query Failed")
        
def initdb():
    with open("datasets/userdata.csv") as user_csv:
        data = csv.reader(user_csv, delimiter=',')
        first_line = True
        records=[]
        uid = 10000  
        for i in data:
            if not first_line:

                records.append({
                    "user_id":uid,
                    "name":i[0],
                    "email": i[1],
                    "password": i[2],
                    "usertype": i[3]
                })
            else:
                first_line = False
            uid = uid + 1
            
            
    WriteUserToDb(records)

class Question(db.Model):
    __bind_key__ = 'question'
    question_id = db.Column(db.Integer,primary_key = True)
    questionTitle = db.Column(db.String(200), nullable=False)
    referenceAnswer = db.Column(db.String(1000), nullable=False)
    questionType = db.Column(db.Integer, nullable=False) #0 is MCQ, 1 is fill blanks,2 is match,3 descriptive
    options = db.Column(db.String(200))# Used for mcq and match
    marks = db.Column(db.Integer)

    def __init__(self, question_id,questionTitle,referenceAnswer,questionType,options,marks):
        self.question_id = question_id
        self.questionTitle = questionTitle
        self.referenceAnswer = referenceAnswer
        self.questionType = questionType
        self.options = options
        self.marks = marks

def WriteQToDb(records):
    for record in records:
        question = Question(record["question_id"],record["questionTitle"],record["referenceAnswer"],record["questionType"],record["options"],record["marks"])
        db.session.add(question)
        db.session.commit()

def ExtractQFromDb(question_list):
    questions = []
    for q in question_list:
        questions.append(Question.query.filter_by(question_id = q).first())
    try:
        return questions
    except: 
        question.logger.info("ExtractQFromDb(): question extraction from db Failed")

def evaluatemarks(questionanswer):
    return evaluator.evaluate(questionanswer)

def generateQuestions(no_of_questions):
    q = Question.query.all()
    question_list = []
    for i in range(0,no_of_questions):
        n = random.randint(1001,1001+len(q) - 1)
        if n in question_list:
            i = i - 1
            continue
        else:
            question_list.append(n)
    return question_list

def initQdb():
    with open("datasets/DatasetFinalcsv.csv") as user_csv:
        data = csv.reader(user_csv, delimiter=',')
        first_line = True
        records=[]
        qid = 1000
        for i in data:
            if not first_line:
                qid = qid + 1
                records.append({
                    "question_id":qid,
                    "questionTitle":i[0],
                    "referenceAnswer": i[1],
                    "questionType": int(i[2]),
                    "options":(None if i[3] in (None, "") else i[3]),#only present for mcq and match
                    "marks": (5 if int(i[2])>=2 else 1)#5 for mcq and match, 1 for others, changable afterwards
                })
            else:
                first_line = False
        
    WriteQToDb(records)

@app.route('/student_response',methods=['POST','GET']) 
def student_response():
    score = 0
    max_score = 0
    dcount = 0
    mcqcount = 0
    fillcount = 0
    result = []
    scores = []
    answers= []
    refans = []
    qtype = []
    matchops = []
    try:
        #Getting form data from question.html
        selected_question = request.form.getlist('selectedquestion')
        descanswer = request.form.getlist('descanswer')
        #The option here is the option selected by the student
        option = request.form.getlist("option")
        matchans = request.form.getlist("matchans")
        fillanswer = request.form.getlist("fillanswer")
        result.append(selected_question)
        for i in range(0,len(selected_question)):
            q = Question.query.filter_by(questionTitle = selected_question[i]).first()
            refans.append(q.referenceAnswer)
            qtype.append(q.questionType)
            score = 0
            if q.questionType == 0:#MCQ
                ans = option[mcqcount]
                if option[mcqcount] == q.referenceAnswer:
                    score = score + q.marks
                max_score = max_score + q.marks
                scores.append(score)
                mcqcount = mcqcount + 1
            elif q.questionType == 1:#Fill in the blanks
                ans = fillanswer[fillcount]
                if fillanswer[fillcount] == q.referenceAnswer:
                    score = score + q.marks
                max_score = max_score + q.marks
                scores.append(score)

                fillcount = fillcount + 1
            elif q.questionType == 2:#Match the following
                m = []
                matchops.append(q.options)
                for i in q.referenceAnswer:
                    if i != ',':
                        m.append(i)
                l = len(m)
                ans = matchans
                for i in range(0,l):
                    if matchans[i] == m[i]:
                        score = score + q.marks/l
                max_score = max_score + q.marks
                scores.append(score)


            else:#Descriptive
                
                response = []
                ans = descanswer[dcount]
                response.append(ans)
                response.append(q.questionTitle)
                response.append(q.referenceAnswer)

                try:
                    markObtained = round(evaluatemarks(response)*q.marks,0) #executes function in evaluator.py and returns marks
                    score = score + markObtained
                    max_score = max_score + q.marks
                    dcount = dcount + 1
                except:
                    app.logger.info("descriptive answer evaluation error")
                scores.append(score)
                app.logger.info(score)
            answers.append(ans)
    except:
        app.logger.info("Failed to submit data")
    result.append(refans)
    result.append(answers)
    result.append(qtype)
    result.append(matchops)
    result.append(scores)
    result.append(max_score)
    return render_template('display.html',response = [result])#Page after answer submission
        
@app.route('/',methods=['POST','GET'])   
def index():
    #Question Database
    my_file_question = Path("question.db")
    if my_file_question.is_file():
        # file exists
        app.logger.info("question db exists")
    else:
        app.logger.info("Initializing question db...")
        db.create_all(bind = 'question')
        initQdb()
    #Test Database
    my_file_test = Path("test.db")
    if my_file_question.is_file():
        # file exists
        app.logger.info("test db exists")
    else:
        app.logger.info("Initializing test db...")
        db.create_all(bind='test')    
    #Creating User Database
    my_file_user = Path("main.db")
    if my_file_user.is_file():
        # file exists
        app.logger.info("user db exists")
    else:
        app.logger.info("Initializing user db...")
        
         #creates db,initializes values
        db.create_all()
        initdb()
    #DisplayUserFromDb()#testing
    return redirect('/login')

    """  question_list = [1007,1036,1037,1021,1038]
    questions = ExtractQFromDb(question_list)
    #question.logger.info(question_list)
    return render_template('question.html',questions = [questions]) """
    #return render_template('index.html',records=[records])#dictionaries can't be passed
    
@app.route('/login',methods=['POST','GET'])   
def login(): 
    session.pop('email', None)      #sign out if already signed in
    session.pop('name', None)
    session.pop('usertype', None)
    if request.method == "POST":
        
        if request.form.get("login"):
            email = request.form['email']
            password = request.form['password']
            if email == "":
                return render_template('login.html', error = "Enter a valid e-mail ID!")
            if password == "":
                return render_template('login.html', error = "Enter a password!")

            record = db.session.query(User.email, User.password, User.usertype, User.name).filter_by(email=email).first()
        
            if record is None:
                return render_template('login.html', error = "Account not found.")
            if record.password != password:
                return render_template('login.html', error = "Incorrect password.")
            else:
                session['email'] = email
                session['usertype'] = record.usertype
                session['name'] = record.name
                #return render_template('login.html', error = "Logged in!")
                return redirect('/dashboard')
        if request.form.get("signup"):
            return redirect('/signup')

    return render_template('login.html', error = " ")
    
@app.route('/createtest',methods=['POST','GET'])  
def create_test():
    if request.method == "POST":
        if request.form.get("cancel"):
            return redirect('/dashboard')
        if request.form.get("createtest"):
            test_name = request.form['testname']
            no_of_questions = request.form['qno']
            if test_name == "":
                return render_template('createtest.html', error = "Enter a valid test name!")
            if no_of_questions == "":
                return render_template('createtest.html', error = "Enter a valid no of questions!")
            question_list = generateQuestions(int(no_of_questions))
            app.logger.info(question_list)
            string_ints = [str(i) for i in question_list]
            qlist = ",".join(string_ints)
            app.logger.info(qlist)
            x = Test.query.all()
            app.logger.info(x)
            if not x:
                testid = 1
            else:
                testid = db.session.query(Test.test_id).order_by(Test.test_id.desc()).first().test_id + 1
            u = User.query.filter_by(email = session['email']).first()
            records=[]    
            records.append({
                "test_id":testid,
                "test_name":test_name,
                "creator_id": u.user_id,
                "question_list": qlist,
                })
            app.logger.info(records)    
            WriteTestToDb(records)
            return redirect('/dashboard')
            

    return render_template('createtest.html')

@app.route('/viewtest',methods=['POST','GET'])   
def viewtest(): 
    if request.method == "POST":
        if request.form.get("Cancel"):
            pass
        if request.form["view"]:
            x = request.form["view"]
            question_list = map(int, x.split(','))
            questions = ExtractQFromDb(question_list)
    app.logger.info(question_list)
    return render_template('question.html',questions = [questions])

@app.route('/signup',methods=['POST','GET'])   
def signup(): 
    if request.method == "POST":
        
        if request.form.get("back"):
            return redirect('/login')
            
        if request.form.get("signup"):
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            if email == "":
                return render_template('register.html', error = "Enter a valid e-mail ID!")
            if name == "":
                return render_template('register.html', error = "Enter your name!")
            if password == "":
                return render_template('register.html', error = "Enter a password!")
            if request.form['usertype'] == 'student':
                usertype = 1
            else:
                usertype = 2

            record = db.session.query(User.email).filter_by(email=email).first()

            if record is None:
                uid = db.session.query(User.user_id).order_by(User.user_id.desc()).first().user_id + 1
                records=[]    
                records.append({
                    "user_id":uid,
                    "name":name,
                    "email": email,
                    "password": password,
                    "usertype": usertype
                    })
                WriteUserToDb(records)
   
                return render_template('login.html', error = "Account created.")
   
            else:
                return render_template('register.html', error = "An account associated with this e-mail ID already exists.")

    return render_template('register.html', error = " ")
    
@app.route('/dashboard',methods=['POST','GET'])   
def dashboard(): 
    if session['usertype'] == 1:
        return render_template('student_dash.html', username = session['name'])
    
    elif session['usertype'] == 2:
        response = []
        response.append(session['name'])
        u = User.query.filter_by(email = session['email']).first()
        tests = Test.query.filter_by(creator_id = u.user_id)
        for test in tests:
            response.append({"test_id":test.test_id,
                "test_name":test.test_name,
                "creator_id": test.creator_id,
                "question_list": test.question_list
                })

        return render_template('teacher_dash.html', info = [response])
  
if __name__ == "__main__":
    app.run(debug=True)
 

    
    
    


