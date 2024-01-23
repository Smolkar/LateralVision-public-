# resources_path = os.environ["RESOURCES_PATH"]
# uploads_path = os.environ["UPLOADS_PATH"]
# processed_path = os.environ["PROCESSED_PATH"]
import os
import sys
import pickle
import json
import shutil
import time
from functools import wraps
from werkzeug.utils import secure_filename
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
)
from flask_cors import CORS
from flask_restx import Api, Resource
from datetime import datetime
from utils.database import init_db, create_relative_correlation_node
from utils.processor import get_all, connections, get_domains

# Constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
# CWD = os.path.abspath(os.getcwd())
# MODEL_PATH = os.path.join(CWD, "resources", "model")
# RESOURCES_PATH = os.path.join(CWD, "resources")
# UPLOADS_PATH = os.path.join(RESOURCES_PATH, "uploads")
# PROCESSED_PATH = os.path.join(RESOURCES_PATH, "processed")
# TEMPLATES_PATH = os.path.join(CWD, "api", "templates")
# STATIC_PATH = os.path.join(CWD, "force-graph", "src", "main")
# SELECTED_PATH = os.path.join(RESOURCES_PATH, "selected")
CWD = os.path.abspath(os.getcwd())
MODEL_PATH = os.path.join(CWD, "resources", "model")
RESOURCES_PATH = os.environ["RESOURCES_PATH"]
UPLOADS_PATH = os.environ["UPLOADS_PATH"]
PROCESSED_PATH = os.environ["PROCESSED_PATH"]
TEMPLATES_PATH = os.path.join(CWD, "api", "templates")
STATIC_PATH = os.path.join(CWD, "force-graph", "src", "main")
SELECTED_PATH = os.path.join(RESOURCES_PATH, "selected")
ALLOWED_EXTENSIONS = {"json", "csv", "txt"}
if os.listdir(SELECTED_PATH) != []:
    SELECTED_FILE = os.listdir(SELECTED_PATH)[0]
else:
    SELECTED_FILE = None
sys.path.insert(0, PARENT_DIR)
# print(os.listdir(STATIC_PATH))
app = Flask(
    __name__,
    template_folder=TEMPLATES_PATH,
    static_folder=STATIC_PATH,
    static_url_path="/",
)

app.debug = True
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOADS_PATH
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["JSON_SORT_KEYS"] = False
api = Api(
    app,
    version="1.0",
    title="LatVis API",
    description="Lateral Vision API",
    doc="/api/docs/",
)
ns = api.namespace("LatVis", description="Lateral Vision operations")


def copy_and_remove(src_file, dst_folder, dst_file):
    # Create the destination folder if it doesn't exist
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    # Copy the source file to the destination folder
    dst_file_path = os.path.join(dst_folder, dst_file)
    shutil.copy(src_file, dst_file_path)

    # Remove all files in the destination folder except the new dst_file
    for filename in os.listdir(dst_folder):
        if filename != dst_file:
            os.remove(os.path.join(dst_folder, filename))


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in app.config["ALLOWED_EXTENSIONS"]  # noqa: E501
    )


def load_pickle_file(filepath):
    file_path = os.path.join(PROCESSED_PATH, filepath)
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    return data


def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return {"error": str(e)}, 500

    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/index")
def scan():
    return render_template("index.html")


@ns.route("/selected")
class Selected(Resource):
    @handle_errors
    def get(self):
        return {"selected": SELECTED_FILE}

    def post(self):
        req_data = api.payload
        filename = req_data["filename"]
        src_file = os.path.join(PROCESSED_PATH, filename)
        if not filename:
            return {"message": "Filename not provided"}, 400

        if not os.path.exists(src_file):
            return {"message": "File not found"}, 404

        dst_folder = SELECTED_PATH
        dst_file = filename
        global SELECTED_FILE
        copy_and_remove(src_file, dst_folder, dst_file)
        SELECTED_FILE = os.path.join(SELECTED_PATH, filename)

        return {"message": f"Moved {filename} from {PROCESSED_PATH} to {SELECTED_PATH}"}


@ns.route("/connections")
class Connections(Resource):
    @handle_errors
    def get(self):
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        data = connections(
            load_pickle_file(SELECTED_FILE), start_date=start_date, end_date=end_date
        )
        json_data = json.dumps(data, cls=CustomJSONEncoder)

        return json.loads(json_data), 200


@ns.route("/relative_ip_workstation")
class Relative(Resource):
    @handle_errors
    def get(self):
        create_relative_correlation_node()

        return 200


@ns.route("/domains")
class Domains(Resource):
    @handle_errors
    def get(self):
        asd, adf = get_domains(load_pickle_file(SELECTED_FILE))
        return {"domains": asd, "count": adf}


@ns.route("/import_domains")
class ImportDomains(Resource):
    @handle_errors
    def get(self):
        data = load_pickle_file(SELECTED_FILE)
        init_db(data)
        return {"message": "Import successful"}


@ns.route("/uploads")
class Uploads(Resource):
    @handle_errors
    def get(self):
        uploads = os.listdir(UPLOADS_PATH)
        return {"uploads": uploads}


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": "Not found", "status": 404}), 404


@ns.route("/upload")
class Upload(Resource):
    @handle_errors
    def post(self):
        if "file" not in request.files:
            return {"message": "No file selected for uploading"}

        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOADS_PATH, filename))
            get_all(filename)

            return {"message": "File uploaded successfully"}
        else:
            return {"message": "Allowed file types are txt, csv, json"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
