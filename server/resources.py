from flask_restful import Api, Resource
from flask import request, session
from models import db, User, Student, Teacher, Course, Enrollment
from schemas import (user_schema, student_schema, teacher_schema, 
                     course_schema, ValidationError,
                     validate_user_data, validate_student_data, 
                     validate_teacher_data, validate_course_data, 
                     validate_enrollment_data)
from auth import role_required, login_required

api = Api()
class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        try:
            validate_user_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'User already exists'}, 400
        new_user = User(username=data['username'], email=data['email'], role=data['role'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()
            print("Login attempt with data:", data)  # Debug print

            if not data:
                return {'message': 'No input data provided'}, 400

            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {'message': 'Username and password are required'}, 400

            user = User.query.filter_by(username=username).first()
            print(f"Found user: {user}")  # Debug print

            if user and user.check_password(password):
                session['user_id'] = user.id
                session['role'] = user.role

                response_data = {
                    'message': 'Logged in successfully',
                    'role': user.role,
                    'username': user.username
                }
                print("Login successful:", response_data)  # Debug print
                return response_data, 200

            return {'message': 'Invalid username or password'}, 401

        except Exception as e:
            print(f"Login error: {str(e)}")  # Debug print
            return {'message': 'An error occurred during login'}, 500

class UserLogout(Resource):
    def post(self):
        session.clear()
        return {'message': 'Logged out successfully'}, 200


    @login_required
    @role_required('admin')
    def get(self, user_id=None):
        if user_id:
            user = User.query.get_or_404(user_id)
            return user_schema.dump(user)
        users = User.query.all()
        return user_schema.dump(users, many=True)

    @login_required
    @role_required('admin')
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Remove password from data if it's not provided
        if 'password' not in data:
            data_to_validate = {k: v for k, v in data.items() if k != 'password'}
        else:
            data_to_validate = data
        try:
            validate_user_data(data_to_validate)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Update user fields
        for field in ['username', 'email', 'role']:
            if field in data:
                setattr(user, field, data[field])
        
        if 'password' in data:
            user.set_password(data['password'])
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the user', 'error': str(e)}, 500
        
        return {'message': 'User updated successfully'}
    
    @login_required
    @role_required('admin')
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}

class StudentResource(Resource):
    # @login_required
    # @role_required('admin', 'teacher')
    def get(self, student_id=None):
        if student_id:
            student = Student.query.get_or_404(student_id)
            return student_schema.dump(student)
        students = Student.query.all()
        return student_schema.dump(students, many=True)

    # @login_required
    # @role_required('admin')
    def post(self):
        data = request.get_json()
        try:
            validate_student_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Check if all required fields are present
        required_fields = ['student_id', 'name', 'email']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400
        
        new_student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data['email']
        )
        
        # Add user_id if it's provided
        if 'user_id' in data:
            new_student.user_id = data['user_id']
        
        try:
            db.session.add(new_student)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the student', 'error': str(e)}, 500
        
        return {'message': 'Student created successfully'}, 201
    
    # @login_required
    # @role_required('admin')
    def put(self, student_id):
        student = Student.query.get_or_404(student_id)
        data = request.get_json()
        
        try:
            validate_student_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Update student fields
        for field in ['student_id', 'name', 'email']:
            if field in data:
                setattr(student, field, data[field])
        
        # Handle user_id separately if it's present and different
        if 'user_id' in data and data['user_id'] != student.user_id:
            student.user_id = data['user_id']
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the student', 'error': str(e)}, 500
        
        # Fetch the updated student from the database to confirm changes
        updated_student = Student.query.get(student_id)
        return {'message': 'Student updated successfully', 'student': student_schema.dump(updated_student)}, 200

    # @login_required
    # @role_required('admin')
    def delete(self, student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return {'message': 'Student deleted successfully'}

class TeacherResource(Resource):
    # @login_required
    # @role_required('admin')
    def get(self, teacher_id=None):
        if teacher_id:
            teacher = Teacher.query.get_or_404(teacher_id)
            return teacher_schema.dump(teacher)
        teachers = Teacher.query.all()
        return teacher_schema.dump(teachers, many=True)

    # @login_required
    # @role_required('admin')
    def post(self):
        data = request.get_json()
        try:
            validate_teacher_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        # Check if all required fields are present
        required_fields = ['user_id', 'teacher_id', 'name', 'email']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400
        new_teacher = Teacher(
            user_id=data['user_id'],
            teacher_id=data['teacher_id'],
            name=data['name'],
            email=data['email']
        )

        try:
            db.session.add(new_teacher)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the teacher', 'error': str(e)}, 500

        return {'message': 'Teacher created successfully'}, 201



    # @login_required
    # @role_required('admin')
    def put(self, teacher_id):
        teacher = Teacher.query.get_or_404(teacher_id)
        data = request.get_json()
        
        try:
            # Use partial=True to allow partial updates
            validate_teacher_data(data, partial=True)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Update only the fields that are present in the request
        for field in ['name', 'email', 'teacher_id']:
            if field in data:
                setattr(teacher, field, data[field])
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the teacher', 'error': str(e)}, 500
        
        return {'message': 'Teacher updated successfully'}, 200


    # @login_required
    # @role_required('admin')
    def delete(self, teacher_id):
        teacher = Teacher.query.get_or_404(teacher_id)
        db.session.delete(teacher)
        db.session.commit()
        return {'message': 'Teacher deleted successfully'}

class CourseResource(Resource):
    # @login_required
    # @role_required('admin', 'teacher', 'student')
    def get(self, course_id=None):
        if course_id:
            course = Course.query.get_or_404(course_id)
            return course_schema.dump(course)
        courses = Course.query.all()
        return course_schema.dump(courses, many=True)

    # @login_required
    # @role_required('admin')
    def post(self):
        data = request.get_json()
        
        try:
            validated_data = validate_course_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        new_course = Course(
            course_name=validated_data['course_name'],
            course_code=validated_data['course_code']
        )
        
        if 'teacher_id' in validated_data and validated_data['teacher_id'] is not None:
            teacher = Teacher.query.get(validated_data['teacher_id'])
            if not teacher:
                return {'error': 'Teacher not found'}, 404
            new_course.teachers.append(teacher)
        
        try:
            db.session.add(new_course)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the course', 'error': str(e)}, 500
        
        return {'message': 'Course created successfully', 'id': new_course.id}, 201

    # @login_required
    # @role_required('admin')
    def put(self, course_id):
        course = Course.query.get_or_404(course_id)
        data = request.get_json()
        try:
            validate_course_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        course.course_name = data['course_name']
        course.course_code = data['course_code']
        teacher = Teacher.query.get(data['teacher_id'])
        if teacher:
            course.teachers = [teacher]
        
        db.session.commit()
        return {'message': 'Course updated successfully'}

    # @login_required
    # @role_required('admin')
    def delete(self, course_id):
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return {'message': 'Course deleted successfully'}

class EnrollmentResource(Resource):
    # @login_required
    # @role_required('admin', 'teacher', 'student')
    def get(self, enrollment_id=None):
        user_id = session.get('user_id')
        user_role = session.get('role')
        if enrollment_id:
            enrollment = Enrollment.query.get_or_404(enrollment_id)
            if user_role == 'student' and enrollment.student.user_id != user_id:
                return {'message': 'Unauthorized'}, 403
            elif user_role == 'teacher':
                teacher = Teacher.query.filter_by(user_id=user_id).first()
                if not teacher or enrollment.course not in teacher.courses:
                    return {'message': 'Unauthorized'}, 403
            return self.serialize_enrollment(enrollment)
        # Handle list request
        
        if user_role == 'student':
            student = Student.query.filter_by(user_id=user_id).first()
            if not student:
                return {'message': 'Student not found'}, 404
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        elif user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=user_id).first()
            if not teacher:
                return {'message': 'Teacher not found'}, 404
            enrollments = Enrollment.query.filter(
                Enrollment.course_id.in_([c.id for c in teacher.courses])
            ).all()
        else:  # admin
            enrollments = Enrollment.query.all()

        return [self.serialize_enrollment(e) for e in enrollments]
    def serialize_enrollment(self, enrollment):
        return {
            'id': enrollment.id,
            'student_id': enrollment.student_id,
            'course_id': enrollment.course_id,
            'grade': enrollment.grade,
            'student': self.serialize_student(enrollment.student) if enrollment.student else None,
            'course': self.serialize_course(enrollment.course) if enrollment.course else None
        }
    def serialize_student(self, student):
        if student is None:
            return None
        return {
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
            'email': student.email
        }
    def serialize_course(self, course):
        if course is None:
            return None
        return {
            'id': course.id,
            'course_name': course.course_name,
            'course_code': course.course_code
        }
    # @login_required
    # @role_required('admin', 'teacher')
    def post(self):
        data = request.get_json()
        try:
            validate_enrollment_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        new_enrollment = Enrollment(
            student_id=data['student_id'], 
            course_id=data['course_id']
        )
        if 'grade' in data:
            new_enrollment.grade = data['grade']
        try:
            db.session.add(new_enrollment)
            db.session.commit()
            return {'message': 'Enrollment created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the enrollment', 'error': str(e)}, 500
    # @login_required
    # @role_required('admin', 'teacher')
    def put(self, enrollment_id):
        user_id = session.get('user_id')
        user_role = session.get('role')
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        if user_role == 'teacher':
            teacher = Teacher.query.filter_by(user_id=user_id).first()
            if not teacher or enrollment.course not in teacher.courses:
                return {'message': 'Unauthorized'}, 403
        data = request.get_json()
        try:
            validate_enrollment_data(data)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        if 'grade' in data:
            enrollment.grade = data['grade']
        try:
            db.session.commit()
            return {'message': 'Grade updated successfully'}
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while updating the grade', 'error': str(e)}, 500
    # @login_required
    # @role_required('admin')
    def delete(self, enrollment_id):
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        try:
            db.session.delete(enrollment)
            db.session.commit()
            return {'message': 'Enrollment deleted successfully'}
        except Exception as e:
            db.session.rollback()
            return {'message': 'An error occurred while deleting the enrollment', 'error': str(e)}, 500


# Register resources
api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')  # Add this line
api.add_resource(StudentResource, '/students', '/students/<int:student_id>')
api.add_resource(TeacherResource, '/teachers', '/teachers/<int:teacher_id>')
api.add_resource(CourseResource, '/courses', '/courses/<int:course_id>')
api.add_resource(EnrollmentResource, '/enrollments', '/enrollments/<int:enrollment_id>')