from flask import jsonify

class ApiResponse:
    @staticmethod
    def success(data):
        return jsonify({"success": True, **data})

    @staticmethod
    def error(message):
        return jsonify({"success": False, "error": message}), 400