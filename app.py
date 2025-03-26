import os
from flask import Flask, request, jsonify
from collections import deque

app = Flask(__name__)

# تعریف خطوط مترو با همه ایستگاه‌ها

app = Flask(__name__)

# تعریف خطوط مترو با همه ایستگاه‌ها
lines = {
    "Line1": ["تجریش", "قیطریه", "شهید صدر", "قلهک", "دکتر شریعتی", "میرداماد",
              "شهید حقانی", "شهید همت", "مصلی امام خمینی", "شهید بهشتی", "شهید مفتح",
              "شهدای هفتم تیر", "طالقانی", "دروازه دولت", "سعدی", "امام خمینی",
              "پانزده خرداد", "خیام", "میدان محمدیه", "شوش", "ترمینال جنوب", "شهید بخارایی",
              "علی اباد", "جوانمرد قصاب", "شهر ری", "پالایشگاه", "باقر شهر - شاهد", "کهریزک"],
    "Line2": ["فرهنگسرا", "تهرانپارس", "دانشگاه علم و صنعت", "سرسبز", "جانبازان", "فدک", "سبلان",
              "شهید مدنی", "امام حسین", "دروازه شمیران", "بهارستان", "ملت", "امام خمینی",
              "حسن اباد", "دانشگاه امام علی", "میدان حر", "شهید نواب صفوی", "شادمان", "دانشگاه شریف", "طرشت", "صادقیه"],
    "Line3": ["قائم", "شهید محلاتی", "اقدسیه", "نوبنیاد", "حسین اباد", "هروی", "زین الدین",
              "خواجه عبدالله انصاری", "صیاد شیرازی", "شهید قدوسی", "سهروردی", "شهید بهشتی", "میرزای شیرازی", "میدان جهاد",
              "میدان ولیعصر", "تئاتر شهر", "منیریه", "مهدیه", "راه اهن", "جوادیه", "زمزم",
              "شریعتی", "عبدل اباد", "نعمت اباد", "ازادگان"],
    "Line4": ["شهید کلاهدوز", "نیرو هوایی", "نبرد", "پیروزی", "ابن سینا", "میدان شهدا",
              "دروازه شمیران", "دروازه دولت", "فردوسی", "تئاتر شهر", "میدان انقلاب", "توحید",
              "شادمان", "دکتر حبیب اله", "استاد معین", "میدان ازادی", "1,2فرودگاه مهراباد پایانه", "فرودگاه مهراباد پایانه 4و6",
              "شهرک اکباتان", "ارم سبز", "علامه جعفری", "ایت الله کاشانی", "چهارباغ"],
    "Line5": ["صادقیه", "ارم سبز", "استادیوم ازادی", "چیتگر", "ایران خودرو", "ورداورد",
              "گرمدره", "اتمسفر", "کرج", "محمد شهر", "گلشهر", "شهید سلیمانی"],
    "Line6": ["حرم عبدالعظیم", "میدان حضرت عبدالعظیم", "ابن بابویه", "چشمه علی", "دولت اباد", "کیان شهر",
              "بعثت", "شهید رضایی", "میدان خراسان", "شهدای هفده شهریور", "امیر کبیر", "میدان شهدا",
              "امام حسین", "سرباز", "بهارشیراز", "شهدای هفتم تیر", "شهید نجات اللهی",
              "میدان ولیعصر", "پارک لاله", "کارگر", "دانشگاه تربیت مدرس", "شهرک ازمایش", "مرزداران",
              "یادگار امام", "شهید اشرفی اصفهانی", "شهید ستاری", "ایت اله کاشانی", "شهر زیبا", "شهران", "شهدای کن", "کوهسار"],
    "Line7": ["میدان کتاب", "شهید دادمان", "میدان صنعت", "برج میلاد", "بوستان گفتگو",
              "دانشگاه تربیت مدرس", "مدافعان سلامت", "توحید", "شهید نواب صفوی", "رودکی", "کمیل", "بریانک",
              "حلال احمر", "مهدیه", "میدان محمدیه", "مولوی", "میدان قیام", "شهدای هفده شهریور",
              "چهل تن دولاب", "اهنگ", "بسیج", "ورزشگاه تختی"]
}

# دیکشنری ایستگاه‌ها و خطوط
station_lines = {}
for line, stations in lines.items():
    for station in stations:
        if station not in station_lines:
            station_lines[station] = []
        station_lines[station].append(line)

# دیکشنری جهت خطوط (ایستگاه اول و آخر هر خط)
line_directions = {line: (stations[0], stations[-1]) for line, stations in lines.items()}

