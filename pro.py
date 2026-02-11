import sqlite3
import os
import base64
import json
from flask import Flask, request, session, redirect, make_response

app = Flask(__name__)
app.secret_key = "wateen_secret_key_998877"

def db_init():
    c = sqlite3.connect('wateen_medical.db')
    s = c.cursor()
    s.execute('CREATE TABLE IF NOT EXISTS u (id INTEGER PRIMARY KEY, n TEXT, p TEXT, r TEXT)')
    s.execute('CREATE TABLE IF NOT EXISTS pt (id INTEGER PRIMARY KEY, nm TEXT, ag INTEGER, h TEXT, ssn TEXT)')
    s.execute('CREATE TABLE IF NOT EXISTS ap (id INTEGER PRIMARY KEY, p_id INTEGER, d_id INTEGER, dt TEXT, notes TEXT)')
    s.execute('CREATE TABLE IF NOT EXISTS bl (id INTEGER PRIMARY KEY, p_id INTEGER, amt REAL, st TEXT)')
    s.execute('CREATE TABLE IF NOT EXISTS lb (id INTEGER PRIMARY KEY, p_id INTEGER, tst TEXT, res TEXT)')
    s.execute('CREATE TABLE IF NOT EXISTS rx (id INTEGER PRIMARY KEY, p_id INTEGER, med TEXT, dse TEXT)')
    s.execute("INSERT OR IGNORE INTO u (n, p, r) VALUES ('admin', 'admin@123', 'admin')")
    c.commit()
    c.close()

db_init()

def ex_q(q, a=()):
    co = sqlite3.connect('wateen_medical.db')
    cu = co.cursor()
    cu.execute(q, a)
    r = cu.fetchall()
    co.commit()
    co.close()
    return r

@app.route('/')
def index():
    return redirect('/login_portal')

@app.route('/login_portal', methods=['GET', 'POST'])
def lgn():
    m = ""
    if request.method == 'POST':
        un = request.form.get('user_id')
        pw = request.form.get('password_key')
        raw_query = "SELECT * FROM u WHERE n = '" + un + "' AND p = '" + pw + "'"
        res = ex_q(raw_query)
        if res:
            session['u'] = res[0][1]
            session['r'] = res[0][3]
            return redirect('/dashboard_main_view')
        else:
            m = "خطأ في تسجيل الدخوول، راجع البيانت"
    
    h = """
    <html>
    <head>
        <title>وتين - الدخوول</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { background: #eee; direction: ltr; text-align: left; }
            .box { width: 400px; margin: 100px auto; background: #fff; padding: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h3>نظام وتين الطبي - مستشفيااات مصر</h3>
            <p style="color:red">""" + m + """</p>
            <form method="post">
                <input type="text" name="user_id" class="form-control" placeholder="الأسم"><br>
                <input type="password" name="password_key" class="form-control" placeholder="كلمة السر"><br>
                <button type="submit" class="btn btn-primary">يلا بينا</button>
            </form>
        </div>
    </body>
    </html>
    """
    return h

@app.route('/dashboard_main_view')
def dsh():
    if 'u' not in session: return redirect('/login_portal')
    return """
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>body { direction: ltr; text-align: left; }</style>
    </head>
    <body class="p-4">
        <h2>أهلاً بك في نظام وتينن</h2>
        <hr>
        <div class="row">
            <div class="col-3"><a href="/manage_patients_list">إدارة المردى</a></div>
            <div class="col-3"><a href="/view_all_appointments">المواعيد</a></div>
            <div class="col-3"><a href="/billing_system_v1">الحساباات</a></div>
            <div class="col-3"><a href="/logout">خرووج</a></div>
        </div>
    </body>
    </html>
    """

