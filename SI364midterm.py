# Francisco Gallardo
# SI 364 - Building Interactive Applications
# Midterm Assignment

###############################
####### SETUP (OVERALL) #######
###############################

# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, ValidationError, TextAreaField, RadioField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell # New
from collections import defaultdict
import requests
import json


## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = "Paco's Application"

## All app.config values
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/frgamidterm"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)
manager = Manager(app)

######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_name(name):
    if Name.query.filter_by(name = name).first():
        flash('{} is already saved in the database'.format(name))
        return Name.query.filter_by(name = name).first()
    else:
        name = Name(name = name)
        db.session.add(name)
        db.session.commit()
        flash('{} was saved in the Database'.format(name))
        return name

# Helper function that will make a request to Google's GEOcode API to get the coordiantes of a dity or address
def get_location_coordinates(query):
	GEOCODE_APIKEY = 'AIzaSyA9r92obBJRGRV_lcZA9zMSo4lP10Z3bcY'
	google_url = 'https://maps.googleapis.com/maps/api/geocode/json'
	params = {'key': GEOCODE_APIKEY, 'address':query}
	# making request
	resp = requests.get(google_url, params)
	data = json.loads(resp.text)
	# If its a location, then return a tuple of latitude and longitude
	try:
		geometry = data['results'][0]['geometry']
		lat = geometry['location']['lat']
		lng = geometry['location']['lng']
		return (lat, lng)
	except:
		return None

# Helper fucntion that will make a request to the YELP API to get location
def get_yelp_results(query, lat, lng, rad = 4000, price = 1, limit = 50):
	# YELP's API requres an APIKEY sent to the HEADERS of the Request
	headers = {'Authorization': 'Bearer 5KEy7KVV3cfdFWQ8IbgmLeBFXui7q13RaQT3q_MYYLJo-FUqCWksbC8tlAqWHWeI7-SEZnjqUT1JDR3TRP-ekHvGpFdMrzCYL_h0Kc1ln_-8m6ddtNq4iIgCBfalWnYx'}
	# Params to make the appropriate request
	params = {'term':query, 'latitude':lat, 'longitude':lng, 'radius':rad, 'limit':limit, 'price':price}
	url = 'https://api.yelp.com/v3/businesses/search'
	# Make the requst to YELP's API
	resp = requests.get(url, params = params, headers = headers)
	data = json.loads(resp.text)
	# Return a JSON object
	return data['businesses']

# Get a JSON object (from Yelp's API) and create a list of tuples
def list_results(jsonobject):
	return [(item['name'], item['location']['display_address'][0], item['price'], item['rating'] )for item in jsonobject]

# Helper function that will create a city in the data base or return an exitsing city
def get_or_create_city(cityname):
	city = City.query.filter_by(city_name = cityname).first()
	if not city:
		city = City(city_name = cityname)
		db.session.add(city)
		db.session.commit()
		return city
	return city


# Helper function that will add YELP results to the database to the Attractions table
def create_recommendations(lst, city):
	if not Attractions.query.filter_by(business_name = lst[1], business_address = lst[2], city_id = city.id).first():
		record = Attractions(business_name = lst[1], business_address = lst[2], price = lst[3], rating = lst[4], city_id = city.id)
		db.session.add(record)
		db.session.commit()
		flash("{} was successfully added!".format(lst[1]))

	else:
		flash('{} is already stored in the data base'.format(lst[1])) 



##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)



class City(db.Model):
	__tablename__ = 'cities'
	id = db.Column(db.Integer, primary_key = True)
	city_name = db.Column(db.String(128))
	businesses = db.relationship('Attractions', backref = 'city')


	def __repr__(self):
		return "{} (ID: {})".format(self.city_name, self.id)



class Attractions(db.Model):
	__tablename__ = 'businesses'
	id = db.Column(db.Integer, primary_key = True)
	business_name = db.Column(db.String(128))
	business_address = db.Column(db.String(256))
	price = db.Column(db.String(4))
	rating = db.Column(db.Float)
	city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))

	def __repr__(self):
		return "{} (ID: {}) | City ID: {}".format(self.business_name, self.id, self.city_id)



###################
###### FORMS ######
###################
def within_range(form, field):
	if len(field.data.split()) > 1:
		raise ValidationError('Money field needs to be a number (1-4)')

	elif len(field.data) > 1:

		raise ValidationError('Wrong Value - Money field needs to be ONE SINGLE number (1-4)')
	try:
		num = int(field.data)
		if (num  not in list(range(1,5))):
			raise ValidationError('Wrong Value - Money field needs to be a within 1 and 4')
	except:
		raise ValidationError('Wrong value - Money field needs to be a number (1-4)')

# 
def results_range(form, field):
	if field.data > 50:
		raise ValidationError('Recommendation Field - Number has to be between 1 and 50')
	elif field.data < 1:
		raise ValidationError('Recommendation Field - Number has to be between 1 and 50')


class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField()

