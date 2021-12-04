
translations = (
    "advertensie",          # Afrikaans
    "shpallje",             # Albanian
    "ማስታወቂያ",              # Amharic
    "الإعلانات",             # Arabic
    "գովազդ",               # Armenian
    "Հայտարարություն",      # Armenian
    "reklam",               # Azerbaijani, Turkish, Maltese, Haitian Creole
    "iragarkia",            # Basque
    "рэклама",              # Belarusian
    "বিজ্ঞাপন",                # Bengali
    "reklama",              # Bosnian, Czech, Polish, Slovak, Uzbek
    "реклама",              # Bulgarian, Macedonian, Serbian, Tajik, Tatar
    "inzerát",              # Czech
    "anunci",               # Catalan
    "advertisement",        # Cebuano
    "kutsatsa",             # Chichewa
    "malonda",              # Chichewa
    "广告",                  # Chinese (Simplified)
    "廣告",                  # Chinese (Traditional)
    "publicità",            # Corsican
    "oglas",                # Croatian, Slovenian
    "reklame",              # Danish
    "advertentie",          # Dutch
    "Ad",                   # English
    "reklamo",              # Esperanto
    "reklaam",              # Estonian
    "patalastas",           # Filipino
    "mainos",               # Finnish
    "ilmoitus",             # Finnish
    "publicité",            # French
    "annonce",              # French, Luxembourgish
    "advertinsje",          # Frisian
    "publicidade",          # Galician
    "რეკლამა",              # Georgian
    "Werbung",              # German
    "διαφήμιση",            # Greek
    "જાહેરાત",                 # Gujarati
    "talla",                # Hausa
    "hoʻolaha",             # Hawaiian
    "פרסומת",                 # Hebrew
    "विज्ञापन",                # Hindi
    "kev tshaj tawm",       # Humong
    "hirdetés",             # Hungarian
    "auglýsingu",           # Icelanding
    "mgbasa ozi",           # Igbo
    "iklan",                # Indonesian, Malay, Sundanese
    "fógra",                # Irish
    "annuncio",             # Italian
    "広告",                  # Japanese
    "pariwara",             # Javanese
    "ಜಾಹೀರಾತು",             # Kannada
    "жарнама",              # Kazakh
    "ការផ្សាយពាណិជ្ជកម្ម",      # Khmer
    "kwamamaza",            # Kinyarwanda
    "광고",                  # Korean
    "gilî",                 # Kurdish(Kurmanji)
    "жарнама",              # Kyrgyz
    "ການ​ໂຄ​ສະ​ນາ​",            # Lao
    "tabula",               # Latin
    "reklāma",              # Latvian
    "skelbimas",            # Lithuanian
    "dokam-barotra",        # Malagasy
    "പരസ്യം",                # Malayalam
    "pānuitanga",           # Maori
    "जाहिरात",                # Marathi
    "сурталчилгаа",         # Mongolian
    "ကြော်ငြာ",                # Myanmar(Burmese)
    "विज्ञापन",                # Nepali
    "annonse",              # Norwegian
    "ବିଜ୍ଞାପନ",                # Odia(Oria)
    "اعلان",                 # Pashto
    "تبلیغات",              # Persian
    "ogłoszenie",           # Polish
    "anúncio",              # Portuguese
    "ਇਸ਼ਤਿਹਾਰ",               # Punjabi
    "publicitate",          # Romanian
    "anunț",                # Romanian
    "объявление",           # Russian
    "fa'asalalauga",        # Samoan
    "sanas",                # Scots Gaelic
    "papatso",              # Sesotho
    "kushambadzira",        # Shona
    "اشتهار",               # Sindhi
    "වෙළඳ දැන්වීම",          # Sinhala
    "xayaysiis",            # Somali
    "anuncio publicitario", # Spanish
    "tangazo",              # Swahili
    "annons",               # Swedish
    "விளம்பரம்",             # Tamil
    "ప్రకటన",                 # Telugu
    "โฆษณา",               # Thai
    "mahabat",              # Turkmen
    "реклам",               # Ukranian
    "оголошення",           # Ukranian
    "اشتہار",               # Urdu
    "ئېلان",                 # Uyghur
    "e'lon",                # Uzbek
    "Quảng cáo",            # Vietnamese
    "hysbyseb",             # Welsh
    "isibhengezo",          # Xhosa
    "אַדווערטייזמאַנט",            # Yiddish
    "ipolongo",             # Yoruba
    "isikhangiso",          # Zulu
)


def contains_ad(ad_text):

    return any(translation.lower() in ad_text for translation in translations)
