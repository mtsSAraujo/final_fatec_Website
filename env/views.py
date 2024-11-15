from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from .models import Curso, Aluno, Professor, Disciplina
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)

@views.route("/cursos")
def cursos():
    courses = Curso.query.all()
    enrolled_course_id = None
    if session.get('user_type') == 'aluno':
        enrolled_course_id = current_user.curso_id 
    return render_template("courses.html", user=current_user, courses=courses, enrolled_course_id=enrolled_course_id)

@views.route("/alunos")
def alunos():
    students = Aluno.query.all()
    enrolled_course_id = None
    if session.get('user_type') == 'aluno':
        enrolled_course_id = current_user.curso_id 
    return render_template("students.html", user=current_user, students=students, enrolled_course_id=enrolled_course_id)

@views.route("/professores")
def professors():
    professors = Professor.query.all()
    return render_template("teachers.html", user=current_user, professors= professors)

@views.route("/disciplinas")
def disciplinas():
    disciplines = Disciplina.query.all()
    return render_template("disciplines.html", user = current_user, disciplines=disciplines)