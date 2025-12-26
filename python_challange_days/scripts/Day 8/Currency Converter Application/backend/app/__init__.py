from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.resources import CurrencyList, ConvertCurrency

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for Streamlit frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    api = Api(app)
    
    # Register Routes
    api.add_resource(CurrencyList, '/api/v1/currencies')
    api.add_resource(ConvertCurrency, '/api/v1/convert')
    
    return app