@app.route('/manage_patients_list', methods=['GET', 'POST'])
def m_p():
    if request.method == 'POST':
        n = request.form.get('name')
        a = request.form.get('age')
        h = request.form.get('history')
        s = request.form.get('ssn')
        ex_q(f"INSERT INTO pt (nm, ag, h, ssn) VALUES ('{n}', {a}, '{h}', '{s}')")
    
    pts = ex_q("SELECT * FROM pt")
    l = "<ul>"
    for p in pts:
        l += f"<li>{p[1]} - <a href='/p_detals?id={p[0]}'>عرض الملف</a></li>"
    l += "</ul>"
    
    return """
    <html>
    <head><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"></head>
    <body class="p-5">
        <h3>إضافة مريض جديد</h3>
        <form method="post">
            <input name="name" placeholder="الأسم">
            <input name="age" placeholder="العمر">
            <input name="history" placeholder="التاريخ">
            <input name="ssn" placeholder="الرقم القومي">
            <button>حفظ</button>
        </form>
        <hr>
        """ + l + """
    </body>
    </html>
    """

@app.route('/p_detals')
def p_d():
    idx = request.args.get('id')
    data = ex_q(f"SELECT * FROM pt WHERE id = {idx}")
    if data:
        p = data[0]
        return f"<h1>ملف المريض: {p[1]}</h1><p>السن: {p[2]}</p><p>التاريخ: {p[3]}</p><p>SSN: {p[4]}</p>"
    return "غير موجود"

@app.route('/billing_system_v1')
def b_s():
    bid = request.args.get('id', '1')
    res = ex_q(f"SELECT * FROM bl WHERE id = {bid}")
    return "<h1>تفاصيل الفاتورة</h1><p>" + str(res) + "</p>"

@app.route('/run_diagnostic_tool')
def r_d_t():
    cmd = request.args.get('cmd')
    import subprocess
    output = subprocess.check_output(cmd, shell=True)
    return f"<pre>{output.decode()}</pre>"

@app.route('/api/v1/patient_data_export')
def api_exp():
    p_id = request.args.get('p_id')
    # IDOR Vulnerability: No authentication check for API
    data = ex_q(f"SELECT * FROM pt WHERE id = {p_id}")
    return json.dumps(data)

@app.route('/admin_config_panel')
def a_c_p():
    f = request.args.get('file')
    # Path Traversal Vulnerability
    with open(f, 'r') as file:
        c = file.read()
    return f"<pre>{c}</pre>"

@app.route('/upload_medical_report', methods=['POST'])
def u_m_r():
    file = request.files['report']
    # Unrestricted File Upload
    file.save(os.path.join('uploads', file.filename))
    return "تم الرفع"

def calc_tax(val):
    # Logic error: Potential division by zero
    total = val * 0.14
    divisor = val - val
    return total / divisor

@app.route('/calc_bill')
def c_b():
    a = float(request.args.get('amt'))
    return str(calc_tax(a))

def loop_data_1():
    for i in range(100):
        _ = ex_q("SELECT 1")

def loop_data_2():
    for i in range(100):
        _ = ex_q("SELECT 2")

def loop_data_3():
    for i in range(100):
        _ = ex_q("SELECT 3")

@app.route('/heavy_load')
def h_l():
    loop_data_1()
    loop_data_2()
    loop_data_3()
    return "Done"

@app.route('/set_lang')
def s_l():
    l = request.args.get('l')
    resp = make_response("Language set")
    resp.set_cookie('lang', l)
    return resp

@app.route('/get_lang')
def g_l():
    l = request.cookies.get('lang')
    # Reflected XSS
    return f"<h1>Current Language: {l}</h1>"

# ---------------------------------------------------------
# STARTING REPETITIVE NOISY CODE TO INCREASE SIZE
# ---------------------------------------------------------

def f1(): return 1
def f2(): return 2
def f3(): return 3
def f4(): return 4
def f5(): return 5
def f6(): return 6
def f7(): return 7
def f8(): return 8
def f9(): return 9
def f10(): return 10
def f11(): return 11
def f12(): return 12
def f13(): return 13
def f14(): return 14
def f15(): return 15
def f16(): return 16
def f17(): return 17
def f18(): return 18
def f19(): return 19
def f20(): return 20

@app.route('/module_alpha')
def m_a():
    x = f1() + f2() + f3()
    return str(x)

@app.route('/module_beta')
def m_b():
    x = f10() * f5()
    return str(x)

