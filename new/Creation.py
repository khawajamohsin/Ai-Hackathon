"""Smart Bus Ticket Booking System - in-memory only (data is lost on exit)."""
from collections import Counter, defaultdict
from itertools import count

CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")
KEYS = ("route_id", "departure_city", "destination_city", "departure_time", "ticket_price", "total_seats")
ROUTES = (("R101", "Karachi", "Hyderabad", "08:00 AM", 1200, 40),
          ("R102", "Karachi", "Sukkur", "09:30 AM", 2000, 36),
          ("R103", "Hyderabad", "Mirpur Khas", "11:00 AM", 800, 32),
          ("R104", "Karachi", "Lahore", "07:00 PM", 5000, 45),
          ("R105", "Sukkur", "Hyderabad", "02:00 PM", 1500, 30))

routes = {r[0]: dict(zip(KEYS, r), available_seats=r[5]) for r in ROUTES}  # id -> route, in order
bookings: dict[str, dict] = {}   # id -> booking; insertion order = history, keys = issued IDs
booking_ids = count(1001)

# ---------- Languages ----------
LANGUAGES = ("English", "اردو (Urdu)", "سنڌي (Sindhi)", "پنجابی (Punjabi)",
             "بلوچی (Balochi)", "پښتو (Pashto)", "سرائیکی (Saraiki)")
lang = 0   # index into LANGUAGES; 0 = English (the messages written in the code)

