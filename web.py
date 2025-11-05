#!/usr/bin/env python3
# =======================================================
# 🧠 Skin Cancer AI Detector - Skin Cancer Detection Web App
# =======================================================

from flask import Flask, request, render_template_string, jsonify, redirect, url_for, session
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
from datetime import datetime
import os

# === CONFIGURATION ===
API_URL = "https://detect.roboflow.com"
API_KEY = "Kz1uRQNYQfiMGbhGigCh"  # Roboflow API key
MODEL_ID = "classification-igqvf/1"
OUTPUT_DIR = "static/results"
SECRET_KEY = "supersecretkey"
# ======================

app = Flask(__name__)
app.secret_key = SECRET_KEY
CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

HTML = """
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧠 Skin Cancer AI Detector</title>
<style>
body {
    margin: 0;
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #8EC5FC, #E0C3FC);
    min-height: 100vh;
    color: #333;
    overflow-x: hidden;
    transition: background 0.5s ease-in-out;
}

/* ===== Navbar ===== */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(8px);
    padding: 10px 20px;
    position: sticky;
    top: 0;
}
.navbar h2 {
    color: white;
}
.menu {
    display: flex;
    gap: 20px;
}
.menu a {
    text-decoration: none;
    color: white;
    font-weight: bold;
    transition: 0.3s;
}
.menu a:hover {
    color: #ffd700;
}
.hamburger {
    display: none;
    font-size: 26px;
    cursor: pointer;
    color: white;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .menu {
        display: none;
        flex-direction: column;
        background: rgba(255,255,255,0.2);
        position: absolute;
        top: 60px;
        right: 20px;
        padding: 10px;
        border-radius: 8px;
    }
    .menu.active { display: flex; }
    .hamburger { display: block; }
}

/* ===== Main content ===== */
.container {
    text-align: center;
    padding: 50px 20px;
    animation: fadeIn 1s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
.upload-box {
    background: rgba(255,255,255,0.3);
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    display: inline-block;
    transition: transform 0.3s;
}
.upload-box:hover { transform: scale(1.03); }
input[type=file] { margin: 20px 0; }
button {
    background: #4b6cb7;
    color: white;
    padding: 10px 25px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.3s;
}
button:hover { background: #182848; }

/* ===== Spinner ===== */
.spinner {
    display: none;
    margin: 20px auto;
    border: 5px solid rgba(255,255,255,0.4);
    border-top: 5px solid #4b6cb7;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1s linear infinite;
}
@keyframes spin { to {transform: rotate(360deg);} }

.result img {
    margin-top: 20px;
    width: 300px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

footer {
    text-align: center;
    margin-top: 60px;
    padding: 20px;
    color: white;
}
.page { display: none; }
.page.active { display: block; }

/* ===== Cards (Bosh sahifa) ===== */
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 30px;
}
.card {
    background: rgba(255,255,255,0.3);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.05);
}
.card img {
    width: 100px; height: 70px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.history-item {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    margin: 10px;
    padding: 10px;
    border-radius: 10px;
    width: 220px;
}
/* AI tekshiruvi sahifasining orqa foni */
.page {
    background-image: url('bg.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    padding: 50px 20px;
}

.history-item img { width: 100%; border-radius: 8px; }
</style>
</head>
<body>

<div class="navbar">
    <h2>🧠 Skin Cancer AI Detector</h2>
    <div class="hamburger" onclick="toggleMenu()">☰</div>
    <div class="menu" id="menu">
        <a href="#" onclick="showPage('home')">Bosh sahifa</a>
        <a href="#" onclick="showPage('ai')">AI tekshiruvi</a>
        <a href="#" onclick="showPage('history')">Tekshiruvlar tarixi</a>
        <a href="#" onclick="showPage('contact')">Aloqa</a>
        <a href="/logout">Chiqish</a>
    </div>
</div>

<div class="container">

    <!-- === Bosh sahifa === -->
    <div id="home" class="page active">
        <h2>👩‍⚕️ Teri saratoni haqida</h2>
        <p style="max-width:750px;margin:auto;font-size:18px;">
            Teri saratoni — bu teri hujayralarining nazoratsiz o‘sishidan paydo bo‘ladigan xavfli o‘sma bo‘lib,
            erta bosqichda aniqlansa, davolanish imkoniyati yuqori bo‘ladi. Quyida asosiy turlari bilan tanishing:
        </p>

        <div class="info-grid">
            <div class="card">
                <img src="https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/reference_guide/malignant_melanoma_ref_guide/1800x1200_malignant_melanoma_ref_guide.jpg" alt="Melanoma">
                <h4>Melanoma (Mel)</h4>
                <p>Eng xavfli turi. Melanin ishlab chiqaruvchi hujayralarda rivojlanadi. Rangi o‘zgaruvchi dog‘lar bilan namoyon bo‘ladi.</p>
            </div>
            <div class="card">
                <img src="https://mismosavama.net/wp-content/uploads/2022/05/bazalni-1.webp" alt="BCC">
                <h4>Bazal hujayrali saraton (BCC)</h4>
                <p>Eng ko‘p uchraydigan turi. Odatda yuz yoki bo‘yinda oqish dog‘ sifatida paydo bo‘ladi.</p>
            </div>
            <div class="card">
                <img src="https://citydermatologyclinic.com/wp-content/uploads/2025/09/Squamous-Cell-Carcinoma-1024x1024.jpg" alt="SCC">
                <h4>Yassi hujayrali saraton (SCC)</h4>
                <p>Teri yuzasida qattiq qizil shishlar yoki yara ko‘rinishida bo‘ladi. Quyosh nuri bilan bog‘liq.</p>
            </div>
            <div class="card">
                <img src="https://ballaratskincancer.com.au/wp-content/uploads/2020/04/Ballarat-Skin-Cancer-Centre-naevus-1.jpg" alt="SCC">
                <h4>Melanotsitik nevi (NV)</h4>
                <p>Benign (xavfsiz) lezyon, melanotsitlardan hosil bo‘ladi. Ko‘pincha jigarrang yoki qora dog‘; dumaloq yoki oval shaklda; chekkalari aniq. Tananing har qaysi qismida paydo bo‘lishi mumkin. Odatda xavfsiz, lekin ba’zi melanomalar nevi ustidan rivojlanishi mumkin.</p>
            </div>
        </div>

        <br>
        <h3>🧠 AI yordamida aniqlash qanday ishlaydi?</h3>
        <p style="max-width:750px;margin:auto;font-size:17px;">
            NeuroScan AI siz yuklagan rasmni chuqur neyron tarmoq orqali tahlil qiladi:
        </p>
        <ul style="text-align:left;max-width:600px;margin:20px auto;line-height:1.7;">
            <li>📸 Rasm yuklanadi</li>
            <li>🧮 Model rasmni 1000 dan ortiq o‘qitilgan namunalar bilan solishtiradi</li>
            <li>💡 AI o‘xshashlik va xavf darajasini hisoblaydi</li>
            <li>📊 Natija: aniqlangan turi va ishonchlilik foizi</li>
        </ul>

        <br>
        <button onclick="showPage('ai')">🔍 AI tekshiruvni boshlash</button>
    </div>

    <!-- === AI tekshiruvi === -->
    <div id="ai" class="page">
        <div class="upload-box">
            <h3>AI orqali rasmni tahlil qilish</h3>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required><br>
                <button type="submit">Tahlilni boshlash</button>
            </form>
            <div class="spinner" id="spinner"></div>
            <div class="result" id="result"></div>
        </div>
    </div>

    <!-- === Tarix === -->
    <div id="history" class="page">
        <h3>📂 Tekshiruvlar tarixi</h3>
        <button onclick="clearHistory()">🗑️ Tarixni tozalash</button>
        <div id="historyList"></div>
    </div>

    <!-- === Aloqa === -->
    <div id="contact" class="page">
        <h3>📞 Aloqa ma’lumotlari</h3>
        <p>Email: <b>bobokhonov_a@samdu.uz</b></p>
        <p>Manzil: Samarqand, O‘zbekiston</p>
    </div>
</div>

<footer>© 2025 Skin Cancer AI Detector — Barcha huquqlar himoyalangan</footer>

<script>
function toggleMenu() {
    document.getElementById("menu").classList.toggle("active");
}
function showPage(id) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.getElementById(id).classList.add("active");
    document.getElementById("menu").classList.remove("active");
    if (id === 'history') loadHistory();
}

document.getElementById("uploadForm").onsubmit = async (e) => {
    e.preventDefault();
    const spinner = document.getElementById("spinner");
    const result = document.getElementById("result");
    spinner.style.display = "block";
    result.innerHTML = "";
    const formData = new FormData(e.target);
    const res = await fetch("/analyze", {method: "POST", body: formData});
    const data = await res.json();
    spinner.style.display = "none";
    if (data.error) {
        result.innerHTML = `<p style='color:red;'>${data.error}</p>`;
    } else {
        result.innerHTML = `<p><b>${data.label}</b> (${data.confidence.toFixed(1)}%)</p>
        <img src="${data.image}" alt="Natija">`;
    }
    loadHistory();
};

async function loadHistory() {
    const res = await fetch("/history");
    const data = await res.json();
    const div = document.getElementById("historyList");
    if (data.length === 0) {
        div.innerHTML = "<p>Hozircha hech qanday natija yo‘q.</p>";
    } else {
        div.innerHTML = data.map(item => `
            <div class='history-item'>
                <img src='${item.image}' alt='natija'>
                <p><b>${item.label}</b></p>
                <p>${item.confidence.toFixed(1)}%</p>
                <small>${item.time}</small>
            </div>`).join('');
    }
}
async function clearHistory(){
    if(!confirm('Haqiqatdan ham tarixni tozalaysizmi?')) return;
    await fetch('/history/clear', {method:'POST'});
    loadHistory();
}

</script>
</body>
</html>
"""

