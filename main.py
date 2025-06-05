"""
main.py

This script serves as the command-line interface for exploring and analyzing flight delay data
stored in a SQLite database. It allows users to query flights by various parameters (ID, date,
airline, airport), generate visualizations, and export results to CSV or PNG.

Features:
- Look up a specific flight by ID
- View all flights scheduled on a given date
- List delayed flights by airline or airport
- Plot delay percentage per airline as a horizontal bar chart
- Export query results to CSV interactively
- Display individual delay histograms
- Menu-driven navigation and input validation

Modules used:
- matplotlib.pyplot for plotting
- pandas for CSV export
- SQLAlchemy for database querying
- re for label sanitization
- datetime for date parsing

Edge Cases Handled:
- Invalid user input (non-numeric ID, incorrect date format, wrong IATA codes)
- Empty result sets from queries
- Missing or NULL delay values
- Unsafe filenames are sanitized automatically before export

Note:
All delay percentages assume a threshold of ≥ 20 minutes.
The script must be executed with access to the SQLite database under /data/flights.sqlite3.
"""

import re
from matplotlib import pyplot as plt
import flights_data
from datetime import datetime
import sqlalchemy
import pandas as pd

IATA_LENGTH = 3


def plot_percentage_of_delayed_flight_per_airline():
    """
    Calculates the percentage of delayed flights (≥ 20 minutes) per airline and plots the results
    as a horizontal bar chart.

    :return: None. The chart is saved as a PNG file using a filename provided by the user.
    """
    airlines = flights_data.get_all_airlines()
    label_list = []
    percentage_list = []

    for airline in airlines:
        all_flights = flights_data.get_all_flights_by_airline(airline)
        delayed_flights = flights_data.get_delayed_flights_by_airline(airline)

        total = len(all_flights)
        delayed = len(delayed_flights)

        if total == 0:
            continue  # Avoid division by zero

        percent = (delayed / total) * 100
        label_list.append(airline)
        percentage_list.append(percent)

    save_bar_chart(
        labels=label_list,
        values=percentage_list,
        title="Percentage of Delayed Flights per Airline",
        xlabel="Delay (%)",
    )


