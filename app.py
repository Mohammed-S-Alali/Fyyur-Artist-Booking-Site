#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import countOf
from re import S
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask.globals import g
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import query, selectin_polymorphic
from wtforms import meta
from forms import *
from flask_migrate import Migrate
from models import db,Venue, Artist, Show
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  

  states_cities = Venue.query.with_entities(Venue.state,Venue.city).distinct().order_by(Venue.state)
  data=[]

  for state_city in states_cities:
    count = 0
    venue_list=[]
    state_city_dict={
      "city":state_city[1],
      "state":state_city[0],
      "venues":venue_list
    }

    for venue in Venue.query.filter_by(state=state_city[0],city=state_city[1]):   
      count = get_num_upcoming_shows_venue(venue_id=venue.id)
      venue_list.append({
        "id":venue.id,
        "name":venue.name,
        'num_upcoming_shows':count
      })

    data.append(state_city_dict)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = str(request.form['search_term'])
  venue_result = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  venue_result_dict = {}
  venue_list = []

  if venue_result.count()>0:
    for venue in venue_result:
      id = venue.id
      name = venue.name
      count = get_num_upcoming_shows_venue(venue_id=venue.id)
      venue_list.append({
        "id":id,
        "name":name,
        "num_upcoming_shows":count
      })
  else:
        venue_list.append({})

  venue_result_dict["count"] = venue_result.count()
  venue_result_dict["data"] = venue_list

  response=venue_result_dict

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

def get_num_upcoming_shows_venue(venue_id):
  """
  This function returns the number of upcoming shows venue by venue Id
  """
  current_time = datetime.now()
  venue_show =  db.session.query(Show).join(Venue,Show.venue_id==venue_id).distinct()
  count = 0
  if venue_show.count() > 0:
    count = venue_show.filter(Show.start_time>current_time).count()
  return count

def get_info_upcoming_shows_venue(venue_id):
  """
  This function returns the required information such as Id, name and image link of artist of upcoming shows, and start time
  by venue Id
  """
  current_time = datetime.now()
  venue_show =  db.session.query(Show).join(Venue,Show.venue_id==venue_id).distinct()
  info_list = []
  if venue_show.count() > 0:
    for artist_id,start_time in venue_show.filter(Show.start_time>current_time).with_entities(Show.artist_id,Show.start_time):
      artist = Artist.query.get(artist_id)
      artist_name = artist.name
      artist_image_link = artist.image_link

      info_list.append({
        "artist_id":artist_id,
        "artist_name":artist_name,
        "artist_image_link":artist_image_link,
        "start_time":str(start_time)
      })

  return info_list

def get_info_past_shows_venue(venue_id):
  """
    This function returns the required information such as Id, name and image link of artist of past shows, and start time 
    by venue Id
  """
  current_time = datetime.now()
  venue_show =  db.session.query(Show).join(Venue,Show.venue_id==venue_id).distinct()
  info_list = []
  if venue_show.count() > 0:
    for artist_id,start_time in venue_show.filter(Show.start_time<current_time).with_entities(Show.artist_id,Show.start_time):
      artist = Artist.query.get(artist_id)
      artist_name = artist.name
      artist_image_link = artist.image_link

      info_list.append({
        "artist_id":artist_id,
        "artist_name":artist_name,
        "artist_image_link":artist_image_link,
        "start_time":str(start_time)
      })

  return info_list

