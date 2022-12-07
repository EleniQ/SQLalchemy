
# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

measurement1 = Base.classes.measurement
station1 = Base.classes.station

app = Flask(__name__)

# Start at the homepage
# List all the available routes
@app.route("/")
def Welcome():
    """List available api routes."""
    return (
        f"All Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Complete List of Stations: /api/v1.0/stations<br/>"
        f"Temperature Over one year: /api/v1.0/tobs<br/>"
        f"Temperature from the start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature from start date to end date: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


# Route 1 '/api/v1.0/precipitation'
# Convert the query results from your precipitation analysis 
# to a dictionary using date as the key and prcp as the value.
#prcp is value
@app.route('/api/v1.0/precipitation')

def precipitation():
    session= Session(engine)
    queryp= [measurement1.date,measurement1.prcp]
    queryresultp= session.query(*queryp).all()
    session.close()

    precipitation= [] # list to append
    for date, prcp in queryresultp:
        pdict= {} #not list !!
        pdict["Date in YYYY-MM-DD Format"] = date
        pdict["Precipitation in Inches"] = prcp
        precipitation.append(pdict)
    return jsonify(precipitation)

# Return a JSON list of stations from the dataset. #station,name,lat,long,elevation
@app.route('/api/v1.0/stations')
def stations():
    session= Session(engine)
    querys= [station1.station,station1.name,station1.latitude,station1.longitude,station1.elevation]
    queryresults= session.query(*querys).all()
    session.close()

    stations= [] #list not function 
    for station,name,lat,long,elevation in queryresults:
        sdict= {}
        sdict["Station ID"] = station
        sdict["Station Name"] = name
        sdict["Latitude of Station"] = lat
        sdict["Longitude of Station"] = long
        sdict["Elevation of Station"] = elevation
        stations.append(sdict)

    return jsonify(stations)


# Route 3 '/api/v1.0/tobs'
# Query the dates and temperature observations of the most-active 
# station for the previous year of data.
#earlier, 1 year after? changing original code from measurement to measurement1 ?
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    recdate = session.query(measurement1.date).order_by(measurement1.date.desc()).first()
    recdate1 = dt.datetime.strptime(recdate[0], '%Y-%m-%d')
    yeardate = dt.date(recdate1.year -1, recdate1.month, recdate1.day)
    queryt = [measurement1.date,measurement1.tobs]
    queryresultt = session.query(*queryt).filter(measurement1.date >= yeardate).all()
    session.close()

    tobslist = []
    for date, tobs in queryresultt:
        tdict = {}
        tdict["Date in YYYY-MM-DD Format"] = date
        tdict["TOBS"] = tobs
        tobslist.append(tdict)
    return jsonify(tobslist)


# Route 4 '/api/v1.0/<start>' and '/api/v1.0/<start>/<end>'
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
@app.route('/api/v1.0/<start>')
def startdate(start):
    session = Session(engine)
    queryresultstart = session.query(func.min(measurement1.tobs), func.avg(measurement1.tobs), func.max(measurement1.tobs)).filter(measurement1.date >= start).all()
    session.close()

    tobslist1 = []
    for min,avg,max in queryresultstart:
        tdict1 = {}
        tdict1["Minimum Temperature"] = min
        tdict1["Average Temperature"] = avg
        tdict1["Maximum Temperature"] = max
        tobslist1.append(tdict1)

    return jsonify(tobslist1)

    #route5
@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresultss = session.query(func.min(measurement1.tobs), func.avg(measurement1.tobs), func.max(measurement1.tobs)).\
        filter(measurement1.date >= start).filter(measurement1.date <= stop).all()
    session.close()

    tobslist2 = []
    for min,avg,max in queryresultss:
        tdict2 = {}
        tdict2["Minimum Temperature"] = min
        tdict2["Average Temperature"] = avg
        tdict2["Maximum Temperature"] = max
        tobslist2.append(tdict2)

    return jsonify(tobslist2)


if __name__ == '__main__':
    app.run(debug=True)  