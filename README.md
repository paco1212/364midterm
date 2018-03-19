# SI364 Midterm

I created a Flask application that allows users save locations and businesses they wish to visit when they get to the city. The user enters a city/address, a general search term (like cofee, nightleife, etc., how much money they are willing to spend (1-4), and the number of reponses they wish to get back from the YELP API. I am using Google's Geocode API and Yelp's API to get the data.

## Getting Started

Navigate to the repository where your .py is at on your local machine using terminal. Once you are in the directory, type "python si364miderm.py runserver" in the terminal/commandline. Open up your prefferend browser on your loca machine. Then go to "http://localhost:5000/". If you'd like, enter your name and it will be stored on your database. Then clikc on the "search for new places". On the page, enter the city/address you will be visiting, the type of activites/businesses you are looking for, the amount of money you want to spend, and the number of responses you would like see. Hit "Get Recommendations". That will redirect you to a page with x amount of listings. At the bottom of the page, you can select one item that you would like to visit. Click on the radio button and hit "submit". That will then redirect you back to the "/locationform" page of the app. If the business was added to your database, it will flash a message. If it is lready stored in your database, it will flash a message saying that. Then you can navigate to the "view all saved cities" link, which will dispaly all the cities/locations that you entered as a search query. Then you can click on a location and hit "go" and it will redirect you to the page that will list all of the saved business/locations that you want to visit at that location.

### Prerequisites

What things you need to install the software and how to install them

```
In your terminal, create a postgres database call 'frgamidterm'
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Flask
Anaconda
python
requests
```



## Authors

* **Francisco "Paco" Gallardo** - *Initial work* - [paco1212](https://github.com/paco1212)
