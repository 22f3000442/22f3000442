from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
api = Api(app)
db = SQLAlchemy(app)

# Database Models
class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Enrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# Error Codes
class ErrorCode:
    COURSE001 = {'code': 'COURSE001', 'message': 'Course Name is required'}
    COURSE002 = {'code': 'COURSE002', 'message': 'Course Code is required'}
    STUDENT001 = {'code': 'STUDENT001', 'message': 'Roll Number required'}
    STUDENT002 = {'code': 'STUDENT002', 'message': 'First Name is required'}
    ENROLLMENT001 = {'code': 'ENROLLMENT001', 'message': 'Course does not exist'}
    ENROLLMENT002 = {'code': 'ENROLLMENT002', 'message': 'Student does not exist.'}

# Resources

class CourseResource(Resource):
    def get(self, course_id):
    # Retrieve a specific course by course_id
        course = Course.query.get(course_id)
        if course:
            return {'course_id': course.course_id, 'course_name': course.course_name,
                    'course_code': course.course_code, 'course_description': course.course_description}
        else:
            return {'message': 'Course not found'}, 404
    def post(self):
        data = request.get_json()
        if not data.get('course_name'):
            return ErrorCode.COURSE001, 400
        if not data.get('course_code'):
            return ErrorCode.COURSE002, 400
        new_course = Course()
        new_course.course_name = data['course_name']
        new_course.course_code = data['course_code']
        new_course.course_description = data.get('course_description', '')
          # Add the new course to the database
        db.session.add(new_course)
        db.session.commit()

        return {'message': 'Course created successfully','course_id': new_course.course_id}, 201
          
class EnrollmentResource(Resource):
   def get(self, enrollment_id=None):
     # Retrieve a specific enrollment by enrollment_id
     enrollment = Enrollment.query.get(enrollment_id)
     if enrollment:
        return {'enrollment_id': enrollment.enrollment_id, 'student_id': enrollment.student_id,
                     'course_id': enrollment.course_id}
     else:
         return {'message': 'Enrollment not found'}, 404
     
   def post(self):
        data = request.get_json()
        # Check if course exists
        course = Course.query.filter_by(course_id=data.get('course_id')).first()
        if not course:
            return ErrorCode.ENROLLMENT001, 404

        # Check if student exists
        student = Student.query.filter_by(student_id=data.get('student_id')).first()
        if not student:
            return ErrorCode.ENROLLMENT002, 404
       
        new_enrollment = Enrollment()
        new_enrollment.student_id = data['student_id']
        new_enrollment.course_id = data['course_id']
        # Add the new enrollment to the database
        db.session.add(new_enrollment)
        db.session.commit()

        return {'message': 'Enrollment created successfully', 'enrollment_id': new_enrollment.enrollment_id}, 201

class StudentResource(Resource):
  def get(self, student_id):
    # Retrieve a specific student by student_id
    student = Student.query.get(student_id)
    if student:
        return {'student_id': student.student_id, 'roll_number': student.roll_number,
                'first_name': student.first_name, 'last_name': student.last_name}
    else:
        return {'message': 'Student not found'}, 404

  def post(self):
      data = request.get_json()
      if not data.get('roll_number'):
          return ErrorCode.STUDENT001, 400
      if not data.get('first_name'):
          return ErrorCode.STUDENT002, 400
      new_student = Student()
      new_student.roll_number = data['roll_number']
      new_student.first_name = data['first_name']
      new_student.last_name = data.get('last_name', '')

      db.session.add(new_student)
      db.session.commit()

      return {'message': 'Student created successfully', 'student_id': new_student.student_id}, 201

api.add_resource(CourseResource, '/courses', '/courses/<int:course_id>')
api.add_resource(EnrollmentResource, '/enrollments', '/enrollments/<int:enrollment_id>')
api.add_resource(StudentResource, '/students', '/students/<int:student_id>')

def run():
    app.run(debug=True)

if __name__ == '__main__':
    run()