# === Flask routes ===
@app.route("/")
def index():
    if "user" not in session:
        session["user"] = "active"
    return render_template_string(HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "Rasm tanlanmadi"})
    image = request.files["image"]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = os.path.join(OUTPUT_DIR, image.filename)
    image.save(img_path)
    try:
        result = CLIENT.infer(img_path, model_id=MODEL_ID)
        preds = result.get("predictions", {})
        if not preds:
            return jsonify({"label": "Teri saratoni aniqlanmadi", "confidence": 0, "image": f"/{img_path}"})
        label, info = max(preds.items(), key=lambda x: x[1]["confidence"])
        conf = info["confidence"] * 100
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), f"{label} ({conf:.1f}%)", fill="red")
        result_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        result_path = os.path.join(OUTPUT_DIR, result_name)
        img.save(result_path)
        with open(os.path.join(OUTPUT_DIR, "history.txt"), "a", encoding="utf-8") as f:
            f.write(f"{result_path}|{label}|{conf:.1f}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return jsonify({"label": label, "confidence": conf, "image": f"/{result_path}"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/history")
def history():
    path = os.path.join(OUTPUT_DIR, "history.txt")
    if not os.path.exists(path):
        return jsonify([])
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in reversed(f.readlines()):
            p, l, c, t = line.strip().split("|")
            data.append({"image": f"/{p}", "label": l, "confidence": float(c), "time": t})
    return jsonify(data)
@app.route("/history/clear", methods=["POST"])
def clear_history():
    history_file = os.path.join(OUTPUT_DIR, "history.txt")
    if os.path.exists(history_file):
        os.remove(history_file)
    # Natija rasmlarini ham o'chirish
    for file in os.listdir(OUTPUT_DIR):
        if file.startswith("result_"):
            os.remove(os.path.join(OUTPUT_DIR, file))
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
