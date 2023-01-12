import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)
#Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#Flask Setup``
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create our session(link) from Python to the DB
    session = Session(engine)

    """Return the JSON representation of your dictionary"""
    recent_date = dt.date(2017, 8 ,23)
    yr_ago = recent_date - dt.timedelta(days=365)
    twelve_month_prcp = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date > yr_ago).\
    order_by(measurement.date).all()

    session.close()

    #Convert query into dictionary using dict comphrension
    prcp = {date: prcp for date, prcp in twelve_month_prcp}

    return jsonify(prcp)

@app.route('/api/v1.0/stations')
def stations():
    #Create our session(link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    active_stations = session.query(station.station,station.name).all()

    session.close()

    station_names = {station: name for station, name in active_stations}

    return jsonify(station_names)

@app.route('/api/v1.0/tobs')
def tobs():
    #Create our session(link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) 
    for the previous year."""
    recent_date = dt.date(2017, 8 ,23)
    yr_ago = recent_date - dt.timedelta(days=365)
    previous_yr = (session.query(measurement.date, measurement.tobs)
                .filter(measurement.station == 'USC00519281')
                .filter(measurement.date <= recent_date)
                .filter(measurement.date >= yr_ago)
                .order_by(measurement.tobs).all())

    session.close()

    prevyr = {date: tobs for date, tobs in previous_yr}

    return jsonify(prevyr)

@app.route('/api/v1.0/<start>') 
def start(start):
    #Create our session(link) from Python to the DB
    session = Session(engine)

    all_tobs = (session.query(measurement.tobs)
                .filter(measurement.date.between(start, '2017-08-23')).all())
    
    session.close()

    tobs_df = pd.DataFrame(all_tobs)

    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()
    
    return jsonify(tavg, tmax, tmin)

@app.route('/api/v1.0/<start>/<end>') 
def startend(start, end):
    #Create our session(link) from Python to the DB
    session = Session(engine)
    
    tobs_only = (session.query(measurement.tobs)
                .filter(measurement.date.between(start, end)).all())
    
    session.close()

    tobs_df = pd.DataFrame(tobs_only)

    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()
    
    return jsonify(tavg, tmax, tmin)

if __name__ == '__main__':
    app.run(debug=True)

