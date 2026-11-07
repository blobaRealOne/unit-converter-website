# TODO
# 1. Add screenshots of work in README.md
# 2. Add Describtion block on github
"""Provide a simple web-based unit conversion application.

The application uses the standard library's HTTP server to handle
requests and serves HTML pages for unit selection and conversion results.

Supported measurement categories include length, weight, and temperature.
Conversions use category-specific base units, with custom conversion
functions for units that require an offset or a different scale.
"""

import math
from collections.abc import Callable
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import NotRequired, TypedDict
from urllib.parse import parse_qs, urlsplit

BASE_PATH = Path(__file__).resolve().parent

HTML_MAIN_TEMPLATE = (BASE_PATH / "webpage_main.html").read_text(encoding="utf-8")
HTML_RESULT_TEMPLATE = (BASE_PATH / "webpage_result.html").read_text(encoding="utf-8")

MAX_BODY_SIZE = 8 * 1024

TempFunc = Callable[[float], float]


class UnitInfo(TypedDict):
    """Describe a measurement unit and its conversion parameters.

    Attributes:
        symbol: Short symbol used to display the unit.
        rate: Multiplication factor for conversion to the base unit.
            Used for units with linear conversion formulas.
        to_base: Optional function converting a value to the base unit.
            Used for units requiring a custom conversion formula.
        from_base: Optional function converting a value from the base
            unit to the target unit.
    """

    symbol: str
    rate: NotRequired[float]
    to_base: NotRequired[TempFunc]
    from_base: NotRequired[TempFunc]


class CategoryInfo(TypedDict):
    """Describe a measurement category and its available units.

    Attributes:
        base: Name of the base unit for the category.
        units: Mapping of unit names to their conversion parameters.
    """

    base: str
    units: dict[str, UnitInfo]


CONVERTERS: dict[str, CategoryInfo] = {
    "length": {
        "base": "meter",
        "units": {
            "millimeter": {"rate": 0.001, "symbol": "mm"},
            "centimeter": {"rate": 0.01, "symbol": "cm"},
            "meter": {"rate": 1.0, "symbol": "m"},
            "kilometer": {"rate": 1000.0, "symbol": "km"},
            "inch": {"rate": 0.0254, "symbol": "in"},
            "foot": {"rate": 0.3048, "symbol": "ft"},
            "yard": {"rate": 0.9144, "symbol": "yd"},
            "mile": {"rate": 1609.344, "symbol": "mi"},
        },
    },
    "weight": {
        "base": "gram",
        "units": {
            "milligram": {"rate": 0.001, "symbol": "mg"},
            "gram": {"rate": 1.0, "symbol": "g"},
            "kilogram": {"rate": 1000.0, "symbol": "kg"},
            "ounce": {"rate": 28.349523125, "symbol": "oz"},
            "pound": {"rate": 453.59237, "symbol": "lb"},
        },
    },
    "temperature": {
        "base": "celsius",
        "units": {
            "celsius": {
                "to_base": lambda c: float(c),
                "from_base": lambda c: float(c),
                "symbol": "°C",
            },
            "fahrenheit": {
                "to_base": lambda f: (float(f) - 32) * 5 / 9,
                "from_base": lambda c: (float(c) * 9 / 5) + 32,
                "symbol": "°F",
            },
            "kelvin": {
                "to_base": lambda k: float(k) - 273.15,
                "from_base": lambda c: float(c) + 273.15,
                "symbol": "K",
            },
        },
    },
}

OPTIONS = {
    category: "\n".join(
        f'<option value="{unit_name}">{unit_name.capitalize()}</option>'
        for unit_name in cat_data["units"]
    )
    for category, cat_data in CONVERTERS.items()
}

UNIT_TO_CATEGORY: dict[str, str] = {
    unit_name: category
    for category, cat_data in CONVERTERS.items()
    for unit_name in cat_data["units"]
}


def read_form_data(handler: BaseHTTPRequestHandler) -> dict[str, list[str]] | None:
    """Read and validate a URL-encoded POST request body.

    Checks the Content-Length header, limits the request body size,
    decodes the body as UTF-8, and parses the submitted form fields.
    Sends an appropriate HTTP error response if validation fails.

    Args:
        handler: The HTTP request handler receiving the form data.

    Returns:
        A dictionary mapping form field names to lists of values,
        or None if the request is invalid.
    """

    content_type = handler.headers.get_content_type()

    if content_type != "application/x-www-form-urlencoded":
        handler.send_error(415, "Unsupported Media Type")
        return None

    raw_length = handler.headers.get("Content-Length")

    if raw_length is None:
        handler.send_error(411, "Content-Length required")
        return None

    try:
        length = int(raw_length)
    except ValueError:
        handler.send_error(400, "Invalid Content-Length")
        return None

    if length < 0:
        handler.send_error(400, "Invalid Content-Length")
        return None

    if length > MAX_BODY_SIZE:
        handler.send_error(413, "Request body too large")
        return None

    body = handler.rfile.read(length)

    if len(body) != length:
        handler.send_error(400, "Incomplete request body")
        return None

    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError:
        handler.send_error(400, "Request body must use UTF-8")
        return None

    try:
        return parse_qs(decoded, keep_blank_values=True, max_num_fields=20)
    except ValueError:
        handler.send_error(400, "Too many form fields")
        return None


class RequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for the unit converter application.

    Supports GET requests for the main page and POST requests for
    unit conversion. Invalid conversion input redirects the client
    to the main page with an error indicator.
    """

    def do_GET(self) -> None:
        """Serve the main page for supported GET requests.

        Reads the selected measurement category from the query string.
        Falls back to the length category when the selection is invalid.

        Returns:
            None.
        """
        url = urlsplit(self.path)
        url_path = url.path
        try:
            url_query = parse_qs(url.query, keep_blank_values=True, max_num_fields=20)
        except ValueError:
            self.send_error(400, "Too many query fields")
            return
        if url_path == "/":
            raw_unit = url_query.get("unit", ["length"])[0]
            unit = raw_unit if raw_unit in CONVERTERS else "length"
            error_happened = "error" in url_query
            html_main_b = webpage_main_mod_rt(unit, error_happened)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            _ = self.wfile.write(html_main_b)
            return
        else:
            self.send_error(404)
            return

    def do_POST(self) -> None:
        """Handle POST requests for unit conversion.

        Processes form data and serves the conversion result.
        Invalid requests receive an error response or redirect.

        Returns:
            None.
        """
        if urlsplit(self.path).path != "/result":
            self.send_error(404)
            return
        data = read_form_data(self)
        if data is None:
            return
        try:
            html_result_b = webpage_result_mod_rt(data)
        except ValueError, KeyError, IndexError:
            self.redirect("/?error=1")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        _ = self.wfile.write(html_result_b)

    def redirect(self, location: str) -> None:
        """Redirect the client using HTTP status code 303.

        Args:
            location: URL to which the client should be redirected.

        Returns:
            None.
        """
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()


def webpage_main_mod_rt(measure_unit: str, error_happened: bool = False) -> bytes:
    """Render the main page with the selected measurement category.

    Args:
        measure_unit: Name of the measurement category to display.
        error_happened: Whether to display the invalid-input message.

    Returns:
        Rendered HTML page encoded as UTF-8 bytes.

    Raises:
        KeyError: If the specified category is missing from OPTIONS.
    """
    options = OPTIONS[measure_unit]
    visibility = "visible" if error_happened else "hidden"
    error_block = f'<p style="color: red; visibility: {visibility};">Invalid input!</p>'
    page_setup = {
        "title": "Main Page",
        "unit": measure_unit,
        "error_msg": error_block,
        "options_from": options,
        "options_to": options,
    }
    html_main_mod = HTML_MAIN_TEMPLATE.format_map(page_setup)
    return html_main_mod.encode("utf-8")


def webpage_result_mod_rt(data: dict[str, list[str]]) -> bytes:
    """Convert a measurement and render the result page.

    Extracts the input value and selected units from submitted form data,
    converts the value through the category's base unit, and inserts
    the formatted result into the HTML result template.

    Args:
        data: Parsed form data containing input_data, units_from,
        and units_to fields.

    Returns:
        Rendered HTML result page encoded as UTF-8 bytes.

    Raises:
        KeyError: If a required form field or conversion entry is missing.
        IndexError: If a required form field has no values.
        ValueError: If the input is not a finite number, the units are
        incompatible, or a conversion cannot be performed.
    """
    val_str = data["input_data"][0]
    unit_from = data["units_from"][0]
    unit_to = data["units_to"][0]

    val_float = float(val_str)

    if not math.isfinite(val_float):
        raise ValueError("Input value must be finite")

    if unit_from not in UNIT_TO_CATEGORY or unit_to not in UNIT_TO_CATEGORY:
        raise ValueError("Unknown unit")
    category = UNIT_TO_CATEGORY[unit_from]

    if UNIT_TO_CATEGORY[unit_to] != category:
        raise ValueError("Units belong to different categories")

    if category == "weight" and val_float < 0:
        raise ValueError("Mass cannot be negative")

    units_dict = CONVERTERS[category]["units"]
    u_from = units_dict[unit_from]
    u_to = units_dict[unit_to]

    if "to_base" in u_from and u_from["to_base"] is not None:
        base_val = u_from["to_base"](val_float)
    elif (rate_from := u_from.get("rate")) is not None:
        base_val = val_float * rate_from
    else:
        raise ValueError("Source unit has no conversion method")

    if category == "temperature":
        kelvin_val = base_val + 273.15
        if kelvin_val < 0 and not math.isclose(kelvin_val, 0.0, abs_tol=1e-9):
            raise ValueError("Temperature cannot be below absolute zero")

    if "from_base" in u_to and u_to["from_base"] is not None:
        res_val = u_to["from_base"](base_val)
    elif (rate_to := u_to.get("rate")) is not None:
        res_val = base_val / rate_to
    else:
        raise ValueError("Target unit has no conversion method")

    val_str = format_number(val_float)
    res_str = format_number(res_val)

    res_block = f"<p>{val_str} {u_from['symbol']} = {res_str} {u_to['symbol']}</p>"
    page_setup = {"title": "Result Page", "calc_res": res_block}
    html_result_mod = HTML_RESULT_TEMPLATE.format_map(page_setup)
    return html_result_mod.encode("utf-8")


def format_number(value: float) -> str:
    """Format a number without scientific notation.

    Args:
        value: Finite floating-point number to format.

    Returns:
        Decimal representation without unnecessary trailing zeros.

    Raises:
        ValueError: If the value is not finite.
    """

    if not math.isfinite(value):
        raise ValueError("Cannot format a non-finite number")

    if value == 0:
        return "0"

    result = format(Decimal(str(value)), "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return result


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