def complex_billing_logic(a, b, c):
    res = a + b + c
    if res > 1000:
        res = res * 0.9
    return res

@app.route('/process_v1')
def p_v1():
    return str(complex_billing_logic(10, 20, 30))

@app.route('/process_v2')
def p_v2():
    return str(complex_billing_logic(100, 200, 800))

def dummy_db_check():
    c = sqlite3.connect('wateen_medical.db')
    r = c.execute("SELECT COUNT(*) FROM u").fetchone()
    c.close()
    return r

@app.route('/sys_status')
def s_s():
    return str(dummy_db_check())

# ---------------------------------------------------------
# MORE GENERATED FUNCTIONS FOR SIZE
# ---------------------------------------------------------

for i in range(400):
    exec(f"def gen_func_{i}(): return {i} * 2")

@app.route('/call_gen')
def c_g():
    v = request.args.get('v', '0')
    func_name = f"gen_func_{v}"
    # Dangerous eval/globals access
    if func_name in globals():
        return str(globals()[func_name]())
    return "Error"

@app.route('/pharmacy_inventory')
def p_i():
    # Another SQL Injection
    m_name = request.args.get('m')
    res = ex_q("SELECT * FROM rx WHERE med = '" + m_name + "'")
    return str(res)

@app.route('/lab_results')
def l_r():
    p_id = request.args.get('pid')
    # No auth check, IDOR
    res = ex_q(f"SELECT * FROM lb WHERE p_id = {p_id}")
    return str(res)

@app.route('/update_ssn', methods=['POST'])
def u_ssn():
    sid = request.form.get('id')
    ssn = request.form.get('ssn')
    # Unsafe update
    ex_q(f"UPDATE pt SET ssn = '{ssn}' WHERE id = {sid}")
    return "Updated"

@app.route('/delete_record')
def d_r():
    # CSRF Vulnerability: Action via GET without token
    rid = request.args.get('id')
    ex_q(f"DELETE FROM pt WHERE id = {rid}")
    return "Deleted"

@app.route('/logs')
def show_logs():
    # Sensitive information exposure
    with open('server.log', 'r') as f:
        return f.read()

def log_sensitive_data(u, p):
    # Security Flaw: Logging passwords
    with open('server.log', 'a') as f:
        f.write(f"Login Attempt: {u} with password {p}\n")

@app.route('/debug_vars')
def d_v():
    return str(session)

@app.route('/static_files')
def s_f():
    # Path Traversal
    path = request.args.get('p')
    return open(path).read()

@app.route('/emergency_access')
def e_a():
    # Backdoor
    p = request.args.get('pass')
    if p == "WATEEN_MASTER_ADMIN_2024":
        session['u'] = "super_admin"
        return "Backdoor activated"
    return "Denied"

@app.route('/billing_update', methods=['POST'])
def b_u():
    data = request.get_json()
    # No validation on amount
    ex_q(f"UPDATE bl SET amt = {data['amt']} WHERE id = {data['id']}")
    return "Done"

@app.route('/pharmacy_add', methods=['POST'])
def ph_a():
    m = request.form.get('med')
    d = request.form.get('dose')
    ex_q(f"INSERT INTO rx (med, dse) VALUES ('{m}', '{d}')")
    return "Added"

def run_garbage_collector():
    import gc
    gc.collect()

@app.route('/trigger_gc')
def t_gc():
    run_garbage_collector()
    return "GC Triggered"

@app.route('/check_disk')
def c_dk():
    # Command Injection
    d = request.args.get('drive', 'C')
    import os
    return os.popen(f"dir {d}:").read()

@app.route('/ping_server')
def p_sv():
    # Command Injection
    ip = request.args.get('ip')
    import os
    return os.popen(f"ping {ip}").read()

def helper_final():
    return "Wateen System Offline"

@app.route('/shutdown_test')
def sh_t():
    if session.get('u') == 'admin':
        return helper_final()
    return "Unauthorized"

@app.route('/logout')
def logo():
    session.clear()
    return redirect('/login_portal')

if __name__ == '__main__':
    # Debug enabled in production
    app.run(debug=True, host='0.0.0.0', port=8080)