def save_bar_chart(labels: list[str], values: list[float], title: str, xlabel: str):
    """
    Generates and saves a horizontal bar chart using the provided data and labels.

    :param labels: List of y-axis labels (e.g., airline names).
    :param values: Corresponding x-axis values (e.g., delay percentages).
    :param title: Title of the chart.
    :param xlabel: Label for the x-axis.

    :return: None. Saves the chart as a PNG file using the filename provided via input().
    """
    file_name = input("Please name your output file (e.g. delays.png): ")
    if not file_name.endswith(".png"):
        file_name += ".png"

    plt.figure(figsize=(10, 6))
    plt.barh(labels, values, color="skyblue")
    plt.xlabel(xlabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(file_name)
    print(f"Chart saved as {file_name}")


def get_delay_histogram(results: list[dict]):
    """
    Generates and saves a horizontal bar chart representing individual flight delays.

    :param results: List of SQLAlchemy result objects (or dict-like rows) containing at least 'DELAY'
                    and either 'AIRLINE' or 'ORIGIN_AIRPORT'.
    :return: None. Saves the histogram as a PNG file based on user input.
    """
    file_name = input("Please name your histogram (e.g.: delays.png): ")
    if not file_name.endswith(".png"):
        file_name += ".png"

    # Prepare lists for labels and delay values
    label_list = []
    delay_list = []

    for result in results:
        r = result._mapping
        try:
            delay = int(r["DELAY"]) if r["DELAY"] else 0
            airline_or_airport = (
                r.get("AIRLINE") or r.get("ORIGIN_AIRPORT") or "Unknown"
            )
            label_list.append(airline_or_airport)
            delay_list.append(delay)
        except Exception as e:
            print(f"Error reading entry: {e}")
            continue

    # Generate plot
    plt.figure(figsize=(10, 6))
    plt.barh(label_list, delay_list)
    plt.xlabel("Delay (min)")
    plt.ylabel("Airline / Airport")
    plt.title("Flight Delays Histogram")

    plt.tight_layout()
    plt.savefig(file_name)
    print(f'Histogram saved as "{file_name}"', "green")


def confirm_csv_export_with_filename(default_filename: str) -> str | None:
    """
    Asks the user whether they want to export data to a CSV file and lets them confirm or change the filename.

    :param default_filename: Suggested default filename (should end with '.csv').
    :return: The confirmed or custom filename as a string, or None if the user declines export.
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
    Saves the given data to a CSV file using pandas.

    :param data: A pandas DataFrame or a list of dictionaries to be saved.
    :param filename: The target filename for the CSV (e.g. 'output.csv').
    :param delimiter: Delimiter to use in the CSV file (default is comma).
    :param encoding: File encoding (default is 'utf-8').
    :param include_index: Whether to include the DataFrame index in the output (default is False).
    :return: None. Prints confirmation or error message after saving.
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

    :param prompt: A prefix string used in the filename (e.g., 'delayed_flights_from_').
    :param results: The data to be exported, typically a list of dicts or a DataFrame.
    :param label: A label string (e.g., airline or airport name) that will be sanitized and included in the filename.
    :return: None. Saves the results to a CSV file if the user confirms.
    """
    safe_label = re.sub(r"[^a-zA-Z0-9]", "_", label.strip().lower())
    filename = confirm_csv_export_with_filename(f"{prompt}{safe_label}.csv")
    if filename:
        save_to_csv(results, filename)


def delayed_flights_by_airline():
    """
    Prompts the user for an airline name, retrieves all delayed flights for that airline,
    displays the results, and optionally exports them to a CSV file.

    :return: None. Outputs the results to the console and saves them if confirmed by the user.
    """
    airline_input = input("Enter airline name: ")
    results = flights_data.get_delayed_flights_by_airline(airline_input)
    print_results(results)

    export_results_to_csv("delayed_flights_from_", results, airline_input)


def delayed_flights_by_airport():
    """
    Prompts the user for a 3-letter IATA airport code, validates the input,
    retrieves all delayed flights from that airport, displays the results,
    and optionally exports them to a CSV file.

    :return: None. Outputs results to the console and saves them if confirmed by the user.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        # Validate input
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = flights_data.get_delayed_flights_by_airport(airport_input)
    print_results(results)
    export_results_to_csv("delayed_flights_from_airport_", results, airport_input)


def flight_by_id():
    """
    Prompts the user for a numeric flight ID, validates the input,
    retrieves the corresponding flight record, displays the result,
    and optionally exports it to a CSV file.

    :return: None. Outputs the result to the console and saves it if confirmed by the user.
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
    Prompts the user for a date in DD/MM/YYYY format, validates and parses the input,
    retrieves all flights scheduled for that date, displays the results,
    and optionally exports them to a CSV file.

    :return: None. Outputs the results to the console and saves them if confirmed by the user.
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
    Prints a list of flight results with key flight information.

    :param results: List of dictionary-like SQLAlchemy result objects.
                    Each item must contain the keys:
                    'FLIGHT_ID', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'AIRLINE', and 'DELAY'.

    :return: None. Outputs each flight's information to the console.
    """
    print(f"Got {len(results)} results.")
    for result in results:
        # turn result into dictionary
        result = result._mapping

        # Check that all required columns are in place
        try:
            delay = (
                int(result["DELAY"]) if result["DELAY"] else 0
            )  # If delay column is NULL, set it to 0
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
    Displays the available menu options, prompts the user to select one,
    and returns the corresponding function pointer.

    :return: A callable function corresponding to the user's menu choice.
             Keeps prompting until a valid numeric input is entered.
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
    5: (
        plot_percentage_of_delayed_flight_per_airline,
        "Plots the percentage of delayed flights per airline in an bar diagram",
    ),
    6: (quit, "Exit"),
}


def main():

    # The Main Menu loop
    while True:
        choice_func = show_menu_and_get_input()
        choice_func()


if __name__ == "__main__":
    main()
