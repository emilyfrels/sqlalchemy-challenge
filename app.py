#import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt


#import flask and jsonify
from flask import Flask, jsonify

#############################################################
#                      DATABASE SETUP                       #
#############################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()

#reflect tables
Base.prepare(engine, reflect=True)

#save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#############################################################
#                       FLASK SETUP                        #
#############################################################

#create an app
app = Flask(__name__)

#Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page. ")
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#Define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

    #create session link
    session = Session(engine)

    
    # find the latest date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # calculate the date 1 year ago from last date in database
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    last_year_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.date <= '2017-08-23').all()

    #close session
    session.close()


    # Convert the query results to a dictionary using date as the key and prcp as the value.
    last_year = []

    for date, prcp in last_year_data:
        last_year_dict = {}
        last_year_dict["date"] = date
        last_year_dict["prcp"] = prcp
        last_year.append(last_year_dict)



    #Return the JSON representation of your dictionary.
    return jsonify(last_year)


#Define stations route
@app.route("/api/v1.0/stations")
def stations():

    #create session link
    session = Session(engine)

    #return a JSON list of stations from the dataset

    results = session.query(Station.station).all()

    #close session
    session.close()

    #convert to normal list
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)


#Define tobs route
@app.route("/api/v1.0/tobs")
def tobs():

    #create session link
    session = Session(engine)

    most_active_weather_station = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.date <= '2017-08-23').all()


    #close session
    session.close()

    most_active= []

    for date, tobs in most_active_weather_station:
        most_active_dict = {}
        most_active_dict["date"] = date
        most_active_dict["tobs"] = tobs
        most_active.append(most_active_dict)
    return jsonify(most_active)


#Define start route
@app.route("/api/v1.0/<start>")
def start(start):

    #create session link
    session = Session(engine)



    most_active_weather_station = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').all()

    search_term = start
    


    #close session
    session.close()

    # find lowest, highest, and avg temp of most active station
    # based on end date
    lowest_temp = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= search_term).scalar()
    
    highest_temp = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= search_term).scalar()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= search_term).scalar()

    for date in most_active_weather_station:
        if start == search_term:
            return(
                f"The lowest temperature is {lowest_temp}<br>"
                f"The highest temperature is {highest_temp}<br>"
                f"The average temperature is {avg_temp}<br>"
            )
    return jsonify({"error": f"Date {start} not found."}), 404

#Define end route
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):

    #create session link
    session = Session(engine)

    most_active_weather_station = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').all()

    search_start = start
    search_end = end



    #close session
    session.close()

    # find lowest, highest, and avg temp of most active station
    # based on start date and end date
    lowest_temp = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= search_start).\
    filter(Measurement.date <= search_end).scalar()
    
    highest_temp = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= search_start).\
    filter(Measurement.date <= search_end).scalar()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= search_start).\
    filter(Measurement.date <= search_end).scalar()

    for date in most_active_weather_station:
        if start == search_start and end == search_end:
            return(
                f"The lowest temperature is {lowest_temp}<br>"
                f"The highest temperature is {highest_temp}<br>"
                f"The average temperature is {avg_temp}<br>"
            )
    return jsonify({"error": f"Dates {start} and {end} not found."}), 404

#run the app
if __name__ == "__main__":
    app.run(debug=True)
