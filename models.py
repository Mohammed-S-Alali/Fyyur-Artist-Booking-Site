from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  genres = db.Column(db.String(120))
  website_link = db.Column(db.String(120))
  is_seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(480), default='')
  shows = db.relationship('Show', backref='venue', lazy=True)

  def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, website, 
          seeking_talent=False, seeking_description=""):
          self.name = name
          self.city = city
          self.state = state
          self.address = address
          self.phone = phone
          self.image_link = image_link
          self.facebook_link = facebook_link
          self.genres = genres
          self.website_link = website
          self.is_seeking_talent = seeking_talent
          self.seeking_description = seeking_description

  def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}>'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String(120))
  is_seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(480), default='')
  shows = db.relationship('Show',backref='artist', lazy=True)

  def __init__(self, name, city, state, phone, genres, image_link, facebook_link, website, 
          seeking_venue=False, seeking_description=""):
          self.name = name
          self.city = city
          self.state = state
          self.phone = phone
          self.image_link = image_link
          self.facebook_link = facebook_link
          self.genres = genres
          self.website_link = website
          self.is_seeking_venue = seeking_venue
          self.seeking_description = seeking_description

  def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_datetime = db.Column(db.DateTime, nullable=False)

  def __init__(self,venue_id,artist_id,start_datetime):
    self.venue_id = venue_id
    self.artist_id = artist_id
    self.start_datetime = start_datetime

  def __repr__(self):
        return f'<Show ID: {self.id}, Venue Id: {self.venue_id}, Artist Id: {self.artist_id}>'