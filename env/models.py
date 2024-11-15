from . import db
from flask_login import UserMixin
from sqlalchemy.orm import validates

class Disciplina(db.Model):
    __tablename__ = 'mateus_disciplina'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)

class Professor(db.Model, UserMixin):
    __tablename__ = 'mateus_professor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256))
    telefone = db.Column(db.String(20))
    usuario = db.Column(db.String(50))
    senha = db.Column(db.String(256))
    disciplina_ministrada = db.relationship("Disciplina", secondary="mateus_professor_disciplina", backref="professores")

    @property
    def is_active(self):
        return True

professor_disciplina = db.Table('mateus_professor_disciplina',
    db.Column('professor_id', db.Integer, db.ForeignKey('mateus_professor.id'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('mateus_disciplina.id'), primary_key=True)
)

class Curso(db.Model):
    __tablename__ = 'mateus_curso'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256))
    disciplinas = db.relationship("Disciplina", secondary="mateus_curso_disciplina", backref="cursos")

    def calcula_carga_horaria(self):
        return sum(disciplina.carga_horaria for disciplina in self.disciplinas)

curso_disciplina = db.Table('mateus_curso_disciplina',
    db.Column('curso_id', db.Integer, db.ForeignKey('mateus_curso.id'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('mateus_disciplina.id'), primary_key=True)
)


class Endereco(db.Model):
    __tablename__ = 'mateus_endereco'
    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(256))
    numero = db.Column(db.Integer)
    bairro = db.Column(db.String(256))
    cep = db.Column(db.String(9))
    complemento = db.Column(db.String(256))

class Aluno(db.Model, UserMixin):
    __tablename__ = 'mateus_aluno'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256))
    cpf = db.Column(db.String(14))
    usuario = db.Column(db.String(50))
    endereco_id = db.Column(db.Integer, db.ForeignKey('mateus_endereco.id'))
    endereco = db.relationship("Endereco", backref="alunos")
    senha = db.Column(db.String(256))
    curso_id = db.Column(db.Integer, db.ForeignKey('mateus_curso.id'))
    curso = db.relationship("Curso")
    curso = db.relationship("Curso", backref="alunos")

    @property
    def is_active(self):
        return True