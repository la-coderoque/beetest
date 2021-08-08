from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'qwerty'
app.config.from_object('config.Config')

admin = Admin(app, name='EventReg', template_mode='bootstrap3')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

registration_table = db.Table(
    'registrations',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    events = db.relationship(
        'Event', secondary=registration_table, back_populates='users'
    )


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    users = db.relationship(
        'User', secondary=registration_table, back_populates='events'
    )


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Event, db.session))

class EventAPI(MethodView):
    def get(self, event_id):
        if event_id is None:
            events = Event.query.all()
            resp = []
            for event in events:
                resp.append(
                    {
                        'id': event.id,
                        'title': event.title,
                        'description': event.description,
                        'date': str(event.date),
                        'users': True if event.users else False
                    }
                )
            return jsonify(resp)
        else:
            event = Event.query.get(event_id)
            if not event:
                return {}
            return {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': str(event.date),
                'users': [
                    {'id': user.id, 'name': user.name}
                    for user in event.users
                ]
            }

    def put(self):
        json_in = request.json
        event_id = json_in.get('event_id')
        users = json_in.get('users', [])
        if not event_id:
            return 'Не передан обязательный параметр "event_id"', 400
        
        event = Event.query.get(event_id)
        if not event:
            return 'Мероприятие не найдено', 400

        registred_users = [user.id for user in event.users]

        for user_id in users:
            user = User.query.get(user_id)
            if user and user.id not in registred_users:
                event.users.append(user)
        
        db.session.commit()

        return self.get(event_id)


event_view = EventAPI.as_view('events')
app.add_url_rule(
    '/events/', view_func=event_view,
    defaults={'event_id': None}, methods=['GET']
)
app.add_url_rule(
    '/events/<int:event_id>', view_func=event_view, methods=['GET']
)
app.add_url_rule(
    '/events/registration/', view_func=event_view, methods=['PUT']
)

if __name__ == '__main__':
    app.run(debug=True)