def get_num_past_shows_venue(venue_id):
  """
    This function returns the number of past shows venue by venue Id
  """
  current_time = datetime.now()
  venue_show =  db.session.query(Show).join(Venue,Show.venue_id==venue_id).distinct()
  count = 0
  if venue_show.count() > 0:
    count = venue_show.filter(Show.start_time<current_time).count()
  return count

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter_by(id=venue_id).first()
  if not venue is None:
    flag =  True if venue.seeking_talent == True else False
    data={
      "id":venue_id,
      "name":venue.name,
      "genres":venue.genres,
      "address":venue.address,
      "city":venue.city,
      "state":venue.state,
      "phone":venue.phone,
      "website":venue.website_link,
      "facebook_link":venue.facebook_link,
      "image_link":venue.image_link,
      "past_shows":get_info_past_shows_venue(venue_id=venue.id),
      "upcoming_shows":get_info_upcoming_shows_venue(venue_id=venue.id),
      "past_shows_count":get_num_past_shows_venue(venue_id=venue.id),
      "upcoming_shows_count":get_num_upcoming_shows_venue(venue_id=venue.id)
    }

    if flag:
      data["seeking_talent"]=flag
      data["seeking_description"]=venue.seeking_description
    else:
      data["seeking_talent"]=flag
  else:
    return render_template('error/404.html')

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
      
      venue = Venue()
      form.populate_obj(venue)

      if not venue.seeking_talent:
        venue.seeking_description = ""

      db.session.add(venue)
      db.session.commit()

    # on successful db insert, flash success
      flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue ' + request.form.get('name') + ' was not successfully listed!')
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    delete_venue_ = Venue.query.get(venue_id)
    delete_venue_.delete()
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists_ = Artist.query.all()
  data=[]
  for artist in artists_:
    data.append({
      "id":artist.id,
      "name":artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = str(request.form['search_term'])
  artist_result = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  artist_result_dict = {}
  artist_list = []

  if artist_result.count()>0:
    for artist in artist_result:
      id = artist.id
      name = artist.name
      count = get_num_upcoming_shows_artist(artist_id=artist.id)
      artist_list.append({
        "id":id,
        "name":name,
        "num_upcoming_shows":count
      })
  else:
        artist_list.append({})

  artist_result_dict["count"] = artist_result.count()
  artist_result_dict["data"] = artist_list

  response=artist_result_dict

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

def get_num_upcoming_shows_artist(artist_id):
  """
    This function returns the number of upcoming shows artist by artist Id
  """
  current_time = datetime.now()
  artist_show =  db.session.query(Show).join(Artist,Show.artist_id==artist_id).distinct()
  count = 0
  if artist_show.count() > 0:
    count = artist_show.filter(Show.start_time>current_time).count()
  return count

def get_info_upcoming_shows_artist(artist_id):
  """
    This function returns the required information such as Id, name and image link of venue of upcoming shows, and start time 
    by artist Id
  """
  current_time = datetime.now()
  venue_show =  db.session.query(Show).join(Artist,Show.artist_id==artist_id).distinct()
  info_list = []
  if venue_show.count() > 0:
    for venue_id,start_time in venue_show.filter(Show.start_time>current_time).with_entities(Show.venue_id,Show.start_time):
      venue = Venue.query.get(venue_id)
      venue_name = venue.name
      venue_image_link = venue.image_link

      info_list.append({
        "venue_id":venue_id,
        "venue_name":venue_name,
        "venue_image_link":venue_image_link,
        "start_time":str(start_time)
      })

  return info_list

def get_info_past_shows_artist(artist_id):
  """
    This function returns the required information such as Id, name and image link of venue of past shows, and start time 
    by artist Id
  """
  current_time = datetime.now()
  venue_show =  db.session.query(Show).join(Artist,Show.artist_id==artist_id).distinct()
  info_list = []
  if venue_show.count() > 0:
    for venue_id,start_time in venue_show.filter(Show.start_time<current_time).with_entities(Show.venue_id,Show.start_time):
      venue = Venue.query.get(venue_id)
      venue_name = venue.name
      venue_image_link = venue.image_link

      info_list.append({
        "venue_id":venue_id,
        "venue_name":venue_name,
        "venue_image_link":venue_image_link,
        "start_time":str(start_time)
      })

  return info_list

def get_num_past_shows_artist(artist_id):
  """
    This function returns the number of past shows artist by artist Id
  """
  current_time = datetime.now()
  artist_show =  db.session.query(Show).join(Artist,Show.artist_id==artist_id).distinct()
  count = 0
  if artist_show.count() > 0:
    count = artist_show.filter(Show.start_time<current_time).count()
  return count


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.get(artist_id)
  if not artist is None:
    flag = True if artist.seeking_venue == True else False
    data = {
      "id":artist_id,
      "name":artist.name,
      "genres":artist.genres,
      "city":artist.city,
      "state":artist.state,
      "phone":artist.phone,
      "website":artist.website_link,
      "facebook_link":artist.facebook_link,
      "image_link":artist.image_link,
      "past_shows":get_info_past_shows_artist(artist_id=artist.id),
      "upcoming_shows":get_info_upcoming_shows_artist(artist_id=artist.id),
      "past_shows_count":get_num_past_shows_artist(artist_id=artist.id),
      "upcoming_shows_count":get_num_upcoming_shows_artist(artist_id=artist.id)
    }

    if flag:
      data["seeking_venue"]=flag
      data["seeking_description"]=artist.seeking_description
    else:
      data["seeking_talent"]=flag
  else:
    return render_template('error/404.html')

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  
  artist = Artist.query.get_or_404(artist_id)
  
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)

  if not artist is None:
    name = request.form.get('name')
    genres = request.form.getlist('genres')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    seeking_venue = bool(request.form.get('seeking_venue'))
    image_link = request.form.get('image_link')
    if seeking_venue:
      seeking_description = request.form.get('seeking_description')
    else:
      seeking_description = ""
    
    artist.name=name
    artist.genres=genres
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.website_link=website_link
    artist.facebook_link=facebook_link
    artist.seeking_venue=seeking_venue
    artist.image_link=image_link
    if seeking_venue:
      artist.seeking_description=seeking_description
    else:
      artist.seeking_description=seeking_description

    try:
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  else:
    return render_template('error/404.html')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  # TODO: populate form with values from venue with ID <venue_id>
  
  venue = Venue.query.get_or_404(venue_id)

  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)

  if not venue is None:
    name = request.form.get('name')
    genres = request.form.getlist('genres')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    seeking_talent = bool(request.form.get('seeking_talent'))
    image_link = request.form.get('image_link')
    if seeking_talent:
      seeking_description = request.form.get('seeking_description')
    else:
      seeking_description = ""
    
    venue.name=name
    venue.genres=genres
    venue.address=address
    venue.city=city
    venue.state=state
    venue.phone=phone
    venue.website_link=website_link
    venue.facebook_link=facebook_link
    venue.seeking_talent=seeking_talent
    venue.image_link=image_link
    if seeking_talent:
      venue.seeking_description=seeking_description
    else:
      venue.seeking_description=seeking_description

    try:
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

  else:
    return render_template('error/404.html')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form, meta={'csrf': False})

  if form.validate():
    try:

      artist = Artist()
      form.populate_obj(artist)

      if not artist.seeking_venue:
        artist.seeking_description = ""

      db.session.add(artist)
      db.session.commit()

    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue ' + request.form.get('name') + ' was not successfully listed!')
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  shows_ = Show.query.all()
  data=[]
  for show in shows_:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
      "venue_id":venue.id,
      "venue_name":venue.name,
      "artist_id":artist.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time":str(show.start_time)
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form, meta={'csrf': False})

  if form.validate():
    try:

      show = Show()
      form.populate_obj(show)

      db.session.add(show)
      db.session.commit()  
      
    # on successful db insert, flash success
      flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Show of was not successfully listed!')
    finally:
      db.session.close()
  # e.g., flash('An error occurred. Show could not be listed.')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