class LocationForm(FlaskForm):
    location = StringField('Please enter a city or adrress.', validators = [Required()])
    query = StringField('Please enter what you are searching for at that city (e.g. cofee, food, nightlife, etc.)', validators = [Required()])
    max_money = StringField('Enter your price range? (1-4, 1 = cheapest, 4 = expensive)',validators = [Required(), within_range])
    num_results = IntegerField('How many recommendations do you want to receive? (Max = 50)', validators = [Required(), results_range])
    submit = SubmitField('Get recommendations')

class addForm(FlaskForm):
	select = RadioField('Add to your database', choices = [])
	submit = SubmitField('Submit')



#######################
##### ERROR FXNS ######
#######################
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

#######################
###### VIEW FXNS ######
#######################

@app.route('/', methods = ['GET', 'POST'])
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        newname = get_or_create_name(name)
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)



@app.route('/names', methods = ['GET', 'POST'])
def all_names():
    names = Name.query.all()
    names = [x.name for x in names]
    return render_template('name_example.html',names=names)



@app.route('/locationform', methods = ['GET', 'POST'])
def enter_location():
	# Form that will display for user to enter a search query
    form = LocationForm()
    # Form2 will load only when I get appropitate data from the API
    form2 = addForm(request.form)

    # Make sure the form sends the correct data
    if form.validate_on_submit():
    	# Get the form's information
        location_query = form.location.data
        search_query = form.query.data
        num_results = form.num_results.data
        max_money = form.max_money.data
        # Make a request to Google's GeoCode API to get the coordinate of the city's search query
        coordinates = get_location_coordinates(location_query)
        # If the coordinates do not exist, flash an error message and redirect the form
        if not coordinates:
        	flash('Location entered was not valid')
        	return redirect(url_for('enter_location'))

        # Make a request to Yelp's API to get data
        yelp_data = get_yelp_results(search_query, coordinates[0],coordinates[1], price = max_money, limit = num_results)

        # Turn the JSON object into a list of tuples, containing information about the places found
        display_data = list_results(yelp_data)

        # Create a list of tuples from the data returned from YELP API
        # Got this idea from https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field
        select_options = [((location_query, place), place[0]) for place in display_data]
        # Update the form's Radio choices based off the lst of tuples I created
        form2.select.choices = select_options
        return render_template('yelp_results.html', items = display_data, form  =  form2)

    # Else, display the original page
    # PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
    	string_errors = " | ".join([str(er) for er in errors])
    	flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
    return render_template('enter_location.html', form = form)



@app.route('/add_search', methods = ['GET', 'POST'])
def add_to_database():

	if request.method == 'GET':
		# Get the user's choices
		select = request.args.get('select')
		# Split the item at all the commas because the option is a string-like tuple
		lis = select.split(",")
		# cleaning up the options from the tuple and adding the clean strings into a list
		info = []
		for item in lis:
			item = item.strip()
			item = item.replace("(", "")
			item = item.replace(")", "")
			if item[0] == "'" and item[-1] == "'":
				item = item[1:-1]
			info.append(item)

		# Create or get a city from the City model
		city = get_or_create_city(info[0].upper())

		# Add the location to the Attraction's model
		create_recommendations(info, city)
		return redirect(url_for('enter_location'))

	return redirect(url_for('view_all_cities'))



@app.route('/all_cities', methods = ['GET', 'POST'])
def view_all_cities():
	# Display all the cities in an HTML template
	cities = City.query.all()
	city_names = [city.city_name for city in cities]
	return render_template('view_cities.html', cities = city_names)

        

@app.route('/view/<city>', methods = ['GET', 'POST'])
def view_cities(city):
	
	if request.method == 'GET':
		# Get the argument that was pass in through the HTML form
		d = request.args.get('city', None)
		if not d:
			return redirect(url_for('view_all_cities'))
		# reassigning the city's name to the city variable so that the url could display the city
		city = d
		# Make a query to the City model table to get the object in the table
		city_obj = City.query.filter_by(city_name = d).first()
		# use the city object's id to make a query to the Attractions Model table
		# Grab all of the items that are linked to to the city object's id
		attractions = Attractions.query.filter_by(city_id = city_obj.id).all()

		# Create a list of tuples, containing the information stored for that specific city chosen
		attraction_details = []
		for x in attractions:
			tup = (x.business_name, x. business_address, x.price, x.rating)
			attraction_details.append(tup)
		# Display the city and the locations stored in an HTML page
		return render_template('display_recommendations.html', city = city, locations = attraction_details)

	# Do the same thing descibed above, but in a POST methdod
	elif request.method == 'POST':
		d = request.form['city']
		city = d
		city_obj = City.query.filter_by(city_name = d).first()
		attractions = Attractions.query.filter_by(city_id = city_obj.id).all()
		attraction_details = []
		for x in attractions:
			tup = (x.business_name, x. business_address, x.price, x.rating)
			attraction_details.append(tup)
		return render_template('display_recommendations.html', city = city, locations = attraction_details)



if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    # app.run(use_reloader=True,debug=True) # The usual
    manager.run()
