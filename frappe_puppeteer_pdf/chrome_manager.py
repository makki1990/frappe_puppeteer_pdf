import frappe

class ChromeManager:
    """إدارة الاتصال بحاوية الكروم المركزية للطباعة"""

    def __init__(self):
        # القيمة الافتراضية هي اسم حاوية browserless في دوكر
        self.remote_url = frappe.conf.get("browserless_url") or "http://browserless:3000"
        self.port = 3000

    def start(self):
        """لا نحتاج لتشغيل عملية، الحاوية تعمل بشكل مستقل في دوكر"""
        frappe.logger().info(f"Connecting to Centralized Chrome at {self.remote_url}")
        return

    def get_connection_url(self):
        """إرجاع الرابط الذي سيستخدمه Playwright للاتصال"""
        return self.remote_url

    def is_running(self):
        """نفترض دائماً أن الحاوية المركزية تعمل (يديرها Docker)"""
        return True

    def stop(self):
        """لا نقوم بإيقاف الحاوية المركزية من هنا"""
        pass

    def get_chrome_path(self):
        """لا نحتاج لمسار ملف تنفيذي عند الربط عن بعد"""
        return None

# Singleton instance
_chrome_manager = None

def get_chrome_manager():
    global _chrome_manager
    if _chrome_manager is None:
        _chrome_manager = ChromeManager()
    return _chrome_manager

def ensure_chrome_running():
    manager = get_chrome_manager()
    manager.start()
    return manager

def stop_chrome():
    # في حالة الحاوية المركزية، لا نحتاج لفعل شيء هنا
    pass
