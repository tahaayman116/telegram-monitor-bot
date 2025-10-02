#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعداد بوت مراقبة المجموعات
"""

import json
import os

def setup_config():
    """إعداد ملف التكوين"""
    print("🔧 إعداد بوت مراقبة المجموعات")
    print("=" * 50)
    
    print("\n📋 للحصول على API ID و API Hash:")
    print("1. اذهب إلى https://my.telegram.org")
    print("2. سجل دخولك برقم هاتفك")
    print("3. اذهب إلى 'API Development Tools'")
    print("4. أنشئ تطبيق جديد")
    print("5. انسخ API ID و API Hash")
    
    print("\n" + "-" * 50)
    
    # جمع البيانات من المستخدم
    api_id = input("📱 ادخل API ID: ").strip()
    api_hash = input("🔑 ادخل API Hash: ").strip()
    phone = input("📞 ادخل رقم الهاتف (مع رمز البلد): ").strip()
    
    # التحقق من صحة البيانات
    if not api_id or not api_hash or not phone:
        print("❌ يجب ملء جميع الحقول!")
        return False
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ API ID يجب أن يكون رقم!")
        return False
    
    # إنشاء ملف التكوين
    config = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone
    }
    
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ تم إنشاء ملف config.json بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف التكوين: {e}")
        return False

def install_requirements():
    """تثبيت المتطلبات"""
    print("\n📦 تثبيت المتطلبات...")
    
    try:
        import subprocess
        import sys
        
        # تثبيت المتطلبات
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت المتطلبات بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        print("💡 قم بتشغيل الأمر التالي يدوياً:")
        print("pip install -r requirements.txt")
        return False

def main():
    """الدالة الرئيسية"""
    print("🤖 مرحباً بك في إعداد بوت مراقبة المجموعات!")
    
    # التحقق من وجود ملف التكوين
    if os.path.exists('config.json'):
        choice = input("\n⚠️ ملف config.json موجود. هل تريد إعادة إنشاؤه؟ (y/n): ")
        if choice.lower() != 'y':
            print("تم إلغاء العملية.")
            return
    
    # إعداد التكوين
    if not setup_config():
        return
    
    # تثبيت المتطلبات
    install_requirements()
    
    print("\n" + "=" * 50)
    print("🎉 تم الإعداد بنجاح!")
    print("=" * 50)
    print("🚀 لتشغيل البوت:")
    print("python main.py")
    print("\n📝 ملاحظات مهمة:")
    print("• البوت سيطلب منك تسجيل الدخول في المرة الأولى")
    print("• سيتم إنشاء ملف session_name.session للحفاظ على الجلسة")
    print("• الرسائل المحفوظة ستكون في ملف saved_messages.json")
    print("• يمكنك تعديل الكلمات المفتاحية من داخل البوت")

if __name__ == "__main__":
    main()
