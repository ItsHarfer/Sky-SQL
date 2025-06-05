import inspect
import re

import flights_data
from datetime import datetime
import sqlalchemy
import pandas as pd

IATA_LENGTH = 3


def confirm_csv_export_with_filename(default_filename: str) -> str | None:
    """
    Asks the user whether to export results to CSV.
    Offers a default filename, and lets them override it.

    Returns:
    - A string filename ending with '.csv', or
    - None if the user cancels export.
    """
    while True:
        choice = (
            input("Would you like to export this data to a CSV file? (y/n): ")
            .strip()
            .lower()
        )
        if choice == "y":
            confirm = (
                input(f"Use the default filename '{default_filename}'? (y/n): ")
                .strip()
                .lower()
            )
            if confirm == "y":
                return default_filename
            else:
                custom_filename = input("Enter filename (e.g., results.csv): ").strip()
                if not custom_filename.endswith(".csv"):
                    custom_filename += ".csv"
                return custom_filename
        elif choice == "n":
            return None
        else:
            print("Please enter 'y' or 'n'.")


def save_to_csv(
    data: pd.DataFrame,
    filename: str,
    delimiter: str = ",",
    encoding: str = "utf-8",
    include_index: bool = False,
):
    """
    Saves a DataFrame to a CSV file.

    Parameters:
    - data (pd.DataFrame): The DataFrame to save.
    - filename (str): Name of the CSV file (e.g. 'output.csv').
    - delimiter (str): The delimiter to use in the CSV file (default is comma).
    - encoding (str): File encoding (default is 'utf-8').
    - include_index (bool): Whether to write the DataFrame index (default is False).
    """
    try:
        panda_data = pd.DataFrame(data)
        panda_data.to_csv(
            filename, sep=delimiter, encoding=encoding, index=include_index
        )
        if not filename.endswith(".csv"):
            filename += ".csv"
        print(f"File saved successfully as: {filename}")
    except Exception as e:
        print(f"Error while saving file: {e}")


def export_results_to_csv(prompt: str, results, label: str):
    """
    Sanitizes the label, constructs the filename, asks the user for confirmation, and saves the file.
    """
    safe_label = re.sub(r"[^a-zA-Z0-9]", "_", label.strip().lower())
    filename = confirm_csv_export_with_filename(f"{prompt}{safe_label}.csv")
    if filename:
        save_to_csv(results, filename)


def delayed_flights_by_airline():
    """
    Asks the user for a textual airline name (any string will work here).
    Then runs the query using the data object method "get_delayed_flights_by_airline".
    When results are back, calls "print_results" to show them to on the screen.
    """
    airline_input = input("Enter airline name: ")
    results = flights_data.get_delayed_flights_by_airline(airline_input)
    print_results(results)

    export_results_to_csv("delayed_flights_from_", results, airline_input)


def delayed_flights_by_airport():
    """
    Asks the user for a textual IATA 3-letter airport code (loops until input is valid).
    Then runs the query using the data object method "get_delayed_flights_by_airport".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        # Valide input
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = flights_data.get_delayed_flights_by_airport(airport_input)
    print_results(results)
    export_results_to_csv("delayed_flights_from_airport_", results, airport_input)


def flight_by_id():
    """
    Asks the user for a numeric flight ID,
    Then runs the query using the data object method "get_flight_by_id".
    When results are back, calls "print_results" to show them to on the screen.
    """
    id_input = ""
    valid = False
    while not valid:
        try:
            id_input = int(input("Enter flight ID: "))
        except Exception as e:
            print("Try again...")
        else:
            valid = True
    results = flights_data.get_flight_by_id(id_input)
    print_results(results)
    export_results_to_csv("details_flight_id_", results, str(id_input))


def flights_by_date():
    """
    Asks the user for date input (and loops until it's valid),
    Then runs the query using the data object method "get_flights_by_date".
    When results are back, calls "print_results" to show them to on the screen.
    """
    date_input = ""
    date = datetime.date
    valid = False
    while not valid:
        try:
            date_input = input("Enter date in DD/MM/YYYY format: ")
            date = datetime.strptime(date_input, "%d/%m/%Y")
        except ValueError as e:
            print("Try again...", e)
        else:
            valid = True
    results = flights_data.get_flights_by_date(date.day, date.month, date.year)
    print_results(results)
    export_results_to_csv("flight_by_date_", results, date_input)


def print_results(results):
    """
    Get a list of flight results (List of dictionary-like objects from SQLAachemy).
    Even if there is one result, it should be provided in a list.
    Each object *has* to contain the columns:
    FLIGHT_ID, ORIGIN_AIRPORT, DESTINATION_AIRPORT, AIRLINE, and DELAY.
    """
    print(f"Got {len(results)} results.")
    for result in results:
        # turn result into dictionary
        result = result._mapping

        # Check that all required columns are in place
        try:
            delay = (
                int(result["DELAY"]) if result["DELAY"] else 0
            )  # If delay columns is NULL, set it to 0
            origin = result["ORIGIN_AIRPORT"]
            dest = result["DESTINATION_AIRPORT"]
            airline = result["AIRLINE"]
        except (ValueError, sqlalchemy.exc.SQLAlchemyError) as e:
            print("Error showing results: ", e)
            return

        # Different prints for delayed and non-delayed flights
        if delay and delay > 0:
            print(
                f"{result['ID']}. {origin} -> {dest} by {airline}, Delay: {delay} Minutes"
            )
        else:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}")


def show_menu_and_get_input():
    """
    Show the menu and get user input.
    If it's a valid option, return a pointer to the function to execute.
    Otherwise, keep asking the user for input.
    """
    print("Menu:")
    for key, value in FUNCTIONS.items():
        print(f"{key}. {value[1]}")

    # Input loop
    while True:
        try:
            choice = int(input())
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError as e:
            pass
        print("Try again...")


"""
Function Dispatch Dictionary
"""
FUNCTIONS = {
    1: (flight_by_id, "Show flight by ID"),
    2: (flights_by_date, "Show flights by date"),
    3: (delayed_flights_by_airline, "Delayed flights by airline"),
    4: (delayed_flights_by_airport, "Delayed flights by origin airport"),
    5: (quit, "Exit"),
}


def main():

    # The Main Menu loop
    while True:
        choice_func = show_menu_and_get_input()
        choice_func()


if __name__ == "__main__":
    main()
