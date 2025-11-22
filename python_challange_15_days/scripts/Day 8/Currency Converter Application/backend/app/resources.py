from flask_restful import Resource, reqparse
from app.services import CurrencyService

class CurrencyList(Resource):
    def get(self):
        """Get list of supported currencies"""
        return {
            "success": True,
            "currencies": CurrencyService.get_currencies()
        }, 200

class ConvertCurrency(Resource):
    def post(self):
        """Perform currency conversion"""
        parser = reqparse.RequestParser()
        parser.add_argument('from_currency', type=str, required=True, help='Source currency is required')
        parser.add_argument('to_currency', type=str, required=True, help='Target currency is required')
        parser.add_argument('amount', type=float, required=True, help='Amount is required')
        
        args = parser.parse_args()

        try:
            result = CurrencyService.convert(
                args['from_currency'], 
                args['to_currency'], 
                args['amount']
            )
            return {
                "success": True,
                "data": {
                    "from": args['from_currency'],
                    "to": args['to_currency'],
                    "original_amount": args['amount'],
                    "converted_amount": result
                }
            }, 200
        except ValueError as e:
            return {"success": False, "error": str(e)}, 400
        except Exception as e:
            return {"success": False, "error": "Internal Server Error"}, 500