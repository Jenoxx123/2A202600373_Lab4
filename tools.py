from langchain_core.tools import tool

# ==============================================================================
# MOCK DATA – Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# Sinh viên cần đọc hiểu data để debug test cases.
# ==============================================================================

# Constants
MAX_PRICE = 999_999_999

# Helper function for currency formatting
def format_vnd(amount: int) -> str:
    """Helper function to format VND currency with dot separators"""
    return f"{amount:,}".replace(',', '.') + "đ"

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    # Normalize input to handle case sensitivity
    origin = origin.strip().title()
    destination = destination.strip().title()
    
    # Tra cứu FLIGHTS_DB với key (origin, destination)
    flights = FLIGHTS_DB.get((origin, destination))
    
    # Nếu không tìm thấy, thử tra ngược (destination, origin)
    if flights is None:
        flights = FLIGHTS_DB.get((destination, origin))
    
    # Nếu vẫn không tìm thấy, trả về thông báo
    if flights is None:
        return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
    
    # Format danh sách chuyến bay dễ đọc
    result = f"Tìm thấy {len(flights)} chuyến bay từ {origin} đến {destination}:\n"
    for idx, flight in enumerate(flights, 1):
        price_formatted = format_vnd(flight['price'])
        result += f"\n{idx}. {flight['airline']}"
        result += f"\n   Giờ bay: {flight['departure']} - {flight['arrival']}"
        result += f"\n   Hạng: {flight['class']}"
        result += f"\n   Giá: {price_formatted}"
    
    return result

@tool
def search_hotels(city: str, max_price_per_night: int = MAX_PRICE) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    # Normalize input to handle case sensitivity
    city = city.strip().title()
    
    # Tra cứu HOTELS_DB[city]
    hotels = HOTELS_DB.get(city)
    
    # Nếu thành phố không tồn tại trong database
    if hotels is None:
        return f"Không tìm thấy dữ liệu khách sạn tại {city}."
    
    # Lọc theo max_price_per_night
    filtered_hotels = [hotel for hotel in hotels if hotel['price_per_night'] <= max_price_per_night]
    
    # Nếu không có khách sạn nào phù hợp sau khi lọc
    if not filtered_hotels:
        price_formatted = format_vnd(max_price_per_night)
        return f"Không tìm thấy khách sạn tại {city} với giá dưới {price_formatted}/đêm. Hãy thử tăng ngân sách."
    
    # Sắp xếp theo rating giảm dần (cao nhất lên đầu)
    filtered_hotels.sort(key=lambda x: x['rating'], reverse=True)
    
    # Format kết quả đẹp
    result = f"Tìm thấy {len(filtered_hotels)} khách sạn tại {city}:\n"
    for idx, hotel in enumerate(filtered_hotels, 1):
        price_formatted = format_vnd(hotel['price_per_night'])
        stars = "⭐" * hotel['stars']
        result += f"\n{idx}. {hotel['name']} ({stars})"
        result += f"\n   Khu vực: {hotel['area']}"
        result += f"\n   Giá: {price_formatted}/đêm"
        result += f"\n   Đánh giá: {hotel['rating']}/5.0"
    
    return result

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy,
    định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    try:
        # Parse chuỗi expenses thành dictionary
        expense_dict = {}
        total_expenses = 0
        
        # Split theo dấu phẩy để lấy từng khoản chi
        expense_items = expenses.split(',')
        
        for item in expense_items:
            # Split theo dấu hai chấm để tách tên và số tiền
            if ':' not in item:
                return f"Lỗi format: Thiếu dấu ':' trong khoản chi '{item}'. Định dạng đúng: 'tên_khoản:số_tiền'"
            
            parts = item.split(':')
            if len(parts) != 2:
                return f"Lỗi format: Khoản chi '{item}' không đúng định dạng. Định dạng đúng: 'tên_khoản:số_tiền'"
            
            expense_name = parts[0].strip()
            expense_amount_str = parts[1].strip()
            
            # Chuyển đổi số tiền sang integer
            try:
                expense_amount = int(expense_amount_str)
            except ValueError:
                return f"Lỗi format: Số tiền '{expense_amount_str}' không hợp lệ trong khoản chi '{expense_name}'"
            
            expense_dict[expense_name] = expense_amount
            total_expenses += expense_amount
        
        # Tính số tiền còn lại
        remaining = total_budget - total_expenses
        
        # Format bảng chi tiết
        result = "Bảng chi phí:\n"
        for name, amount in expense_dict.items():
            amount_formatted = format_vnd(amount)
            # Capitalize tên khoản chi cho đẹp
            display_name = name.replace('_', ' ').capitalize()
            result += f"- {display_name}: {amount_formatted}\n"
        
        result += "---\n"
        result += f"Tổng chi: {format_vnd(total_expenses)}\n"
        result += f"Ngân sách: {format_vnd(total_budget)}\n"
        
        # Kiểm tra vượt ngân sách
        if remaining < 0:
            deficit = abs(remaining)
            result += f"⚠️ Vượt ngân sách {format_vnd(deficit)}! Cần điều chỉnh."
        else:
            result += f"Còn lại: {format_vnd(remaining)}"
        
        return result
        
    except Exception as e:
        return f"Lỗi khi xử lý chi phí: {str(e)}. Vui lòng kiểm tra lại định dạng 'tên_khoản:số_tiền,tên_khoản2:số_tiền2'"