# English message -> (Urdu, Sindhi, Punjabi, Balochi, Pashto, Saraiki)
TEXT = {
    "SMART BUS RESERVATION SYSTEM": ("سمارٹ بس ریزرویشن سسٹم", "سمارٽ بس ريزرويشن سسٽم", "سمارٹ بس ریزرویشن سسٹم", "سمارٹ بس ریزرویشن سسٹم", "سمارټ بس ریزرویشن سیسټم", "سمارٹ بس ریزرویشن سسٹم"),
    "View Available Routes": ("دستیاب روٹس دیکھیں", "دستياب رستا ڏسو", "دستیاب روٹ ویکھو", "دستیاب روٹ بگند", "شته لارې وګورئ", "دستیاب روٹ ݙیکھو"),
    "Search for a Route": ("روٹ تلاش کریں", "رستو ڳوليو", "روٹ لبھو", "روٹ تلاش بکن", "لاره ولټوئ", "روٹ لبھو"),
    "Book a Ticket": ("ٹکٹ بک کریں", "ٽڪيٽ بُڪ ڪريو", "ٹکٹ بک کرو", "ٹکٹ بک بکن", "ټکټ بک کړئ", "ٹکٹ بک کرو"),
    "View My Bookings": ("میری بکنگز دیکھیں", "منهنجيون بُڪنگون ڏسو", "میریاں بکنگاں ویکھو", "منی بکنگ بگند", "زما بکنګونه وګورئ", "میڈیاں بکنگاں ݙیکھو"),
    "Cancel a Booking": ("بکنگ منسوخ کریں", "بُڪنگ رد ڪريو", "بکنگ رد کرو", "بکنگ رد بکن", "بکنګ لغوه کړئ", "بکنگ منسوخ کرو"),
    "View Seat Availability": ("نشستوں کی دستیابی دیکھیں", "سيٽن جي دستيابي ڏسو", "سیٹاں دی دستیابی ویکھو", "سیٹءِ دستیابی بگند", "د څوکیو شتون وګورئ", "سیٹاں دی دستیابی ݙیکھو"),
    "Generate Booking Report": ("بکنگ رپورٹ بنائیں", "بُڪنگ رپورٽ ٺاهيو", "بکنگ رپورٹ بݨاؤ", "بکنگ رپورٹ جوڑ بکن", "د بکنګ راپور جوړ کړئ", "بکنگ رپورٹ بݨاؤ"),
    "Exit": ("باہر نکلیں", "ٻاهر نڪرو", "باہر نکلو", "باہر بشو", "وتل", "باہر نکلو"),
    "Enter your choice: ": ("اپنا انتخاب درج کریں: ", "پنهنجي چونڊ داخل ڪريو: ", "اپنی چوݨ پاؤ: ", "وتی انتخاب درج بکن: ", "خپل انتخاب داخل کړئ: ", "اپڑی چُݨ درج کرو: "),
    "Invalid choice. Please enter a number from 1 to 8.": ("غلط انتخاب۔ براہ کرم 1 سے 8 تک نمبر درج کریں۔", "غلط چونڊ. مهرباني ڪري 1 کان 8 تائين نمبر داخل ڪريو.", "غلط چوݨ۔ مہربانی کر کے 1 توں 8 تیک نمبر پاؤ۔", "غلط انتخاب. مہربانی 1 چہ 8 تان نمبر درج بکن.", "ناسم انتخاب. مهرباني وکړئ له 1 څخه تر 8 پورې شمیره داخل کړئ.", "غلط چُݨ۔ مہربانی کر تے 1 توں 8 تئیں نمبر درج کرو۔"),
    "Thank you for using Smart Bus. Goodbye!": ("سمارٹ بس استعمال کرنے کا شکریہ۔ خدا حافظ!", "سمارٽ بس استعمال ڪرڻ جي مهرباني. خدا حافظ!", "سمارٹ بس ورتݨ دا شکریہ۔ خدا حافظ!", "سمارٹ بس استعمال کنگءَ شُکر. خدا حافظ!", "د سمارټ بس د کارولو مننه. په مخه ښه!", "سمارٹ بس ورتݨ دا مہربانی۔ خدا حافظ!"),
    "\n1) All routes  2) Only with seats  3) Schedule by city (default 1): ": ("\n1) تمام روٹس  2) صرف خالی نشستوں والے  3) شہر کے لحاظ سے شیڈول (پہلے سے طے 1): ", "\n1) سڀ رستا  2) رڳو سيٽن وارا  3) شهر موجب شيڊيول (ڊفالٽ 1): ", "\n1) سارے روٹ  2) صرف سیٹاں والے  3) شہر مطابق شیڈول (ڈیفالٹ 1): ", "\n1) تمام روٹ  2) فقط سیٹ والا  3) شہر وار شیڈول (ڈیفالٹ 1): ", "\n1) ټولې لارې  2) یوازې د څوکیو سره  3) د ښار له مخې مهال ویش (تلوالیز 1): ", "\n1) سارے روٹ  2) صرف سیٹاں آلے  3) شہر مطابق شیڈول (ڈیفالٹ 1): "),
    "AVAILABLE BUS ROUTES": ("دستیاب بس روٹس", "دستياب بس رستا", "دستیاب بس روٹ", "دستیاب بس روٹ", "شته بس لارې", "دستیاب بس روٹ"),
    "No.": ("نمبر", "نمبر", "نمبر", "نمبر", "شمېره", "نمبر"),
    "Route": ("روٹ", "رستو", "روٹ", "روٹ", "لاره", "روٹ"),
    "Journey": ("سفر", "سفر", "سفر", "سفر", "سفر", "سفر"),
    "Depart": ("روانگی", "روانگي", "روانگی", "روانگی", "حرکت", "روانگی"),
    "Fare": ("کرایہ", "ڀاڙو", "کرایہ", "کرایہ", "کرایه", "کرایہ"),
    "Seats": ("نشستیں", "سيٽون", "سیٹاں", "سیٹ", "څوکۍ", "سیٹاں"),
    "Fully Booked": ("مکمل بک", "مڪمل بُڪ", "پوری بک", "پورا بک", "بشپړ بک", "پوری بک"),
    "seats available": ("نشستیں دستیاب", "سيٽون دستياب", "سیٹاں دستیاب", "سیٹ دستیاب", "څوکۍ شته", "سیٹاں دستیاب"),
    "ROUTE SCHEDULE BY DEPARTURE CITY": ("روانگی کے شہر کے مطابق روٹ شیڈول", "روانگيءَ واري شهر موجب رستن جو شيڊيول", "روانگی دے شہر مطابق روٹ شیڈول", "روانگیءِ شہرءِ روٹ شیڈول", "د حرکت د ښار له مخې د لارو مهال ویش", "روانگی دے شہر مطابق روٹ شیڈول"),
    "No scheduled departures.": ("کوئی طے شدہ روانگی نہیں۔", "ڪا مقرر روانگي ناهي.", "کوئی مقرر روانگی نہیں۔", "هچ روانگی نیست.", "هیڅ ټاکلی حرکت نشته.", "کوئی مقرر روانگی کینی۔"),
    "Search by route ID or city: ": ("روٹ آئی ڈی یا شہر سے تلاش کریں: ", "رستي جي آئي ڊي يا شهر سان ڳوليو: ", "روٹ آئی ڈی یا شہر نال لبھو: ", "روٹ آئی ڈی یا شہرءَ تلاش بکن: ", "د لارې آی ډي یا ښار په اساس ولټوئ: ", "روٹ آئی ڈی یا شہر نال لبھو: "),
    "Please enter a route ID or city name.": ("براہ کرم روٹ آئی ڈی یا شہر کا نام درج کریں۔", "مهرباني ڪري رستي جي آئي ڊي يا شهر جو نالو داخل ڪريو.", "مہربانی کر کے روٹ آئی ڈی یا شہر دا ناں پاؤ۔", "مہربانی روٹ آئی ڈی یا شہرءِ ناں درج بکن.", "مهرباني وکړئ د لارې آی ډي یا د ښار نوم داخل کړئ.", "مہربانی کر تے روٹ آئی ڈی یا شہر دا ناں درج کرو۔"),
    "No routes found for '{}'.": ("'{}' کے لیے کوئی روٹ نہیں ملا۔", "'{}' لاءِ ڪو رستو نه مليو.", "'{}' لئی کوئی روٹ نہیں لبھیا۔", "'{}' ءِ واسطہ کوئی روٹ نہ ملا۔", "د '{}' لپاره هیڅ لاره ونه موندل شوه.", "'{}' واسطے کوئی روٹ نہیں لبھیا۔"),
    "Passenger name: ": ("مسافر کا نام: ", "مسافر جو نالو: ", "مسافر دا ناں: ", "مسافرءِ ناں: ", "د مسافر نوم: ", "مسافر دا ناں: "),
    "Passenger age: ": ("مسافر کی عمر: ", "مسافر جي عمر: ", "مسافر دی عمر: ", "مسافرءِ عمر: ", "د مسافر عمر: ", "مسافر دی عمر: "),
    "Route ID: ": ("روٹ آئی ڈی: ", "رستي جي آئي ڊي: ", "روٹ آئی ڈی: ", "روٹ آئی ڈی: ", "د لارې آی ډي: ", "روٹ آئی ڈی: "),
    "Number of seats: ": ("نشستوں کی تعداد: ", "سيٽن جو تعداد: ", "سیٹاں دی گنتی: ", "سیٹءِ تعداد: ", "د څوکیو شمېر: ", "سیٹاں دی گنتی: "),
    "Rejected: name cannot be empty.": ("مسترد: نام خالی نہیں ہو سکتا۔", "رد: نالو خالي نه ٿو ٿي سگهي.", "رد: ناں خالی نہیں ہو سکدا۔", "رد: ناں خالی نہ بیت.", "ردول شو: نوم خالي نشي کیدای.", "رد: ناں خالی نہیں تھی سڳدا۔"),
    "Rejected: age must be a positive whole number.": ("مسترد: عمر مثبت پورا عدد ہونی چاہیے۔", "رد: عمر مثبت مڪمل عدد هجڻ گهرجي.", "رد: عمر مثبت پورا عدد ہونی چاہیدی اے۔", "رد: عمر مثبت پورا عدد بیت.", "ردول شو: عمر باید مثبت بشپړ عدد وي.", "رد: عمر مثبت پورا عدد ہووݨ چاہیدی ہے۔"),
    "Rejected: route not found.": ("مسترد: روٹ نہیں ملا۔", "رد: رستو نه مليو.", "رد: روٹ نہیں لبھیا۔", "رد: روٹ نہ ملا.", "ردول شو: لاره ونه موندل شوه.", "رد: روٹ نہیں لبھیا۔"),
    "Rejected: seats must be a positive whole number.": ("مسترد: نشستیں مثبت پورا عدد ہونی چاہئیں۔", "رد: سيٽون مثبت مڪمل عدد هجڻ گهرجن.", "رد: سیٹاں مثبت پورا عدد ہونیاں چاہیدیاں نیں۔", "رد: سیٹ مثبت پورا عدد بیت.", "ردول شو: څوکۍ باید مثبت بشپړ عدد وي.", "رد: سیٹاں مثبت پورا عدد ہووݨ چاہیدیاں ہن۔"),
    "Rejected: only {} seat(s) available.": ("مسترد: صرف {} نشست(یں) دستیاب ہیں۔", "رد: رڳو {} سيٽ(ون) دستياب آهن.", "رد: صرف {} سیٹ(اں) دستیاب نیں۔", "رد: فقط {} سیٹ دستیاب انت.", "ردول شو: یوازې {} څوکۍ شته.", "رد: صرف {} سیٹ(اں) دستیاب ہن۔"),
    "Booking confirmed!": ("بکنگ کی تصدیق ہو گئی!", "بُڪنگ جي تصديق ٿي وئي!", "بکنگ دی تصدیق ہو گئی!", "بکنگ تصدیق بوت!", "بکنګ تایید شو!", "بکنگ دی تصدیق تھی گئی!"),
    "Booking ID": ("بکنگ آئی ڈی", "بُڪنگ آئي ڊي", "بکنگ آئی ڈی", "بکنگ آئی ڈی", "د بکنګ آی ډي", "بکنگ آئی ڈی"),
    "Passenger": ("مسافر", "مسافر", "مسافر", "مسافر", "مسافر", "مسافر"),
    "Seats booked": ("بک شدہ نشستیں", "بُڪ ٿيل سيٽون", "بک سیٹاں", "بک سیٹ", "بک شوې څوکۍ", "بک سیٹاں"),
    "Fare per seat": ("فی نشست کرایہ", "في سيٽ ڀاڙو", "فی سیٹ کرایہ", "هر سیٹءِ کرایہ", "د هرې څوکۍ کرایه", "فی سیٹ کرایہ"),
    "Total fare": ("کل کرایہ", "ڪل ڀاڙو", "کل کرایہ", "کل کرایہ", "ټول کرایه", "کل کرایہ"),
    "Status": ("حیثیت", "حيثيت", "حیثیت", "حالت", "حالت", "حیثیت"),
    "Confirmed": ("تصدیق شدہ", "تصديق ٿيل", "تصدیق شدہ", "تصدیق بوتگ", "تایید شوی", "تصدیق شدہ"),
    "Cancelled": ("منسوخ", "رد ٿيل", "رد", "رد بوتگ", "لغوه شوی", "منسوخ"),
    "MY BOOKINGS": ("میری بکنگز", "منهنجيون بُڪنگون", "میریاں بکنگاں", "منی بکنگ", "زما بکنګونه", "میڈیاں بکنگاں"),
    "seat(s)": ("نشست(یں)", "سيٽ(ون)", "سیٹ(اں)", "سیٹ", "څوکۍ", "سیٹ(اں)"),
    "No bookings found.": ("کوئی بکنگ نہیں ملی۔", "ڪا بُڪنگ نه ملي.", "کوئی بکنگ نہیں لبھی۔", "کوئی بکنگ نہ ملی.", "هیڅ بکنګ ونه موندل شو.", "کوئی بکنگ نہیں لبھی۔"),
    "Enter booking ID to cancel: ": ("منسوخ کرنے کے لیے بکنگ آئی ڈی درج کریں: ", "رد ڪرڻ لاءِ بُڪنگ آئي ڊي داخل ڪريو: ", "رد کرن لئی بکنگ آئی ڈی پاؤ: ", "رد کنگءِ واسطہ بکنگ آئی ڈی درج بکن: ", "د لغوه کولو لپاره د بکنګ آی ډي داخل کړئ: ", "منسوخ کرݨ واسطے بکنگ آئی ڈی درج کرو: "),
    "Booking ID '{}' not found.": ("بکنگ آئی ڈی '{}' نہیں ملی۔", "بُڪنگ آئي ڊي '{}' نه ملي.", "بکنگ آئی ڈی '{}' نہیں لبھی۔", "بکنگ آئی ڈی '{}' نہ ملی.", "د بکنګ آی ډي '{}' ونه موندل شو.", "بکنگ آئی ڈی '{}' نہیں لبھی۔"),
    "Booking {} is already cancelled. No seats restored.": ("بکنگ {} پہلے ہی منسوخ ہے۔ کوئی نشست بحال نہیں ہوئی۔", "بُڪنگ {} اڳ ۾ ئي رد ٿيل آهي. ڪا سيٽ بحال نه ٿي.", "بکنگ {} پہلاں ای رد اے۔ کوئی سیٹ بحال نہیں ہوئی۔", "بکنگ {} پیسر رد بوتگ. هچ سیٹ بحال نہ بوت.", "بکنګ {} دمخه لغوه شوی دی. هیڅ څوکۍ بیرته نه ده شوې.", "بکنگ {} پہلے ای منسوخ ہے۔ کوئی سیٹ بحال نہیں تھئی۔"),
    "Booking {} has been cancelled.": ("بکنگ {} منسوخ کر دی گئی۔", "بُڪنگ {} رد ڪئي وئي.", "بکنگ {} رد کر دتی گئی۔", "بکنگ {} رد بوت.", "بکنګ {} لغوه شو.", "بکنگ {} منسوخ کر ݙتی گئی۔"),
    "Seats restored": ("بحال شدہ نشستیں", "بحال ٿيل سيٽون", "بحال سیٹاں", "بحال سیٹ", "بیرته شوې څوکۍ", "بحال سیٹاں"),
    "available seats": ("دستیاب نشستیں", "دستياب سيٽون", "دستیاب سیٹاں", "دستیاب سیٹ", "شته څوکۍ", "دستیاب سیٹاں"),
    "Show only routes with seats? (y/n): ": ("صرف نشستوں والے روٹس دکھائیں؟ (y/n): ", "رڳو سيٽن وارا رستا ڏيکاريو؟ (y/n): ", "صرف سیٹاں والے روٹ وکھاؤ؟ (y/n): ", "فقط سیٹ والا روٹ پیش بکن؟ (y/n): ", "یوازې د څوکیو سره لارې وښایاست؟ (y/n): ", "صرف سیٹاں آلے روٹ ݙکھاؤ؟ (y/n): "),
    "SEAT AVAILABILITY": ("نشستوں کی دستیابی", "سيٽن جي دستيابي", "سیٹاں دی دستیابی", "سیٹءِ دستیابی", "د څوکیو شتون", "سیٹاں دی دستیابی"),
    "No routes have seats available.": ("کسی روٹ میں نشستیں دستیاب نہیں۔", "ڪنهن رستي ۾ سيٽون دستياب ناهن.", "کسے روٹ وچ سیٹاں دستیاب نہیں۔", "هچ روٹءَ سیٹ دستیاب نیست.", "په هیڅ لاره کې څوکۍ شته نه دي.", "کہیں روٹ وچ سیٹاں دستیاب کینی۔"),
    "Available": ("دستیاب", "دستياب", "دستیاب", "دستیاب", "شته", "دستیاب"),
    "Partially Booked": ("جزوی بک", "جزوي بُڪ", "جزوی بک", "کمی بک", "نیمګړی بک", "جزوی بک"),
    "BOOKING REPORT": ("بکنگ رپورٹ", "بُڪنگ رپورٽ", "بکنگ رپورٹ", "بکنگ رپورٹ", "د بکنګ راپور", "بکنگ رپورٹ"),
    "Total bookings created": ("کل بنائی گئی بکنگز", "ڪل ٺاهيل بُڪنگون", "کل بنائیاں بکنگاں", "کل جوڑ بوتگین بکنگ", "ټولې جوړې شوې بکنګونه", "کل بݨیاں بکنگاں"),
    "Confirmed bookings": ("تصدیق شدہ بکنگز", "تصديق ٿيل بُڪنگون", "تصدیق شدہ بکنگاں", "تصدیق بوتگین بکنگ", "تایید شوې بکنګونه", "تصدیق شدہ بکنگاں"),
    "Cancelled bookings": ("منسوخ بکنگز", "رد ٿيل بُڪنگون", "رد بکنگاں", "رد بوتگین بکنگ", "لغوه شوې بکنګونه", "منسوخ بکنگاں"),
    "Seats currently reserved": ("اس وقت محفوظ نشستیں", "هن وقت محفوظ سيٽون", "ہن محفوظ سیٹاں", "هنوکین محفوظ سیٹ", "اوس خوندي څوکۍ", "ہنڑ محفوظ سیٹاں"),
    "Confirmed revenue": ("تصدیق شدہ آمدنی", "تصديق ٿيل آمدني", "تصدیق شدہ آمدن", "تصدیق بوتگین آمدن", "تایید شوې عاید", "تصدیق شدہ آمدن"),
    "Fully booked routes": ("مکمل بک روٹس", "مڪمل بُڪ رستا", "پورے بک روٹ", "پورا بک روٹ", "بشپړې بکې لارې", "پورے بک روٹ"),
    "Confirmed bookings by route:": ("روٹ کے لحاظ سے تصدیق شدہ بکنگز:", "رستي موجب تصديق ٿيل بُڪنگون:", "روٹ مطابق تصدیق شدہ بکنگاں:", "روٹ وار تصدیق بوتگین بکنگ:", "د لارې له مخې تایید شوې بکنګونه:", "روٹ مطابق تصدیق شدہ بکنگاں:"),
    "None.": ("کوئی نہیں۔", "ڪو نه.", "کوئی نہیں۔", "هچ نیست.", "هیڅ نشته.", "کوئی کینی۔"),
}


