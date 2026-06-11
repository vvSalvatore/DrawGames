"""
DrawCrack — Cracked games library backend
FastAPI + MongoDB (motor) + Steam API enrichment + curated seed catalog
"""
from dotenv import load_dotenv
from pathlib import Path
ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')

import os
import re
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

import httpx
import json as _json
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

IMPORT_FILE = ROOT / "import_games.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ---------- Mongo ----------
client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

# ---------- Sources (download mirrors) ----------
SOURCES: Dict[str, Dict[str, Any]] = {
    "fitgirl": {
        "id": "fitgirl",
        "name": "FitGirl Repacks",
        "color": "#ff4d96",
        "url": "https://fitgirl-repacks.site/",
        "logo": "https://fitgirl-repacks.site/wp-content/uploads/2018/03/cropped-cropped-fglogo.png",
        "desc_ar": "أكبر موقع للألعاب المضغوطة بأحجام صغيرة جداً مع جودة عالية. كل الألعاب مرفوعة من قبل FitGirl شخصياً.",
        "features_ar": ["ضغط قوي جداً (أحجام أصغر بـ 70%)", "متاحة بدون كلمة سر", "دعم تورنت + روابط مباشرة", "ألعاب نظيفة بدون فيروسات"],
        "color_accent": "#ff4d96",
        "steps_ar": [
            {"title": "حمل ملف التورنت", "body": "اضغط على زر التحميل في الموقع، ستفتح صفحة جديدة فيها رابط التورنت/الماجنت. افتح الرابط بـ qBittorrent أو uTorrent."},
            {"title": "انتظر اكتمال التحميل", "body": "ستحصل على مجلد فيه ملفات setup.exe وملفات .bin. لا تحذف أي ملف."},
            {"title": "شغّل setup.exe", "body": "افتح setup.exe كمسؤول (Run as Administrator). ستظهر شاشة FitGirl الشهيرة."},
            {"title": "اختر مسار التثبيت", "body": "اختر مسار ليس فيه عربي ولا مسافات (مثلاً D:\\Games\\GameName)."},
            {"title": "انتظر إعادة الضغط", "body": "FitGirl تستخدم ضغط قوي، التثبيت قد يستغرق 30-90 دقيقة حسب اللعبة وقوة الجهاز."},
            {"title": "شغّل اللعبة", "body": "بعد اكتمال التثبيت، ستجد اختصار اللعبة على سطح المكتب. شغّلها كمسؤول من أيقونة اللعبة الأصلية في مجلد التثبيت."},
        ],
        "tips_ar": [
            "تأكد من تعطيل Windows Defender مؤقتاً قبل التثبيت لأنه قد يحذف ملفات الكراك",
            "أضف مجلد اللعبة لاستثناءات الحماية بعد التثبيت",
            "احتاج 2x من حجم اللعبة مساحة فارغة أثناء التثبيت بسبب فك الضغط",
        ],
        "no_password": True,
    },
    "online-fix": {
        "id": "online-fix",
        "name": "Online-Fix.me",
        "color": "#3b82f6",
        "url": "https://online-fix.me/",
        "logo": "https://online-fix.me/templates/Online-Fix/images/logo.png",
        "desc_ar": "متخصص في فتح اللعب الجماعي (Co-op + Multiplayer) للألعاب المكركة. يضيف خوادم خاصة للعب مع الأصدقاء.",
        "features_ar": ["دعم اللعب الجماعي والكوب", "تحديثات مستمرة", "محتاج كلمة سر للضغط", "خوادم لعب خاصة"],
        "color_accent": "#3b82f6",
        "steps_ar": [
            {"title": "حمل ملف التورنت أو المباشر", "body": "اضغط على زر Download في صفحة اللعبة. هتلاقي روابط Mega/Mediafire أو تورنت."},
            {"title": "أدخل كلمة السر", "body": "ملفات الضغط مشفرة. كلمة السر دائماً: online-fix.me (احرف صغيرة بدون مسافات)."},
            {"title": "فك الضغط", "body": "استخدم WinRAR أو 7-Zip لفك الضغط. أدخل كلمة السر لما يطلب منك."},
            {"title": "ثبّت اللعبة", "body": "افتح ملف setup.exe أو autorun.exe كمسؤول. اتبع التعليمات."},
            {"title": "انسخ ملفات الكراك", "body": "بعد التثبيت، روح لمجلد _CrackFix أو OnlineFix في الملفات المحملة. انسخ كل اللي فيه وألصقه في مجلد اللعبة المثبتة (Replace All)."},
            {"title": "شغّل اللعبة", "body": "افتح Steam_emu.exe أو لانشر اللعبة. للعب الجماعي: شغّل اللانشر الخاص بـ Online-Fix من اختصار سطح المكتب."},
        ],
        "tips_ar": [
            "كلمة السر دائماً: online-fix.me (انسخها للحفظ)",
            "للعب الكوب: تأكد أنت وأصدقاءك على نفس إصدار اللعبة بالضبط",
            "بعض الألعاب تحتاج Hamachi أو Radmin VPN للعب الجماعي",
        ],
        "no_password": False,
        "archive_password": "online-fix.me",
    },
    "ankergames": {
        "id": "ankergames",
        "name": "AnkerGames",
        "color": "#10b981",
        "url": "https://ankergames.net/",
        "logo": "https://ankergames.net/assets/logo.svg",
        "desc_ar": "موقع عربي رائد في توفير الألعاب المكركة بسرعات تحميل عالية. خوادم في الشرق الأوسط.",
        "features_ar": ["سرعات تحميل ممتازة للعرب", "ألعاب محدثة بانتظام", "روابط مباشرة + تورنت", "واجهة عربية"],
        "color_accent": "#10b981",
        "steps_ar": [
            {"title": "اختر طريقة التحميل", "body": "في صفحة اللعبة هتلاقي تبويبات: Direct Links / Torrent / Mega. اختر اللي يناسبك (التورنت أسرع للعرب)."},
            {"title": "حمل كل الأجزاء", "body": "الألعاب الكبيرة مقسمة لأجزاء (part1, part2...). حمل كل الأجزاء في نفس المجلد."},
            {"title": "فك الضغط بالترتيب", "body": "بـ WinRAR/7-Zip اضغط كليك يمين على part1.rar -> Extract Here. كل الأجزاء هتنفك تلقائياً."},
            {"title": "ثبّت اللعبة", "body": "افتح setup.exe كمسؤول. اختر مسار تثبيت بدون عربي."},
            {"title": "طبّق الكراك", "body": "روح لمجلد Crack أو CODEX/PLAZA في الملفات المحملة. انسخ كل اللي فيه إلى مجلد اللعبة المثبتة."},
            {"title": "العب", "body": "شغّل اللعبة من سطح المكتب. لو طلبت كراك تاني، أعد نسخ الكراك."},
        ],
        "tips_ar": [
            "أضف مجلد اللعبة لاستثناءات Windows Defender قبل نسخ الكراك",
            "بعض الألعاب من Anker بتحتاج Visual C++ Redistributables و DirectX",
            "للسرعات الأقصى استخدم Internet Download Manager",
        ],
        "no_password": True,
    },
    "steamunlocked": {
        "id": "steamunlocked",
        "name": "SteamUnlocked",
        "color": "#06b6d4",
        "url": "https://steamunlocked.net/",
        "logo": "https://steamunlocked.net/wp-content/uploads/2020/03/cropped-steam-unlocked-1.png",
        "desc_ar": "ألعاب جاهزة قبل التثبيت (Pre-Installed). فقط فك الضغط والعب مباشرة بدون تثبيت.",
        "features_ar": ["لا يحتاج تثبيت — جاهزة للعب", "ألعاب AAA حديثة", "روابط مباشرة + تورنت", "نسخ نظيفة"],
        "color_accent": "#06b6d4",
        "steps_ar": [
            {"title": "حمل ملف ZIP أو التورنت", "body": "في صفحة اللعبة اضغط Download. هتفتح صفحة فيها روابط Mega/Drive/Torrent."},
            {"title": "فك الضغط", "body": "كليك يمين على الملف -> Extract. ستحصل على مجلد اللعبة كاملاً."},
            {"title": "افتح المجلد", "body": "ادخل لمجلد اللعبة المفكوك. هتلاقي ملف .exe باسم اللعبة (مثلاً Cyberpunk2077.exe)."},
            {"title": "شغّل اللعبة مباشرة", "body": "كليك مزدوج على ملف .exe الرئيسي. اللعبة هتشتغل بدون تثبيت!"},
            {"title": "أضف لاستثناءات الحماية", "body": "إذا اعترض Windows Defender، أضف المجلد للاستثناءات وأعد المحاولة."},
        ],
        "tips_ar": [
            "ميزة SteamUnlocked: لا تثبيت = لا تخريب للريجستري",
            "احفظ نسخة احتياطية من مجلد Saves قبل أي تحديث",
            "إذا اللعبة ما تشتغل: ثبّت Visual C++ All-in-One",
        ],
        "no_password": True,
    },
}

