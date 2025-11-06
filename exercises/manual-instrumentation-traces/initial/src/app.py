# pyright: reportMissingTypeStubs=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false

import time

import requests
import json
from client import ChaosClient, FakerClient
from flask import Flask, make_response, request
from trace_utils import create_tracer
from opentelemetry import trace as trace_api, context
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.propagate import inject, extract

# global variables
app = Flask(__name__)
tracer = create_tracer("app.py", "0.1")


@app.teardown_request
def teardown_request(err) -> None:
    previous_ctx = request.environ.get("previous_ctx_token", None)
    if previous_ctx:
        context.detach(previous_ctx)


@app.before_request
def before_request() -> None:
    ctx = extract(request.headers)
    previous_ctx = context.attach(ctx)
    request.environ["previous_ctx_token"] = previous_ctx


@app.route("/users", methods=["GET"])
@tracer.start_as_current_span("users")
def get_user():
    user, status = db.get_user(123)
    data = {}
    if user is not None:
        data = {"id": user.id, "name": user.name, "address": user.address}
    response = make_response(data, status)
    return response


@tracer.start_as_current_span("do_stuff")
def do_stuff():
    headers = {}
    inject(headers)
    time.sleep(0.1)
    url = "http://localhost:6000/"
    response = requests.get(url, headers=headers)
    print("Headers included in outbound request.:")
    print(json.dumps(response.json()["request"]["headers"], indent=2))
    return response


@app.route("/")
@tracer.start_as_current_span("index")
def index():
    span = trace_api.get_current_span()
    span.set_attributes(
        {
            SpanAttributes.HTTP_REQUEST_METHOD: request.method,
            SpanAttributes.URL_PATH: request.path,
            SpanAttributes.HTTP_RESPONSE_STATUS_CODE: 200,
        }
    )
    do_stuff()
    current_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    return f"Hello, World! It's currently {current_time}"


if __name__ == "__main__":
    db = ChaosClient(client=FakerClient())
    app.run(host="0.0.0.0", port=8000, debug=True)