def tr(text):
    """Return the message in the chosen language (falls back to English)."""
    return TEXT[text][lang - 1] if lang and text in TEXT else text


def choose_language():
    """Ask the user for a language once at startup; anything invalid keeps English."""
    global lang
    print("\nChoose your language / زبان منتخب کریں")
    for i, name in enumerate(LANGUAGES, 1):
        print(f"{i}. {name}")
    choice = input("> ").strip()
    lang = int(choice) - 1 if choice.isdecimal() and 1 <= int(choice) <= len(LANGUAGES) else 0



def num(prompt):
    """Positive whole number, else None."""
    s = input(prompt).strip()
    return int(s) if s.isdecimal() and int(s) > 0 else None


def journey(r):
    return f"{r['departure_city']} -> {r['destination_city']}"


def route_line(r):
    return f"{r['route_id']} | {journey(r)} | Rs. {r['ticket_price']} | {r['available_seats']} {tr('seats available')}"


def schedule():
    by_city = defaultdict(list)
    for r in routes.values():
        by_city[r["departure_city"]].append(f"  {r['route_id']} -> {r['destination_city']} | {r['departure_time']}")
    print("\n".join(["\n" + tr("ROUTE SCHEDULE BY DEPARTURE CITY"),
                     *(line for c in CITIES for line in (c, *(by_city[c] or ["  " + tr("No scheduled departures.")])))]))