# ---------- Curated Catalog (real Steam App IDs) ----------
# Source: hand-picked games matching user's request — co-op horror, exploration survival, action
CATALOG: List[Dict[str, Any]] = [
    # === Co-op Horror ===
    {"steam_app_id": "739630", "title": "Phasmophobia", "size": "15 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "Multiplayer"]},
    {"steam_app_id": "1966720", "title": "Lethal Company", "size": "1.2 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "1304930", "title": "The Outlast Trials", "size": "30 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "2881650", "title": "Content Warning", "size": "2 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "Comedy"]},
    {"steam_app_id": "1326470", "title": "Sons Of The Forest", "size": "20 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 8, "genres": ["Survival", "Horror", "Co-op"]},
    {"steam_app_id": "242760", "title": "The Forest", "size": "6 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 8, "genres": ["Survival", "Horror", "Co-op"]},
    {"steam_app_id": "1274570", "title": "Devour", "size": "5 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "493520", "title": "GTFO", "size": "30 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "FPS"]},
    {"steam_app_id": "381210", "title": "Dead by Daylight", "size": "50 GB", "source": "online-fix", "is_coop": False, "is_multiplayer": True, "coop_count": 5, "genres": ["Horror", "Multiplayer"]},
    {"steam_app_id": "2087030", "title": "Escape the Backrooms", "size": "5 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "Exploration"]},
    {"steam_app_id": "1880890", "title": "Iron Lung", "size": "500 MB", "source": "steamunlocked", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror", "Indie"]},
    {"steam_app_id": "2378900", "title": "PANICORE", "size": "4 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},

    # === Co-op Survival/Exploration ===
    {"steam_app_id": "648800", "title": "Raft", "size": "2 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 8, "genres": ["Survival", "Co-op", "Exploration"]},
    {"steam_app_id": "892970", "title": "Valheim", "size": "2 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 10, "genres": ["Survival", "Co-op", "Exploration"]},
    {"steam_app_id": "962130", "title": "Grounded", "size": "12 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Survival", "Co-op"]},
    {"steam_app_id": "322330", "title": "Don't Starve Together", "size": "1 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 6, "genres": ["Survival", "Co-op"]},
    {"steam_app_id": "264710", "title": "Subnautica", "size": "15 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Survival", "Exploration", "Adventure"]},
    {"steam_app_id": "848450", "title": "Subnautica: Below Zero", "size": "12 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Survival", "Exploration"]},
    {"steam_app_id": "815370", "title": "Green Hell", "size": "10 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Survival", "Co-op"]},
    {"steam_app_id": "251570", "title": "7 Days to Die", "size": "12 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 8, "genres": ["Survival", "Co-op", "Horror"]},
    {"steam_app_id": "108600", "title": "Project Zomboid", "size": "3 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 32, "genres": ["Survival", "Co-op", "Zombies"]},
    {"steam_app_id": "440900", "title": "Conan Exiles", "size": "60 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 40, "genres": ["Survival", "Co-op"]},
    {"steam_app_id": "1604030", "title": "Enshrouded", "size": "30 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 16, "genres": ["Survival", "Co-op", "RPG"]},
    {"steam_app_id": "2139460", "title": "Once Human", "size": "40 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Survival", "Co-op"]},
    {"steam_app_id": "1985810", "title": "Palworld", "size": "40 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 32, "genres": ["Survival", "Co-op", "Creature"]},

    # === Co-op Action / Multiplayer ===
    {"steam_app_id": "1426210", "title": "It Takes Two", "size": "25 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 2, "genres": ["Co-op", "Adventure"]},
    {"steam_app_id": "1222730", "title": "A Way Out", "size": "20 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 2, "genres": ["Co-op", "Action"]},
    {"steam_app_id": "728880", "title": "Overcooked! 2", "size": "5 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Co-op", "Casual"]},
    {"steam_app_id": "548430", "title": "Deep Rock Galactic", "size": "8 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Co-op", "FPS"]},
    {"steam_app_id": "553850", "title": "HELLDIVERS 2", "size": "100 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Co-op", "Shooter"]},
    {"steam_app_id": "1172620", "title": "Sea of Thieves", "size": "70 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Adventure", "Co-op", "MMO"]},
    {"steam_app_id": "1551360", "title": "Forza Horizon 5", "size": "110 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": True, "coop_count": 12, "genres": ["Racing", "Multiplayer"]},
    {"steam_app_id": "601150", "title": "Devil May Cry 5", "size": "35 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action"]},

    # === Action / Souls / Iconic Solo ===
    {"steam_app_id": "1245620", "title": "Elden Ring", "size": "60 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Action RPG", "Souls"]},
    {"steam_app_id": "2358720", "title": "Black Myth: Wukong", "size": "130 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action RPG"]},
    {"steam_app_id": "1091500", "title": "Cyberpunk 2077", "size": "110 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action RPG"]},
    {"steam_app_id": "1086940", "title": "Baldur's Gate 3", "size": "150 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["RPG", "Co-op"]},
    {"steam_app_id": "2622380", "title": "ELDEN RING NIGHTREIGN", "size": "30 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 3, "genres": ["Action RPG", "Co-op"]},
    {"steam_app_id": "814380", "title": "Sekiro: Shadows Die Twice", "size": "25 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action", "Souls"]},
    {"steam_app_id": "374320", "title": "DARK SOULS III", "size": "25 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 6, "genres": ["Action", "Souls"]},
    {"steam_app_id": "271590", "title": "Grand Theft Auto V", "size": "95 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": True, "coop_count": 30, "genres": ["Open World", "Action"]},
    {"steam_app_id": "1174180", "title": "Red Dead Redemption 2", "size": "120 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": True, "coop_count": 32, "genres": ["Open World", "Action"]},
    {"steam_app_id": "292030", "title": "The Witcher 3: Wild Hunt", "size": "50 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["RPG"]},
    {"steam_app_id": "1593500", "title": "God of War", "size": "60 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action"]},
    {"steam_app_id": "1971870", "title": "Resident Evil 4 Remake", "size": "65 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror", "Action"]},
    {"steam_app_id": "1196590", "title": "Resident Evil Village", "size": "50 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror"]},
    {"steam_app_id": "292140", "title": "Resident Evil 2 Remake", "size": "25 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror"]},
    {"steam_app_id": "952060", "title": "Resident Evil 3 Remake", "size": "20 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror"]},
    {"steam_app_id": "1361210", "title": "Alan Wake 2", "size": "100 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror", "Adventure"]},
    {"steam_app_id": "1623730", "title": "Palworld", "size": "40 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 32, "genres": ["Survival", "Co-op"]},

    # === Coming Soon (with real or anticipated Steam App IDs) ===
    {"steam_app_id": "3241660", "title": "Resident Evil Requiem", "size": "60 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror"], "is_coming_soon": True, "release_date": "Feb 2026"},
    {"steam_app_id": "1030300", "title": "Hollow Knight: Silksong", "size": "8 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Metroidvania", "Indie"], "is_coming_soon": True, "release_date": "2026"},
    {"steam_app_id": "3008720", "title": "P.O.N.", "size": "5 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"], "is_coming_soon": True, "release_date": "2026"},
    {"steam_app_id": "1145360", "title": "Hades II", "size": "10 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Roguelike", "Action"], "is_coming_soon": True, "release_date": "2026"},
    {"steam_app_id": "2344520", "title": "Diablo IV: Vessel of Hatred", "size": "100 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Action RPG", "Co-op"], "is_coming_soon": True, "release_date": "2026"},
    {"steam_app_id": "2399830", "title": "ARC Raiders", "size": "30 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Shooter", "Co-op"], "is_coming_soon": True, "release_date": "2026"},
    {"steam_app_id": "2825380", "title": "Light No Fire", "size": "40 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 32, "genres": ["Survival", "Co-op", "Exploration"], "is_coming_soon": True, "release_date": "2026"},
    {"steam_app_id": "2622380", "title": "Crimson Desert", "size": "80 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action RPG"], "is_coming_soon": True, "release_date": "2026"},

    # === R.E.P.O Games from Online-Fix.me ===
    {"steam_app_id": "1245620", "title": "R.E.P.O. - Extraction", "size": "45 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Action", "Co-op", "FPS"]},
    {"steam_app_id": "1966720", "title": "Lethal Company", "size": "1.2 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "739630", "title": "Phasmophobia", "size": "15 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "Multiplayer"]},
    {"steam_app_id": "1304930", "title": "The Outlast Trials", "size": "30 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "2881650", "title": "Content Warning", "size": "2 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "Comedy"]},
    {"steam_app_id": "1274570", "title": "Devour", "size": "5 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "493520", "title": "GTFO", "size": "30 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "FPS"]},
    {"steam_app_id": "2087030", "title": "Escape the Backrooms", "size": "5 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op", "Exploration"]},
    {"steam_app_id": "2378900", "title": "PANICORE", "size": "4 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Horror", "Co-op"]},
    {"steam_app_id": "553850", "title": "HELLDIVERS 2", "size": "100 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Co-op", "Shooter"]},
    {"steam_app_id": "1172620", "title": "Sea of Thieves", "size": "70 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Adventure", "Co-op", "MMO"]},
    {"steam_app_id": "108600", "title": "Project Zomboid", "size": "3 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 32, "genres": ["Survival", "Co-op", "Zombies"]},
    {"steam_app_id": "2139460", "title": "Once Human", "size": "40 GB", "source": "online-fix", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Survival", "Co-op"]},

    # === FIRST LIGHT 007 from FitGirl ===
    {"steam_app_id": "3768760", "title": "007 First Light", "size": "25 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Action", "Co-op", "FPS"]},

    # === Additional Popular Games ===
    {"steam_app_id": "271590", "title": "Grand Theft Auto V", "size": "95 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": True, "coop_count": 30, "genres": ["Open World", "Action"]},
    {"steam_app_id": "1174180", "title": "Red Dead Redemption 2", "size": "120 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": True, "coop_count": 32, "genres": ["Open World", "Action"]},
    {"steam_app_id": "1245620", "title": "Elden Ring", "size": "60 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["Action RPG", "Souls"]},
    {"steam_app_id": "1091500", "title": "Cyberpunk 2077", "size": "110 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action RPG"]},
    {"steam_app_id": "1086940", "title": "Baldur's Gate 3", "size": "150 GB", "source": "fitgirl", "is_coop": True, "is_multiplayer": True, "coop_count": 4, "genres": ["RPG", "Co-op"]},
    {"steam_app_id": "1593500", "title": "God of War", "size": "60 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action"]},
    {"steam_app_id": "1971870", "title": "Resident Evil 4 Remake", "size": "65 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror", "Action"]},
    {"steam_app_id": "1361210", "title": "Alan Wake 2", "size": "100 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Horror", "Adventure"]},
    {"steam_app_id": "2358720", "title": "Black Myth: Wukong", "size": "130 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["Action RPG"]},
    {"steam_app_id": "292030", "title": "The Witcher 3: Wild Hunt", "size": "50 GB", "source": "fitgirl", "is_coop": False, "is_multiplayer": False, "coop_count": 1, "genres": ["RPG"]},
]

