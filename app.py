# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# creating engine
engine = create_engine("C:\Users\Paige\Desktop\Class\Module10\Starter_Code\Resources\hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Welcome To The Hawaii Climate Analysis API <br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/temp/start <br/>"
        f"/api/v1.0/temp/start/end <br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session and query for last 12 months of precipitation data
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query precipitation
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert to dictionary format
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create session and query all stations
    session = Session(engine)
    station_data = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations = [station[0] for station in station_data]
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session and query for the dates and temperature observations
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query for most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]

    # Query temperature observations for the previous year at the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert to list of temperature observations
    tobs_list = [{date: temp} for date, temp in tobs_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    # Create session and query for temperature stats
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # If only a start date is provided
    if end is None:
        results = session.query(*sel).filter(Measurement.date >= start).all()
    # If both start and end dates are provided
    else:
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Convert to dictionary format
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)