def list_routes():
    mode = input(tr("\n1) All routes  2) Only with seats  3) Schedule by city (default 1): ")).strip()
    if mode == "3":
        return schedule()
    rows = [f"{n:<4}{r['route_id']:<7}{journey(r):<28}{r['departure_time']:<10}{'Rs.' + str(r['ticket_price']):<10}"
            + (f"{r['available_seats']}/{r['total_seats']}" if r["available_seats"] else tr("Fully Booked"))
            for n, r in enumerate(routes.values(), 1) if mode != "2" or r["available_seats"]]
    print("\n".join(["\n" + tr("AVAILABLE BUS ROUTES"), f"{tr('No.'):<4}{tr('Route'):<7}{tr('Journey'):<28}{tr('Depart'):<10}{tr('Fare'):<10}{tr('Seats')}", *rows]))


def search():
    if not (t := input(tr("Search by route ID or city: ")).strip()):
        return print(tr("Please enter a route ID or city name."))
    hits = [hit] if (hit := routes.get(t.upper())) else [
        r for r in routes.values() if t.lower() in (r["departure_city"].lower(), r["destination_city"].lower())]
    print("\n".join(map(route_line, hits)) or tr("No routes found for '{}'.").format(t.lower()))


def book():
    if not (name := input(tr("Passenger name: ")).strip()):
        return print(tr("Rejected: name cannot be empty."))
    if not (age := num(tr("Passenger age: "))):
        return print(tr("Rejected: age must be a positive whole number."))
    if not (route := routes.get(input(tr("Route ID: ")).strip().upper())):
        return print(tr("Rejected: route not found."))
    if not (seats := num(tr("Number of seats: "))):
        return print(tr("Rejected: seats must be a positive whole number."))
    if seats > route["available_seats"]:
        return print(tr("Rejected: only {} seat(s) available.").format(route["available_seats"]))

    bid = f"B{next(booking_ids)}"    # counter never repeats, so IDs are unique
    fare = route["ticket_price"] * seats
    bookings[bid] = {"booking_id": bid, "passenger_name": name, "passenger_age": age,
                     "route_id": route["route_id"], "seats": seats, "total_fare": fare, "status": "Confirmed"}
    route["available_seats"] -= seats
    print(f"\n{tr('Booking confirmed!')}\n{tr('Booking ID')}: {bid}\n{tr('Passenger')}: {name}\n"
          f"{tr('Route')}: {route['route_id']} ({journey(route)})\n{tr('Seats booked')}: {seats}\n"
          f"{tr('Fare per seat')}: Rs. {route['ticket_price']}\n{tr('Total fare')}: Rs. {fare}\n"
          f"{tr('Status')}: {tr('Confirmed')}")