# ساخت گراف
metro_graph = {}
for line, stations in lines.items():
    for i in range(len(stations)):
        if stations[i] not in metro_graph:
            metro_graph[stations[i]] = {}
        if i > 0:
            metro_graph[stations[i]][stations[i - 1]] = 1
        if i < len(stations) - 1:
            metro_graph[stations[i]][stations[i + 1]] = 1

# تابع حدس خط شروع بر اساس مبدا و مقصد
def guess_start_line(start, end):
    start_lines = station_lines[start]
    end_lines = station_lines[end]
    # اگه خط مشترکی بین مبدا و مقصد باشه، اون رو انتخاب کن
    common_lines = set(start_lines) & set(end_lines)
    if common_lines:
        return common_lines.pop()
    # اگه مقصد فقط توی یه خط باشه، خطی از مبدا انتخاب کن که به مقصد راه داشته باشه
    elif len(end_lines) == 1:
        target_line = end_lines[0]
        for line in start_lines:
            # چک کن آیا ایستگاه مشترکی بین خط مبدا و خط مقصد هست
            if any(station in lines[line] and station in lines[target_line] for station in metro_graph):
                return line
    # پیش‌فرض: اولین خط مبدا
    return start_lines[0]

def shortest_path_with_min_line_changes(graph, start, end, start_line):
    if start not in graph or end not in graph:
        return None, None
    
    queue = deque([(start, [start], {start_line}, 0)])
    visited = set()
    best_path = None
    min_changes = float('inf')

    while queue:
        station, path, used_lines, line_changes = queue.popleft()
        
        if station == end:
            if line_changes < min_changes:
                min_changes = line_changes
                best_path = path
            continue
        
        if station not in visited:
            visited.add(station)
            for neighbor in graph.get(station, {}):
                new_used_lines = used_lines.copy()
                new_changes = line_changes
                neighbor_lines = set(station_lines[neighbor])
                if not (new_used_lines & neighbor_lines):
                    new_changes += 1
                    new_used_lines.add(next(line for line in neighbor_lines if neighbor in lines[line]))
                
                if new_changes <= min_changes:
                    queue.append((neighbor, path + [neighbor], new_used_lines, new_changes))
    
    return best_path, min_changes if best_path else None

# تابع برای پیدا کردن جهت حرکت
def get_direction(current_station, next_station, line):
    start, end = line_directions[line]
    stations = lines[line]
    curr_idx = stations.index(current_station)
    next_idx = stations.index(next_station)
    return end if next_idx > curr_idx else start

# نمایش مسیر با دستورات تعویض خط
def get_path_instructions(path, changes, start_line):
    if not path:
        return f"مسیر یافت نشد! با {changes} تعویض خط"
    
    instructions = [f"مسیر با {changes} تعویض خط:"]
    current_line = start_line
    for i in range(len(path) - 1):
        current_station = path[i]
        next_station = path[i + 1]
        next_lines = set(station_lines[next_station])
        
        if not (current_line in next_lines):
            next_next_station = path[i + 2] if i + 2 < len(path) else next_station
            new_line_candidates = [line for line in next_lines if next_station in lines[line] and (next_next_station in lines[line] or next_station == path[-1])]
            new_line = new_line_candidates[0] if new_line_candidates else next_lines.pop()
            direction = get_direction(next_station, next_next_station, new_line)
            instructions.append(f"{current_station}: خط {current_line} - اینجا پیاده شید و به خط {new_line} به سمت {direction} سوار شید")
            current_line = new_line
        else:
            direction = get_direction(current_station, next_station, current_line)
            if i == 0:
                instructions.append(f"{current_station}: خط {current_line} به سمت {direction} سوار شید")
            else:
                instructions.append(f"{current_station}: خط {current_line}")

    instructions.append(f"{path[-1]}: خط {current_line} - اینجا پیاده شید")
    return "\n".join(instructions)

@app.route("/")
def home():
    return "API is running on Railway!"

@app.route("/find-route", methods=["POST"])
def find_route():
    data = request.get_json()
    if not data or "start" not in data or "end" not in data:
        return jsonify({"error": "لطفاً مبدا و مقصد را وارد کنید"}), 400
    
    start = data["start"]
    end = data["end"]
    start_line = guess_start_line(start, end)
    path, changes = shortest_path_with_min_line_changes(metro_graph, start, end, start_line)
    result = get_path_instructions(path, changes, start_line)
    return jsonify({"result": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
