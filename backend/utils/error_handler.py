from flask import jsonify

class ErrorHandler:
    @staticmethod
    def handle(error):
        return jsonify({
            "success": False,
            "error": str(error),
            "type": type(error).__name__
        }), 500