def my_bookings():
    print("\n".join(["\n" + tr("MY BOOKINGS"), *(
        f"{n}. {b['booking_id']} | {b['passenger_name']} | {b['route_id']} | {b['seats']} {tr('seat(s)')} | "
        f"Rs. {b['total_fare']} | {tr(b['status'])}" for n, b in enumerate(bookings.values(), 1))])
          if bookings else tr("No bookings found."))


def cancel():
    bid = input(tr("Enter booking ID to cancel: ")).strip().upper()
    if not (b := bookings.get(bid)):
        return print(tr("Booking ID '{}' not found.").format(bid))
    if b["status"] != "Confirmed":
        return print(tr("Booking {} is already cancelled. No seats restored.").format(bid))
    r = routes[b["route_id"]]
    r["available_seats"] += b["seats"]
    b["status"] = "Cancelled"
    print(f"{tr('Booking {} has been cancelled.').format(bid)}\n{tr('Seats restored')}: {b['seats']}\n"
          f"{tr('Route')} {r['route_id']} {tr('available seats')}: {r['available_seats']}")


def availability():
    only = input(tr("Show only routes with seats? (y/n): ")).strip().lower() == "y"
    rows = [f"{r['route_id']} | {journey(r)} | {r['available_seats']}/{r['total_seats']} | "
            + tr("Fully Booked" if not r["available_seats"] else
                 "Available" if r["available_seats"] == r["total_seats"] else "Partially Booked")
            for r in routes.values() if r["available_seats"] or not only]
    print("\n".join(["\n" + tr("SEAT AVAILABILITY"), *rows]) if rows else tr("No routes have seats available."))


