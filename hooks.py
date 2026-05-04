from . import __version__ as app_version

app_name = "frappe_puppeteer_pdf"
app_title = "Puppeteer PDF Generator"
app_publisher = "Frappe Technologies Pvt Ltd."
app_description = "Frappe App to generate PDFs using Centralized Chrome/Playwright"
app_email = "hello@frappe.io"
app_license = "AGPLv3"

# الأصول (Assets)
# ------------------

# الحفاظ على ملفات الجافا سكريبت الضرورية لواجهة الطباعة
page_js = {
    "print": "frappe_puppeteer_pdf/public/js/print.js",
}

doctype_js = {"Print Format": "frappe_puppeteer_pdf/public/js/print_format.js"}

# Jinja Methods
# ----------
jinja = {
    "methods": [
        "frappe_puppeteer_pdf.pdf_utils.render_user_text",
        "frappe_puppeteer_pdf.pdf_utils.convert_css",
        "frappe_puppeteer_pdf.pdf_utils.convert_uom",
        "frappe_puppeteer_pdf.pdf_utils.get_barcode",
    ]
}

# Installation & Uninstallation
# ------------
# ملاحظة: تأكد أن ملف install.py لا يحاول تثبيت متصفح محلياً الآن
before_install = "frappe_puppeteer_pdf.install.before_install"
after_install = "frappe_puppeteer_pdf.install.after_install"
before_uninstall = "frappe_puppeteer_pdf.uninstall.before_uninstall"

# PDF Generation Hooks
# ------------
# هذه الربطات تضمن استخدام المحرك المخصص عند طلب PDF
pdf_header_html = "frappe_puppeteer_pdf.pdf_utils.pdf_header_footer_html"
pdf_body_html = "frappe_puppeteer_pdf.pdf_utils.pdf_body_html"
pdf_footer_html = "frappe_puppeteer_pdf.pdf_utils.pdf_header_footer_html"

get_print_format_template = "frappe_puppeteer_pdf.pdf_utils.get_print_format_template"

# Request Hooks
# يتم استخدام before_request للتحقق مما إذا كان الطلب يتطلب محرك Chrome
before_request = ["frappe_puppeteer_pdf.pdf_generator.before_request"]
after_request = ["frappe_puppeteer_pdf.pdf_generator.after_request"]

# Main PDF Generator Hook
# هذا هو المفتاح الأساسي لاستبدال wkhtmltopdf بمحركك الجديد
pdf_generator = "frappe_puppeteer_pdf.pdf_generator.get_pdf"

# DocType Class Override
# ---------------
override_doctype_class = {
    "Print Format": "frappe_puppeteer_pdf.overrides.PuppeteerPrintFormat",
}

# Scheduled Tasks
# ---------------
# تم إزالة "setup_chromium" لأننا نعتمد الآن على حاوية خارجية (browserless)
# ولا نحتاج لتحميل المتصفح محلياً بشكل دوري أو عند التثبيت
scheduler_events = {}

# Overriding Methods
# ------------------------------
# إذا واجهت مشاكل في استجابة النظام، يمكنك تفعيل التجاوز المباشر للدالة هنا
override_whitelisted_methods = {
    "frappe.utils.print_format.download_pdf": "frappe_puppeteer_pdf.pdf_generator.get_pdf"
}
