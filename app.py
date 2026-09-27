import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


def check_single_cookie(cookie_value):
    cookie_value = cookie_value.replace("\n", "").replace("\r", "").strip()
    if not cookie_value:
        return None

    # Tự động thêm tiền tố nếu người dùng chỉ dán chuỗi token
    if not cookie_value.startswith(".ROBLOSECURITY="):
        cookie_header = f".ROBLOSECURITY={cookie_value}"
    else:
        cookie_header = cookie_value

    url = "https://users.roblox.com/v1/users/authenticated"
    headers = {
        "Cookie": cookie_header,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ),
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            return {
                "status": "ALIVE",
                "id": user_data.get("id"),
                "username": user_data.get("name"),
                "displayName": user_data.get("displayName"),
                "cookie_snippet": cookie_value[:15] + "...",
            }
        else:
            return {
                "status": "DEAD",
                "id": "N/A",
                "username": "N/A",
                "displayName": "N/A",
                "cookie_snippet": cookie_value[:15] + "...",
            }
    except Exception:
        return {
            "status": "ERROR",
            "id": "N/A",
            "username": "N/A",
            "displayName": "N/A",
            "cookie_snippet": cookie_value[:15] + "...",
        }


@app.route("/check-cookies", methods=["POST"])
def check_cookies():
    try:
        data = request.get_json()
        raw_input = data.get("cookies", "")

        # Tách các cookie theo dòng hoặc dấu phẩy/chấm phẩy
        lines = raw_input.replace(",", "\n").replace(";", "\n").split("\n")
        cookies_list = [line.strip() for line in lines if line.strip()]

        if not cookies_list:
            return (
                jsonify({"success": False, "message": "Không tìm thấy cookie nào!"}),
                400,
            )

        results = []
        for cookie in cookies_list:
            res = check_single_cookie(cookie)
            if res:
                results.append(res)
            time.sleep(0.3)  # Delay ngắn tránh dính Rate Limit

        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi Server: {str(e)}"}), 500


if __name__ == "__main__":
    print("=== SERVER CHECK MULTI-COOKIE DANG CHAY TAI HTTP://LOCALHOST:5000 ===")
    app.run(host="0.0.0.0", port=5000, debug=True)