def report():
    confirmed = 0
    seats, revenue = Counter(), Counter()            # per route ID
    for b in bookings.values():                      # single pass
        if b["status"] == "Confirmed":
            confirmed += 1
            seats[b["route_id"]] += b["seats"]
            revenue[b["route_id"]] += b["total_fare"]
    rows = [f"  {rid}: {s} {tr('seat(s)')}, Rs. {revenue[rid]:,}" for rid, s in seats.items()] or ["  " + tr("None.")]
    print("\n".join(["\n" + tr("BOOKING REPORT"), f"{tr('Total bookings created')}: {len(bookings)}",
                     f"{tr('Confirmed bookings')}: {confirmed}", f"{tr('Cancelled bookings')}: {len(bookings) - confirmed}",
                     f"{tr('Seats currently reserved')}: {seats.total()}", f"{tr('Confirmed revenue')}: Rs. {revenue.total():,}",
                     f"{tr('Fully booked routes')}: {sum(not r['available_seats'] for r in routes.values())}",
                     "\n" + tr("Confirmed bookings by route:"), *rows]))


ITEMS = ("View Available Routes", "Search for a Route", "Book a Ticket", "View My Bookings",
         "Cancel a Booking", "View Seat Availability", "Generate Booking Report", "Exit")
def menu():
    return ("\n" + tr("SMART BUS RESERVATION SYSTEM") + "\n" + "=" * 32 + "\n"
            + "\n".join(f"{i}. {tr(t)}" for i, t in enumerate(ITEMS, 1)) + "\n" + "=" * 32)


ACTIONS = dict(zip("1234567", (list_routes, search, book, my_bookings, cancel, availability, report)))


def main():
    choose_language()
    while (choice := input(menu() + "\n" + tr("Enter your choice: ")).strip()) != "8":
        ACTIONS.get(choice, lambda: print(tr("Invalid choice. Please enter a number from 1 to 8.")))()
    print(tr("Thank you for using Smart Bus. Goodbye!"))


if __name__ == "__main__":
    main()
