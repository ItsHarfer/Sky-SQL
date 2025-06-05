"""
flights_data.py

This module provides query functions for accessing flight, airline, and airport delay data
from a SQLite database using SQLAlchemy. It includes predefined SQL statements and helper
functions for querying flights by ID, date, airline, or airport, as well as retrieving
all airlines and calculating delays.

Functions:
- execute_query: Executes a given SQL query with parameters.
- get_all_airlines: Returns a list of all unique airline names.
- get_all_flights_by_airline: Retrieves all flights for a given airline.
- get_flight_by_id: Retrieves flight details based on a specific flight ID.
- get_flights_by_date: Returns all flights scheduled on a given date.
- get_delayed_flights_by_airline: Returns all delayed flights (≥20 min) for a specific airline.
- get_delayed_flights_by_airport: Returns all delayed flights (≥20 min) from a given airport.

This module assumes the underlying SQLite database uses consistent field naming across
flights, airlines, and airports tables. Unexpected schema changes may cause query failures.
"""

from sqlalchemy import create_engine, text

# SQL Queries
QUERY_FLIGHT_BY_ID = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE flights.ID = :id"
QUERY_FLIGHTS_BY_DATE = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE DAY = :day AND MONTH = :month AND YEAR = :year"
QUERY_FLIGHTS_BY_AIRLINE = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE airlines.airline = :airline AND (flights.DEPARTURE_DELAY IS NOT NULL AND flights.DEPARTURE_DELAY != '' AND flights.DEPARTURE_DELAY >= 20);"
QUERY_FLIGHTS_BY_AIRPORT = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id JOIN airports ON flights.ORIGIN_AIRPORT = airports.IATA_CODE WHERE airports.IATA_CODE = :airport AND (flights.DEPARTURE_DELAY IS NOT NULL AND flights.DEPARTURE_DELAY != '' AND flights.DEPARTURE_DELAY >= 20);"
QUERY_ALL_FLIGHTS_BY_AIRLINE = """SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE airlines.airline = :airline;"""
QUERY_ALL_AIRLINES = "SELECT DISTINCT airline FROM airlines ORDER BY airline;"

# Define the database URL
DATABASE_URL = "sqlite:///data/flights.sqlite3"

# Create the engine
engine = create_engine(DATABASE_URL)


def execute_query(query, params):
    """
    Executes an SQL query using the provided parameter dictionary
    and returns the resulting records.

    :param query: The SQL query string to execute.
    :param params: A dictionary of named query parameters to bind to the SQL.
    :return: A list of records (typically Row or RowMapping objects); returns an empty list if an error occurs.
    """
    try:
        with engine.connect() as conn:
            results = conn.execute(text(query), params)
            rows = results.fetchall()
            return rows

    except Exception as e:
        print("Query error:", e)
        return []


def get_all_airlines():
    """
    Retrieves a list of all available airline names from the database.
    :return: A list of airline names (as strings).
    """
    rows = execute_query(QUERY_ALL_AIRLINES, {})
    return [row[0] for row in rows]


def get_all_flights_by_airline(airline_input: str):
    """
    Retrieves all flights for a specific airline, regardless of delay.

    :param airline_input: Name of the airline as stored in the 'airlines.airline' field.
    :return: List of flight records for the given airline.
    """
    params = {"airline": airline_input}
    return execute_query(QUERY_ALL_FLIGHTS_BY_AIRLINE, params)


def get_flight_by_id(flight_id):
    """
    Retrieves flight details by flight ID.

    :param flight_id: The unique ID of the flight to look up.
    :return: A list containing a single flight record if found, otherwise an empty list.
    """
    params = {"id": flight_id}
    return execute_query(QUERY_FLIGHT_BY_ID, params)


def get_flights_by_date(day: int, month: int, year: int):
    """
    This function retrieves all flights scheduled for a specific date by querying the database
    using the provided day, month, and year. It returns a list of matching flight records.

    :param day: The day of the month (1–31) to filter flights.
    :param month: The month of the year (1–12) to filter flights.
    :param year: The four-digit year (e.g., 2015) to filter flights.
    :return:
    """
    params = {"day": day, "month": month, "year": year}
    return execute_query(QUERY_FLIGHTS_BY_DATE, params)


def get_delayed_flights_by_airline(airline_input: str):
    """
    Retrieves all delayed flights (with a delay of 20 minutes or more) for a specific airline.

    :param airline_input: The airline name or code used to filter the flights.
    :return: A list of flight records matching the airline and delay criteria.
    """
    params = {"airline": airline_input}
    return execute_query(QUERY_FLIGHTS_BY_AIRLINE, params)


def get_delayed_flights_by_airport(airport_input: str):
    """
    Retrieves all flights with a departure delay of 20 minutes or more
    originating from the specified airport.

    :param airport_input: The IATA code of the airport used to filter delayed flights (e.g., "JFK").
    :return: A list of delayed flight records from the given airport.
    """
    params = {"airport": airport_input}
    return execute_query(QUERY_FLIGHTS_BY_AIRPORT, params)
