import math
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import NotRequired, TypedDict
from urllib.parse import parse_qs, urlsplit

BASE_PATH = Path(__file__).resolve().parent
MAIN_WEBPAGE_PATH = str(BASE_PATH / "webpage_main.html")
RESULT_WEBPAGE_PATH = str(BASE_PATH / "webpage_result.html")

def fileread(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as err:
        print(err)
        raise

HTML_MAIN_TEMPLATE = fileread(MAIN_WEBPAGE_PATH)
HTML_RESULT_TEMPLATE = fileread(RESULT_WEBPAGE_PATH)

TempFunc = Callable[[float], float]

class UnitInfo(TypedDict):
    symbol: str
    rate: NotRequired[float]
    to_base: NotRequired[TempFunc]
    from_base: NotRequired[TempFunc]


class CategoryInfo(TypedDict):
    base: str
    units: dict[str, UnitInfo]


CONVERTERS: dict[str, CategoryInfo] = {
    "length": {
        "base": "meter",
        "units": {
            "milimeter": {"rate": 0.001, "symbol": "mm"},
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
            "miligram": {"rate": 0.001, "symbol": "mg"},
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

OPTIONS = {category: "\n".join(f'<option value="{unit_name}">{unit_name.capitalize()}</option>' for unit_name in cat_data["units"]) for category, cat_data in CONVERTERS.items()}

UNIT_TO_CATEGORY: dict[str, str] = {
    unit_name: category
    for category, cat_data in CONVERTERS.items()
    for unit_name in cat_data["units"]
}


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        URL = urlsplit(self.path)
        URL_PATH = URL.path
        URL_QUERY = parse_qs(URL.query, keep_blank_values=True)
        if URL_PATH == "/":
            raw_unit = URL_QUERY.get("unit", ["length"])[0]
            unit = raw_unit if raw_unit in CONVERTERS else "length"
            error_happened = "error" in URL_QUERY
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
        if self.path == "/result":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = parse_qs(body.decode("utf-8"))
            try:
                html_result_b = webpage_result_mod_rt(data)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                _ = self.wfile.write(html_result_b)
                return
            except (ValueError, KeyError, IndexError):
                self.redirect("/?error=1")
                return
        else:
            self.send_error(404)
            return

    def redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()


def webpage_main_mod_rt(measure_unit: str, error_happened: bool = False) -> bytes:
    options = OPTIONS[measure_unit]
    visibility = "visible" if error_happened else "hidden"
    error_block = f'<p style="color: red; visibility: {visibility};">Invalid input!</p>'
    page_setup = {
        "unit": measure_unit,
        "error_msg": error_block,
        "options_from": options,
        "options_to": options,
    }
    html_main_mod = HTML_MAIN_TEMPLATE.format_map(page_setup)
    return html_main_mod.encode("utf-8")


def webpage_result_mod_rt(data: dict[str, list[str]]) -> bytes:
    val_str = data["input_data"][0]
    unit_from = data["units_from"][0]
    unit_to = data["units_to"][0]

    val_float = float(val_str)

    if math.isnan(val_float) or math.isinf(val_float):
        raise ValueError()

    if unit_from not in UNIT_TO_CATEGORY or unit_to not in UNIT_TO_CATEGORY:
        raise ValueError()

    category = UNIT_TO_CATEGORY[unit_from]

    if UNIT_TO_CATEGORY[unit_to] != category:
        raise ValueError()
    units_dict = CONVERTERS[category]["units"]
    u_from = units_dict[unit_from]
    u_to = units_dict[unit_to]

    if "to_base" in u_from and u_from["to_base"] is not None:
        base_val = u_from["to_base"](val_float)
    elif (rate_from := u_from.get("rate")) is not None:
        base_val = val_float * rate_from
    else:
        raise ValueError()

    if "from_base" in u_to and u_to["from_base"] is not None:
        res_val = u_to["from_base"](base_val)
    elif (rate_to := u_to.get("rate")) is not None:
        res_val = base_val / rate_to
    else:
        raise ValueError()

    res_block = f"<p>{val_float} {u_from['symbol']} = {res_val:.6g} {u_to['symbol']}</p>"
    page_setup = {"calc_res": res_block}

    html_result_mod = HTML_RESULT_TEMPLATE.format_map(page_setup)
    return html_result_mod.encode("utf-8")

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), RequestHandler)
    server.serve_forever()
