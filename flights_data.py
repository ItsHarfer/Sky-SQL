from sqlalchemy import create_engine, text

QUERY_FLIGHT_BY_ID = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE flights.ID = :id"
QUERY_FLIGHTS_BY_DATE = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE DAY = :day AND MONTH = :month AND YEAR = :year"
QUERY_FLIGHTS_BY_AIRLINE = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id WHERE airlines.airline = :airline AND (flights.DEPARTURE_DELAY IS NOT NULL AND flights.DEPARTURE_DELAY != '' AND flights.DEPARTURE_DELAY >= 20);"
QUERY_FLIGHTS_BY_AIRPORT = "SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY FROM flights JOIN airlines ON flights.airline = airlines.id JOIN airports ON flights.ORIGIN_AIRPORT = airports.IATA_CODE WHERE airports.IATA_CODE = :airport AND (flights.DEPARTURE_DELAY IS NOT NULL AND flights.DEPARTURE_DELAY != '' AND flights.DEPARTURE_DELAY >= 20);"

# Define the database URL
DATABASE_URL = "sqlite:///data/flights.sqlite3"

# Create the engine
engine = create_engine(DATABASE_URL)


def execute_query(query, params):
    """
    Execute an SQL query with the params provided in a dictionary,
    and returns a list of records (dictionary-like objects).
    If an exception was raised, print the error, and return an empty list.
    """
    try:
        with engine.connect() as conn:
            results = conn.execute(text(query), params)
            rows = results.fetchall()
            return rows

    except Exception as e:
        print("Query error:", e)
        return []


def get_flight_by_id(flight_id):
    """
    Searches for flight details using flight ID.
    If the flight was found, returns a list with a single record.
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
