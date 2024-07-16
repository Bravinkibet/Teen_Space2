from flask import Flask, request, jsonify, session, make_response
from flask_restful import Api, Resource
from flask_cors import CORS
from datetime import datetime
from models import db, User, Club, Event, Announcement  # Assuming these models are defined in models.py

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session encryption
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teen_space.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
api = Api(app)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Content-Type", "Access-Control-Allow-Credentials"])

# Home page
class Index(Resource):
    def get(self):
        return {"index": "Welcome to the Teen Space API"}, 200

api.add_resource(Index, '/')

# Sign up
class Register(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(username=data['username'], password=data['password'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        
        return {"id": new_user.id, "username": new_user.username}, 201

api.add_resource(Register, '/register')

# Sign in
class Login(Resource):
    def options(self):
        response_headers = {
            'Access-Control-Allow-Origin': 'http://localhost:3000',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Credentials',
            'Access-Control-Allow-Credentials': 'true'
        }
        return '', 204, response_headers

    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if not user or user.password != data['password']:
            return {'message': 'Invalid credentials'}, 401

        session['user_id'] = user.id
        session['username'] = user.username
        
        response_data = {
            'message': 'Login successful',
            'user': user.to_dict()
        }

        response_headers = {
            'Access-Control-Allow-Origin': 'http://localhost:3000',
            'Access-Control-Allow-Credentials': 'true'
        }

        return jsonify(response_data), 200, response_headers

api.add_resource(Login, '/login')

# Logout
class Logout(Resource):
    def delete(self):
        session.clear()
        response = make_response({"message": "Successfully logged out"}, 200)
        response.set_cookie('session', '', expires=0)  # Clear session cookie
        return response

api.add_resource(Logout, "/logout")

# Check session
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                return user.to_dict(), 200
        return {}, 401

api.add_resource(CheckSession, "/checksession")

# List of clubs
class Clubs(Resource):
    def get(self):
        clubs = Club.query.all()
        return [{"id": club.id, "name": club.name, "description": club.description} for club in clubs], 200

    def post(self):
        data = request.get_json()
        new_club = Club(name=data['name'], description=data['description'])
        db.session.add(new_club)
        db.session.commit()
        return {"id": new_club.id, "name": new_club.name, "description": new_club.description}, 201

api.add_resource(Clubs, '/clubs', endpoint='clubs_list')

# Find clubs by id (club when clicked)
class ClubByID(Resource):
    def get(self, club_id):
        club = Club.query.filter_by(id=club_id).first()
        if not club:
            return {'message': 'Club not found'}, 404

        events = Event.query.filter_by(club_id=club_id).all()
        announcements = Announcement.query.filter_by(club_id=club_id).all()

        club_data = {
            "id": club.id,
            "name": club.name,
            "description": club.description,
            "events": [{"id": e.id, "name": e.name, "date": e.date.isoformat()} for e in events],
            "announcements": [{"id": a.id, "content": a.content} for a in announcements]
        }
        return club_data, 200

api.add_resource(ClubByID, '/clubs/<int:club_id>')

# User joining a club
class JoinClub(Resource):
    def post(self, club_id):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'User not logged in'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        club = Club.query.get_or_404(club_id)
        user.clubs.append(club)
        db.session.commit()
        return {"message": "Joined club successfully"}, 200

api.add_resource(JoinClub, '/clubs/<int:club_id>/join')

# User leaving a club
class LeaveClub(Resource):
    def post(self, club_id):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'User not logged in'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        club = Club.query.get_or_404(club_id)
        user.clubs.remove(club)
        db.session.commit()
        return {"message": "Left club successfully"}, 200

api.add_resource(LeaveClub, '/clubs/<int:club_id>/leave')

# List of events
class Events(Resource):
    def get(self):
        events = Event.query.all()
        return [{"id": event.id, "name": event.name, "date": event.date.isoformat()} for event in events], 200

    def post(self):
        data = request.get_json()
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'User not logged in'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        new_event = Event(name=data['name'], date=datetime.strptime(data['date'], '%Y-%m-%d'), user_id=user.id, club_id=data['club_id'])
        db.session.add(new_event)
        db.session.commit()
        return {"id": new_event.id, "name": new_event.name, "date": new_event.date.isoformat()}, 201

api.add_resource(Events, '/events')

# Announcements
class Announcements(Resource):
    def get(self):
        announcements = Announcement.query.all()
        return [{'id': announcement.id, 'content': announcement.content} for announcement in announcements], 200

    def post(self):
        data = request.get_json()
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'User not logged in'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        new_announcement = Announcement(content=data['announcement'], club_id=data['club_id'], user_id=user.id)
        db.session.add(new_announcement)
        db.session.commit()
        return {'content': new_announcement.content}, 201

api.add_resource(Announcements, '/announcements')

# Announcements by Club ID
class AnnouncementsByClubId(Resource):
    def get(self, club_id):
        announcements = Announcement.query.filter_by(club_id=club_id).all()
        return [{'id': announcement.id, 'content': announcement.content} for announcement in announcements], 200

api.add_resource(AnnouncementsByClubId, '/club/<int:club_id>/announcements')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
