import asyncio
import logging
import os
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerUser
import json
from datetime import datetime
import time

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class RailwayTelegramBot:
    def __init__(self):
        # بيانات API من متغيرات البيئة
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.phone = os.getenv('PHONE', '')
        
        # الكلمات المفتاحية للبحث
        self.keywords = [
            'يسوي', 'يحل', 'يساعدني', 'يساعد', 'يعمل', 'يقدر',
            'ابحث عن', 'محتاج', 'عايز', 'اريد', 'ممكن حد',
            'حد يقدر', 'مين يعرف', 'عندكم', 'تعرفون حد'
        ]
        
        # قائمة الرسائل المحفوظة (في الذاكرة فقط للخدمات المجانية)
        self.saved_messages = []
        
        # إعدادات الأداء
        self.last_message_time = 0
        self.message_count = 0
        self.start_time = time.time()
        
        # العميل
        self.client = None
        
    def contains_keywords(self, text):
        """فحص النص للبحث عن الكلمات المفتاحية"""
        if not text:
            return False, []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    async def handle_new_message(self, event):
        """معالجة الرسائل الجديدة"""
        try:
            # تحديد معدل المعالجة
            current_time = time.time()
            if current_time - self.last_message_time < 1:  # ثانية واحدة بين الرسائل
                return
            
            self.last_message_time = current_time
            self.message_count += 1
            
            message = event.message
            
            # تجاهل الرسائل الخاصة
            if isinstance(event.message.peer_id, PeerUser):
                return
            
            # فحص النص للكلمات المفتاحية
            has_keywords, found_keywords = self.contains_keywords(message.text)
            
            if has_keywords:
                # الحصول على معلومات المجموعة والمرسل
                chat = await event.get_chat()
                sender = await event.get_sender()
                
                # إنشاء كائن الرسالة
                saved_message = {
                    'timestamp': datetime.now().isoformat(),
                    'chat_title': getattr(chat, 'title', 'مجموعة غير معروفة'),
                    'chat_id': chat.id,
                    'sender_name': f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip(),
                    'sender_username': getattr(sender, 'username', ''),
                    'sender_id': sender.id,
                    'message_text': message.text,
                    'keywords_found': found_keywords,
                }
                
                # إضافة للقائمة (آخر 100 رسالة فقط لتوفير الذاكرة)
                self.saved_messages.append(saved_message)
                if len(self.saved_messages) > 100:
                    self.saved_messages.pop(0)
                
                # إرسال الإشعار
                await self.send_notification_to_self(saved_message)
                
                # طباعة إشعار
                logger.info(f"🔔 رسالة جديدة من {chat.title} - الكلمات: {', '.join(found_keywords)}")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {e}")
    
    async def send_notification_to_self(self, saved_message):
        """إرسال إشعار لنفسك في تلجرام"""
        try:
            # تقصير النص إذا كان طويلاً
            message_text = saved_message['message_text']
            if len(message_text) > 200:
                message_text = message_text[:200] + "..."
            
            # تنسيق الرسالة
            notification_text = f"""🔔 **كلمة مفتاحية جديدة!**

📱 **المجموعة:** {saved_message['chat_title']}
👤 **المرسل:** {saved_message['sender_name']}
🆔 **المعرف:** @{saved_message['sender_username'] or 'غير متوفر'}
🔑 **الكلمات:** {', '.join(saved_message['keywords_found'])}
⏰ **الوقت:** {datetime.now().strftime('%H:%M')}

💬 **الرسالة:**
{message_text}

🔗 **للتواصل:** [اضغط هنا](tg://user?id={saved_message['sender_id']})
📊 **إجمالي الرسائل:** {len(self.saved_messages)}"""
            
            # إرسال الرسالة لنفسك
            await self.client.send_message('me', notification_text)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {e}")
    
    async def handle_bot_commands(self, event):
        """معالجة أوامر البوت"""
        try:
            # التأكد أن الرسالة من نفسك
            if event.sender_id != (await self.client.get_me()).id:
                return
            
            text = event.message.text.strip()
            
            if text.startswith('/stats'):
                await self.handle_stats_command(event)
            elif text.startswith('/keywords'):
                await self.handle_keywords_command(event)
            elif text.startswith('/help'):
                await self.handle_help_command(event)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الأوامر: {e}")
    
    async def handle_stats_command(self, event):
        """عرض إحصائيات البوت"""
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        stats_text = f"""📊 **إحصائيات البوت**

⏰ **وقت التشغيل:** {hours}س {minutes}د
📬 **رسائل محفوظة:** {len(self.saved_messages)}
🔄 **رسائل معالجة:** {self.message_count}
🔑 **كلمات مفتاحية:** {len(self.keywords)}
🌐 **يعمل على:** Railway (مجاني)

✅ **البوت يعمل بشكل مستمر!**"""
        
        await event.reply(stats_text)
    
    async def handle_keywords_command(self, event):
        """عرض الكلمات المفتاحية"""
        keywords_text = "🔑 **الكلمات المفتاحية:**\n\n"
        for i, keyword in enumerate(self.keywords, 1):
            keywords_text += f"{i}. {keyword}\n"
        
        keywords_text += f"\n📊 **المجموع:** {len(self.keywords)} كلمة"
        
        await event.reply(keywords_text)
    
    async def handle_help_command(self, event):
        """عرض المساعدة"""
        help_text = """🤖 **بوت مراقبة المجموعات**

**الأوامر المتاحة:**
• `/stats` - إحصائيات البوت
• `/keywords` - عرض الكلمات المفتاحية
• `/help` - هذه المساعدة

**المميزات:**
✅ يعمل 24/7 على Railway
✅ يراقب جميع المجموعات
✅ إشعارات فورية في Saved Messages
✅ مجاني تماماً

**ملاحظة:** البوت يعمل تلقائياً ولا يحتاج تدخل منك!"""
        
        await event.reply(help_text)
    
    async def start_client(self):
        """بدء العميل"""
        if not self.api_id or not self.api_hash:
            logger.error("❌ بيانات API غير مكتملة!")
            logger.error(f"API_ID موجود: {bool(self.api_id)}")
            logger.error(f"API_HASH موجود: {bool(self.api_hash)}")
            return False
        
        # استخدام الجلسة المشفرة إذا كانت متوفرة
        session_string = os.getenv('SESSION_STRING', '')
        if session_string:
            import base64
            try:
                session_data = base64.b64decode(session_string)
                with open('temp_session.session', 'wb') as f:
                    f.write(session_data)
                self.client = TelegramClient('temp_session', self.api_id, self.api_hash)
                logger.info("🔐 استخدام الجلسة المحفوظة...")
            except Exception as e:
                logger.error(f"خطأ في فك تشفير الجلسة: {e}")
                return False
        else:
            self.client = TelegramClient('railway_session', self.api_id, self.api_hash)
        
        try:
            if session_string:
                await self.client.connect()
                if await self.client.is_user_authorized():
                    logger.info("✅ تم تسجيل الدخول باستخدام الجلسة المحفوظة!")
                    return True
                else:
                    logger.error("❌ الجلسة غير صالحة!")
                    return False
            else:
                await self.client.start(phone=self.phone)
                logger.info("تم تسجيل الدخول بنجاح!")
                return True
        except Exception as e:
            logger.error(f"خطأ في تسجيل الدخول: {e}")
            return False
    
    async def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل بوت Railway...")
        
        # بدء العميل
        if not await self.start_client():
            return
        
        # إضافة معالجات الأحداث
        self.client.add_event_handler(self.handle_new_message, events.NewMessage)
        self.client.add_event_handler(self.handle_bot_commands, events.NewMessage(pattern=r'^/\w+'))
        
        logger.info("✅ البوت يعمل على Railway!")
        logger.info("📊 يراقب المجموعات ويرسل الإشعارات")
        logger.info("🌐 متاح 24/7")
        
        # إرسال رسالة بدء التشغيل
        try:
            await self.client.send_message('me', "🚀 **البوت يعمل الآن على Railway!**\n\n✅ يراقب المجموعات 24/7\n💡 أرسل /help للمساعدة")
        except:
            pass
        
        # تشغيل مستمر
        await self.client.run_until_disconnected()

# تشغيل البوت
if __name__ == "__main__":
    bot = RailwayTelegramBot()
    asyncio.run(bot.run())
