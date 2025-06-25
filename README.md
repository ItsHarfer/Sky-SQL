# Flight Delay Database ✈️ – SQL / Python / API Edition

A Python-based application for querying historical flight delay data from a SQLite database. Built with SQLAlchemy, this project enables filtering by airline, airport, date, and delay status. It's ideal for data analysis, reporting, or extending with web frameworks and APIs.

---

## Features

- 🔍 **Flight Lookup:** Query flights by ID, date, airline, or airport  
- 🛫 **Delay Analysis:** Find delayed flights (≥20 min) by airline or origin airport  
- 📋 **Airline Overview:** Get a list of all airlines in the database  
- 🗃️ **SQLite Backend:** Simple and portable data storage using SQLite  
- ⚙️ **SQLAlchemy Engine:** Flexible, safe query execution with parameter binding  
- 🧩 **Modular Functions:** Clean Python interface for data access and analysis  
- 🧪 **Easy to Extend:** Ideal for web APIs, dashboards, or Jupyter analytics

---

## Tech Stack

- Python 3.10+  
- SQLite (`flights.sqlite3`)  
- SQLAlchemy for database access   

---


## Project Structure

```
.
├── main.py                 # Example entry point for running and testing queries
├── flights_data.py         # Core module: query functions and SQL definitions
├── data/
│   └── flights.sqlite3     # SQLite database (excluded from VCS if large)
├── LICENSE                 # Open source license
├── README.md               # Project documentation (you’re reading it)
└── requirements.txt        # Project requirements to install before run the app
```
---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ItsHarfer/Sky-SQL.git
cd Sky-SQL
```
### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Run the Application
 
```python
python main.py
```

---

## Example Queries

- **🛩️ Get all airlines:**
  ```python
  get_all_airlines()
  ```

- **📅 Get flights on a specific date:**
  ```python
  get_flights_by_date(day=15, month=6, year=2015)
  ```

- **🛫 Get all flights for a specific airline:**
  ```python
  get_all_flights_by_airline("American Airlines")
  ```

- **⚠️ Get delayed flights by airport:**
  ```python
  get_delayed_flights_by_airport("JFK")
  ```

- **🆔 Get details for flight by ID:**
  ```python
  get_flight_by_id(1289)
  ```

---

## License

MIT License – for educational and analytical use.

---

## Author

Martin Haferanke  
GitHub: [@ItsHarfer](https://github.com/ItsHarfer)  
Email: `martin.haferanke@gmail.com`