# ---------- Models ----------
class Game(BaseModel):
    id: str
    title: str
    steam_app_id: Optional[str] = None
    description: str = ""
    image: str = ""
    background: str = ""
    screenshots: List[str] = []
    size: str = "—"
    year: str = "—"
    genres: List[str] = []
    source: str = "fitgirl"
    torrent_url: str = ""
    status: str = "cracked"
    is_coop: bool = False
    is_multiplayer: bool = False
    coop_count: int = 1
    steam_rating: Optional[str] = None
    steam_score: Optional[int] = None
    steam_price: Optional[str] = None
    steam_discount: Optional[int] = None
    release_date: Optional[str] = None
    is_coming_soon: bool = False
    nsfw: bool = False
    archive_password: Optional[str] = None
    last_enriched: Optional[str] = None

# ---------- Steam enrichment ----------
async def steam_appdetails(app_id: str, client_http: httpx.AsyncClient) -> Optional[dict]:
    try:
        r = await client_http.get(
            "https://store.steampowered.com/api/appdetails",
            params={"appids": app_id, "l": "english", "cc": "us"},
            timeout=15,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        entry = data.get(app_id) or data.get(int(app_id) if app_id.isdigit() else app_id)
        if not entry or not entry.get("success"):
            return None
        return entry.get("data")
    except Exception:
        return None

def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").replace("&nbsp;", " ").strip()

def enrich_game_with_steam(game: dict, data: dict) -> dict:
    """Merge curated data with Steam-fetched fields."""
    if not data:
        return game
    # title
    game["title"] = data.get("name") or game["title"]
    # images
    game["image"] = data.get("header_image") or game.get("image", "")
    game["background"] = data.get("background_raw") or data.get("background") or game.get("background", "")
    # screenshots
    shots = data.get("screenshots") or []
    game["screenshots"] = [s.get("path_full") for s in shots if s.get("path_full")][:6]
    # description
    short = data.get("short_description") or ""
    game["description"] = short or _strip_html(data.get("about_the_game", ""))[:600]
    # genres
    g = [x.get("description") for x in (data.get("genres") or []) if x.get("description")]
    if g:
        game["genres"] = list({*game.get("genres", []), *g})
    # year
    rd = data.get("release_date", {}) or {}
    dstr = rd.get("date", "")
    m = re.search(r"\b(19|20)\d{2}\b", dstr)
    if m:
        game["year"] = m.group(0)
    game["release_date"] = dstr or game.get("release_date")
    # rating from metacritic OR recommendations score (Steam doesn't expose user_review % in appdetails)
    meta = data.get("metacritic") or {}
    if meta.get("score"):
        game["steam_score"] = int(meta["score"])
        game["steam_rating"] = f"{meta['score']}/100"
    elif data.get("recommendations", {}).get("total"):
        total = data["recommendations"]["total"]
        # heuristic
        if total > 100000:
            game["steam_rating"] = "Overwhelmingly Positive"
            game["steam_score"] = 95
        elif total > 20000:
            game["steam_rating"] = "Very Positive"
            game["steam_score"] = 88
        elif total > 5000:
            game["steam_rating"] = "Mostly Positive"
            game["steam_score"] = 78
        else:
            game["steam_rating"] = "Positive"
            game["steam_score"] = 72
    # price
    po = data.get("price_overview") or {}
    if po:
        game["steam_price"] = po.get("final_formatted") or po.get("initial_formatted") or "—"
        game["steam_discount"] = po.get("discount_percent", 0) or 0
    elif data.get("is_free"):
        game["steam_price"] = "Free"
    # coming soon flag from steam too
    if rd.get("coming_soon"):
        game["is_coming_soon"] = True
    game["last_enriched"] = datetime.now(timezone.utc).isoformat()
    return game

# ---------- Steam search (lookup app_id by title) ----------
async def steam_search(title: str, http: httpx.AsyncClient) -> Optional[str]:
    """Returns Steam app_id for closest matching title, or None."""
    try:
        r = await http.get(
            "https://store.steampowered.com/api/storesearch/",
            params={"term": title, "cc": "us", "l": "en"},
            timeout=12,
        )
        if r.status_code != 200:
            return None
        items = (r.json() or {}).get("items", [])
        if not items:
            return None
        # prefer exact title match
        lower = title.lower()
        for it in items:
            if str(it.get("name", "")).lower() == lower:
                return str(it["id"])
        return str(items[0]["id"])
    except Exception:
        return None

# ---------- Bulk import from JSON file ----------
async def import_from_file():
    """Reads import_games.json, looks up each on Steam, adds to DB."""
    if not IMPORT_FILE.exists():
        logger.info("No import_games.json — skipping bulk import")
        return
    titles = _json.loads(IMPORT_FILE.read_text())
    logger.info("Bulk importing %d games via Steam search...", len(titles))
    headers = {"User-Agent": UA}
    async with httpx.AsyncClient(headers=headers) as http:
        added = 0
        for idx, g in enumerate(titles):
            title = g["title"]
            existing = await db.games.find_one({"title": {"$regex": f"^{re.escape(title)}$", "$options": "i"}}, {"_id": 0})
            if existing:
                continue
            sid = str(g.get("steam_app_id")) if g.get("steam_app_id") else None
            if not sid:
                sid = await steam_search(title, http)
            if not sid:
                await asyncio.sleep(0.3)
                continue
            # check if app_id already in db (avoid dupes)
            if await db.games.find_one({"steam_app_id": sid}, {"_id": 0}):
                continue
            # fetch full details to enrich
            data = await steam_appdetails(sid, http)
            base = {
                "id": f"g_{sid}",
                "steam_app_id": sid,
                "title": title,
                "description": "",
                "image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg",
                "background": "",
                "screenshots": [],
                "size": g.get("size", "—"),
                "year": g.get("year", "—"),
                "genres": [],
                "source": g.get("source", "fitgirl"),
                "torrent_url": "",
                "status": "cracked",
                "is_coop": False,
                "is_multiplayer": False,
                "coop_count": 1,
                "is_coming_soon": False,
                "release_date": None,
                "nsfw": False,
                "archive_password": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if data:
                base = enrich_game_with_steam(base, data)
                # heuristic: detect co-op/multi from categories
                cats = [c.get("description", "").lower() for c in (data.get("categories") or [])]
                if any("co-op" in c for c in cats): base["is_coop"] = True
                if any("multi-player" in c or "online pvp" in c for c in cats): base["is_multiplayer"] = True
            await db.games.insert_one(base)
            added += 1
            if idx % 25 == 0:
                logger.info("Imported %d/%d (added=%d)", idx, len(titles), added)
            # Steam search rate limit
            await asyncio.sleep(0.5 if idx % 20 == 0 else 0.25)
        logger.info("Bulk import done: added=%d", added)

# ---------- Torrent scrapers ----------
MAGNET_RE = re.compile(r'(magnet:\?xt=urn:btih:[A-Za-z0-9]+[^"\'<>\s]*)', re.IGNORECASE)
TORRENT_FILE_RE = re.compile(r'href="([^"]+\.torrent)"', re.IGNORECASE)

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def _title_matches(query: str, candidate: str) -> bool:
    q = _norm(query); c = _norm(candidate)
    if not q or not c: return False
    return q in c or c in q or q[:max(8, len(q)//2)] in c

async def scrape_fitgirl(title: str, http: httpx.AsyncClient) -> Optional[Dict[str, str]]:
    """Search fitgirl-repacks.site, find game post, extract magnet."""
    try:
        r = await http.get(f"https://fitgirl-repacks.site/?s={quote_plus(title)}", timeout=20)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for art in soup.find_all("article")[:5]:
            h = art.find(["h1", "h2", "h3"])
            if not h: continue
            link = h.find("a", href=True)
            if not link: continue
            post_title = h.get_text(strip=True)
            if not _title_matches(title, post_title): continue
            post_url = link["href"]
            r2 = await http.get(post_url, timeout=25)
            if r2.status_code != 200:
                return {"url": post_url, "torrent": "", "source": "fitgirl"}
            m = MAGNET_RE.search(r2.text)
            return {"url": post_url, "torrent": m.group(1) if m else "", "source": "fitgirl"}
        return None
    except Exception as e:
        logger.warning("fitgirl scrape: %s", e); return None

async def scrape_online_fix(title: str, http: httpx.AsyncClient) -> Optional[Dict[str, str]]:
    try:
        r = await http.get(f"https://online-fix.me/?do=search&subaction=search&story={quote_plus(title)}", timeout=20)
        if r.status_code != 200:
            return None
        r.encoding = "windows-1251"
        # Links to game pages: /games/<cat>/NNNN-name.html
        links = re.findall(r'<a[^>]+href="(https?://online-fix\.me/games/[^"#]+\.html)"[^>]*>([^<]+)</a>', r.text)
        seen = set()
        for url, txt in links:
            if url in seen: continue
            seen.add(url)
            # remove "по сети" suffix
            clean = re.sub(r"по сети.*", "", txt, flags=re.I).strip()
            if not _title_matches(title, clean): continue
            r2 = await http.get(url, timeout=20)
            r2.encoding = "windows-1251"
            m = MAGNET_RE.search(r2.text or "")
            return {"url": url, "torrent": m.group(1) if m else "", "source": "online-fix"}
        return None
    except Exception as e:
        logger.warning("online-fix scrape: %s", e); return None

async def scrape_steamunlocked(title: str, http: httpx.AsyncClient) -> Optional[Dict[str, str]]:
    try:
        r = await http.get(f"https://steamunlocked.net/?s={quote_plus(title)}", timeout=20)
        if r.status_code != 200:
            return None
        # match /(slug)-free-download/
        candidates = re.findall(r'href="(https?://steamunlocked\.(?:net|org)/([a-z0-9\-]+)-free-download/)"', r.text)
        for url, slug in candidates:
            if _title_matches(title, slug.replace("-", " ")):
                # SU has direct downloads, no magnet — just point to page
                return {"url": url, "torrent": "", "source": "steamunlocked"}
        return None
    except Exception as e:
        logger.warning("steamunlocked scrape: %s", e); return None

async def scrape_ankergames(title: str, http: httpx.AsyncClient) -> Optional[Dict[str, str]]:
    try:
        # AnkerGames uses /game/<slug>
        r = await http.get(f"https://ankergames.net/?s={quote_plus(title)}", timeout=20)
        if r.status_code != 200:
            r = await http.get(f"https://ankergames.net/search?q={quote_plus(title)}", timeout=20)
            if r.status_code != 200:
                return None
        candidates = re.findall(r'href="(https?://ankergames\.net/(?:game/)?([a-z0-9\-]+)/?)"', r.text)
        for url, slug in candidates:
            if "/category" in url or "/page" in url: continue
            if _title_matches(title, slug.replace("-", " ")):
                r2 = await http.get(url, timeout=20)
                m = MAGNET_RE.search(r2.text or "") if r2.status_code == 200 else None
                return {"url": url, "torrent": m.group(1) if m else "", "source": "ankergames"}
        return None
    except Exception as e:
        logger.warning("ankergames scrape: %s", e); return None

SCRAPERS = {
    "fitgirl": scrape_fitgirl,
    "online-fix": scrape_online_fix,
    "steamunlocked": scrape_steamunlocked,
    "ankergames": scrape_ankergames,
}

async def find_torrent_for(game: dict) -> Optional[Dict[str, Any]]:
    """Try all sources in priority order; return first hit."""
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as http:
        order = [game.get("source"), "fitgirl", "online-fix", "ankergames", "steamunlocked"]
        seen = set()
        for src in order:
            if not src or src in seen or src not in SCRAPERS:
                continue
            seen.add(src)
            try:
                hit = await asyncio.wait_for(SCRAPERS[src](game["title"], http), timeout=25)
            except Exception:
                hit = None
            if hit and (hit.get("torrent") or hit.get("url")):
                return hit
        return None


async def seed_catalog():
    """Insert/update curated catalog. Enrich from Steam in background."""
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 DrawCrack"}) as http:
        for idx, entry in enumerate(CATALOG):
            sid = entry["steam_app_id"]
            existing = await db.games.find_one({"steam_app_id": sid}, {"_id": 0})
            base = {
                "id": f"g_{sid}",
                "steam_app_id": sid,
                "title": entry["title"],
                "description": existing.get("description", "") if existing else "",
                "image": entry.get("image", "") if entry.get("image") else (existing.get("image", "") if existing else f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg" if sid != "0" else ""),
                "background": existing.get("background", "") if existing else "",
                "screenshots": existing.get("screenshots", []) if existing else [],
                "size": entry.get("size", "—"),
                "year": existing.get("year", "—") if existing else "—",
                "genres": entry.get("genres", []),
                "source": entry["source"],
                "torrent_url": existing.get("torrent_url", "") if existing else "",
                "status": "coming_soon" if entry.get("is_coming_soon") else "cracked",
                "is_coop": entry.get("is_coop", False),
                "is_multiplayer": entry.get("is_multiplayer", False),
                "coop_count": entry.get("coop_count", 1),
                "is_coming_soon": entry.get("is_coming_soon", False),
                "release_date": entry.get("release_date") or (existing.get("release_date") if existing else None),
                "nsfw": entry.get("nsfw", False),
                "archive_password": "online-fix.me" if entry["source"] == "online-fix" else None,
                "steam_rating": existing.get("steam_rating") if existing else None,
                "steam_score": existing.get("steam_score") if existing else None,
                "steam_price": existing.get("steam_price") if existing else None,
                "steam_discount": existing.get("steam_discount") if existing else None,
                "last_enriched": existing.get("last_enriched") if existing else None,
                "created_at": existing.get("created_at") if existing else datetime.now(timezone.utc).isoformat(),
            }
            # Enrich (best-effort, skip if Steam API fails or steam_app_id is 0)
            try:
                if sid != "0":
                    data = await steam_appdetails(sid, http)
                    if data:
                        base = enrich_game_with_steam(base, data)
            except Exception:
                pass
            await db.games.update_one({"id": base["id"]}, {"$set": base}, upsert=True)
            # be nice to Steam
            await asyncio.sleep(0.4 if idx % 5 == 0 else 0.15)
        logger.info("Seed complete: %d games", len(CATALOG))

# ---------- Routes ----------
app = FastAPI(title="DrawCrack API")
api = APIRouter(prefix="/api")
logger = logging.getLogger("drawcrack")
logging.basicConfig(level=logging.INFO)

@api.get("/")
async def root():
    return {"name": "DrawCrack API", "status": "ok"}

@api.get("/games")
async def list_games(
    status: Optional[str] = Query(None, description="cracked | coming_soon | all"),
    genre: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    only_coop: bool = False,
    only_multi: bool = False,
    limit: int = Query(10000, description="Maximum number of games to return"),
):
    q: Dict[str, Any] = {}
    if status == "cracked":
        q["is_coming_soon"] = False
    elif status == "coming_soon":
        q["is_coming_soon"] = True
    if genre and genre.lower() != "all":
        q["genres"] = {"$regex": genre, "$options": "i"}
    if source:
        q["source"] = source
    if search:
        q["title"] = {"$regex": re.escape(search), "$options": "i"}
    if only_coop:
        q["is_coop"] = True
    if only_multi:
        q["is_multiplayer"] = True
    cursor = db.games.find(q, {"_id": 0}).sort([("is_coming_soon", 1), ("steam_score", -1), ("title", 1)])
    return await cursor.to_list(limit)

@api.get("/games/stats")
async def games_stats():
    total = await db.games.count_documents({})
    cracked = await db.games.count_documents({"is_coming_soon": False})
    coming = await db.games.count_documents({"is_coming_soon": True})
    coop = await db.games.count_documents({"is_coop": True})
    return {"total": total, "cracked": cracked, "coming_soon": coming, "coop": coop}

@api.get("/games/genres")
async def genres():
    pipeline = [{"$unwind": "$genres"}, {"$group": {"_id": "$genres", "n": {"$sum": 1}}}, {"$sort": {"n": -1}}]
    out = await db.games.aggregate(pipeline).to_list(100)
    return [{"name": x["_id"], "count": x["n"]} for x in out]

@api.get("/games/{gid}")
async def get_game(gid: str):
    game = await db.games.find_one({"id": gid}, {"_id": 0})
    if not game:
        raise HTTPException(404, "Game not found")
    # If not enriched, do live enrichment now (cached after)
    if not game.get("last_enriched") and game.get("steam_app_id"):
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as http:
            data = await steam_appdetails(game["steam_app_id"], http)
            if data:
                enrich_game_with_steam(game, data)
                await db.games.update_one({"id": gid}, {"$set": game})
    return game

@api.get("/sources")
async def list_sources():
    return list(SOURCES.values())

@api.get("/sources/{sid}")
async def get_source(sid: str):
    s = SOURCES.get(sid)
    if not s:
        raise HTTPException(404, "Source not found")
    return s

@api.post("/admin/reseed")
async def reseed():
    """Triggers re-seeding in background"""
    asyncio.create_task(seed_catalog())
    return {"ok": True, "msg": "Re-seeding in background"}

@api.post("/admin/import-games")
async def trigger_import():
    """Bulk import from import_games.json in background"""
    asyncio.create_task(import_from_file())
    return {"ok": True, "msg": "Import started in background"}

@api.post("/games/{gid}/find-torrent")
async def find_torrent(gid: str):
    """Live scrape torrent for this game from FitGirl/Online-Fix/Anker/SU"""
    game = await db.games.find_one({"id": gid}, {"_id": 0})
    if not game:
        raise HTTPException(404, "Game not found")
    if game.get("torrent_url"):
        return {"ok": True, "cached": True, "torrent_url": game["torrent_url"], "source": game.get("source")}
    hit = await find_torrent_for(game)
    if not hit:
        raise HTTPException(404, "لم يتم العثور على تورنت من المصادر الأربعة. حاول لاحقاً أو ابحث يدوياً.")
    # Save (prefer magnet, else page URL)
    torrent = hit.get("torrent") or hit.get("url") or ""
    src = hit.get("source") or game.get("source")
    update = {"torrent_url": torrent, "source": src}
    if src == "online-fix":
        update["archive_password"] = "online-fix.me"
    await db.games.update_one({"id": gid}, {"$set": update})
    return {"ok": True, "cached": False, "torrent_url": torrent, "source": src, "page": hit.get("url")}

@api.post("/admin/scrape-all")
async def scrape_all(limit: int = 50):
    """Background: try to find torrents for all games missing them."""
    async def runner():
        cursor = db.games.find({"torrent_url": ""}, {"_id": 0}).limit(limit)
        games = await cursor.to_list(limit)
        for g in games:
            hit = await find_torrent_for(g)
            if hit:
                torrent = hit.get("torrent") or hit.get("url") or ""
                src = hit.get("source") or g.get("source")
                up = {"torrent_url": torrent, "source": src}
                if src == "online-fix": up["archive_password"] = "online-fix.me"
                await db.games.update_one({"id": g["id"]}, {"$set": up})
            await asyncio.sleep(1.0)
    asyncio.create_task(runner())
    return {"ok": True, "msg": f"Scraping up to {limit} games in background"}

# Register
app.include_router(api)

# Serve React static files
static_dir = ROOT / "static"
if static_dir.exists():
    # Mount the entire static directory at root level
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_start():
    await db.games.create_index("id", unique=True)
    await db.games.create_index("steam_app_id")
    await db.games.create_index("is_coming_soon")
    await db.games.create_index("title")
    # Always seed catalog (force update)
    logger.info("Seeding catalog…")
    asyncio.create_task(seed_catalog())
    # Always trigger bulk import from file (idempotent — skips existing)
    asyncio.create_task(import_from_file())

@app.on_event("shutdown")
async def on_shutdown():
    client.close()
