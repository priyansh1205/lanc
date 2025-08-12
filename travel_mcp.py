import requests
import json
from typing import Optional, List, Dict, Any, Union

# Before running, ensure you have fastmcp and requests installed:
# pip install "fastmcp[sse]" requests

from fastmcp import FastMCP

# 1. Initialize the FastMCP server
mcp = FastMCP("Travel Server ✈️")

# 2. Define the base URL for the target API
BASE_URL = "https://travel-server-pi-fawn.vercel.app/api/v1"

# 3. Create tools for each API endpoint

# ==================================
# ==      HEALTH & USERS          ==
# ==================================

@mcp.tool
def check_server_health() -> str:
    """Checks the operational status of the Travel Server API."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()  # Raise an exception for HTTP error codes
        return "✅ Server is healthy and running."
    except requests.exceptions.RequestException as e:
        return f"❌ Error connecting to the server: {e}"

@mcp.tool
def create_user(name: str, email: str, password: str, role: str = "user") -> Union[Dict[str, Any], str]:
    """Creates a new user account. The email must be unique."""
    url = f"{BASE_URL}/service/users"
    payload = {"name": name, "email": email, "password": password, "role": role}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error creating user: {e}"

# ==================================
# ==      ADMIN SERVICES          ==
# ==================================

@mcp.tool
def add_flight(flightNumber: str, airline: str, from_city: str, to_city: str, departureTime: str, timeToReach: str, totalSeats: int, availableSeats: int) -> Union[Dict[str, Any], str]:
    """Adds a new flight. Note: 'from_city' and 'to_city' are used to avoid Python keywords."""
    url = f"{BASE_URL}/service/admin/flights"
    payload = {
        "flightNumber": flightNumber, "airline": airline, "from": from_city,
        "to": to_city, "departureTime": departureTime, "timeToReach": timeToReach,
        "totalSeats": totalSeats, "availableSeats": availableSeats
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error adding flight: {e}"

@mcp.tool
def remove_flight(flightId: str) -> Union[Dict[str, Any], str]:
    """Removes a flight from the system using its ID."""
    try:
        response = requests.delete(f"{BASE_URL}/service/admin/flights/{flightId}")
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error removing flight: {e}"

@mcp.tool
def add_cab(cabNumber: str, cab_type: str, location: str, availableSlots: Optional[List[Dict[str, str]]] = None) -> Union[Dict[str, Any], str]:
    """Adds a new cab. Note: 'cab_type' is used to avoid the Python keyword 'type'."""
    url = f"{BASE_URL}/service/admin/cabs"
    payload = {"cabNumber": cabNumber, "type": cab_type, "location": location}
    if availableSlots:
        payload["availableSlots"] = availableSlots
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error adding cab: {e}"

@mcp.tool
def remove_cab(cabId: str) -> Union[Dict[str, Any], str]:
    """Removes a cab from the system using its ID."""
    try:
        response = requests.delete(f"{BASE_URL}/service/admin/cabs/{cabId}")
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error removing cab: {e}"

# ==================================
# ==      PUBLIC SERVICES         ==
# ==================================

@mcp.tool
def get_available_flights() -> Union[List[Dict[str, Any]], str]:
    """Retrieves a list of all flights with available seats."""
    try:
        response = requests.get(f"{BASE_URL}/service/flights/available")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching available flights: {e}"

@mcp.tool
def get_available_cabs() -> Union[List[Dict[str, Any]], str]:
    """Retrieves a list of all available cabs with future unbooked slots."""
    try:
        response = requests.get(f"{BASE_URL}/service/cabs/available")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching available cabs: {e}"

# ==================================
# ==    BOOKING MANAGEMENT        ==
# ==================================

@mcp.tool
def book_flight(userId: str, from_city: str, to_city: str, travelDate: str) -> Union[Dict[str, Any], str]:
    """Books a seat on a flight for a user given a specific travel date."""
    url = f"{BASE_URL}/service/bookings/flight"
    payload = {"userId": userId, "from": from_city, "to": to_city, "travelDate": travelDate}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error booking flight: {e}"

@mcp.tool
def book_cab(userId: str, location: str, start_time: str) -> Union[Dict[str, Any], str]:
    """Books the closest available cab based on location and desired start time (ISO 8601 format)."""
    url = f"{BASE_URL}/service/bookings/cab"
    payload = {"userId": userId, "location": location, "slot": {"start": start_time}}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error booking cab: {e}"

@mcp.tool
def cancel_flight_booking(bookingId: str, userId: str) -> Union[Dict[str, Any], str]:
    """Cancels a specific flight booking for a user."""
    url = f"{BASE_URL}/service/bookings/flight/{bookingId}"
    try:
        response = requests.delete(url, json={"userId": userId})
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error cancelling flight booking: {e}"

@mcp.tool
def cancel_cab_booking(bookingId: str, userId: str) -> Union[Dict[str, Any], str]:
    """Cancels a specific cab booking for a user."""
    url = f"{BASE_URL}/service/bookings/cab/{bookingId}"
    try:
        response = requests.delete(url, json={"userId": userId})
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error cancelling cab booking: {e}"

@mcp.tool
def get_user_bookings(userId: str) -> Union[List[Dict[str, Any]], str]:
    """Retrieves all upcoming flight and cab bookings for a specific user."""
    try:
        response = requests.get(f"{BASE_URL}/service/users/{userId}/bookings")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching user bookings: {e}"


if __name__ == "__main__":
    # 4. Run the server
    # The server will be accessible at http://localhost:8001
    print("Starting Travel MCP Server at https://travel-server-pi-fawn.vercel.app/...")
    mcp.run(transport="sse", host="0.0.0.0", port=8001)