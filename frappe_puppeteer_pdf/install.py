import frappe
import click
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe_puppeteer_pdf.custom_fields import CUSTOM_FIELDS

def check_frappe_version():
    """التحقق من إصدار Frappe لضمان التوافق"""
    def major_version(v: str) -> str:
        return v.split(".")[0]

    frappe_version = major_version(frappe.__version__)
    if int(frappe_version) >= 15:
        return

    click.secho(
        f"You're attempting to install Puppeteer PDF Generator with Frappe version {frappe_version}. "
        "This is not supported. Please use Version 15 or above.",
        fg="red",
    )
    raise SystemExit(1)

def before_install():
    check_frappe_version()

def after_install():
    """الإجراءات المطلوبة بعد التثبيت في البيئة المركزية"""
    # 1. إنشاء الحقول المخصصة (مثل اختيار المحرك في Print Format)
    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
    
    # 2. إضافة خيار 'chrome' لمحرك الطباعة
    add_pdf_generator_option()
    
    click.secho("✅ Puppeteer PDF Generator (Centralized Mode) installed successfully.", fg="green")

def add_pdf_generator_option():
    """إضافة خيار 'chrome' إلى قائمة محركات PDF في نظام Frappe"""
    field = frappe.get_meta("Print Format").get_field("pdf_generator")

    if not field:
        return

    options = (field.options).split("\n")
    generator_name = "chrome" # تأكد أن هذا الاسم يطابق المنطق في pdf_generator.py

    if generator_name not in options:
        options.append(generator_name)
        
        make_property_setter(
            "Print Format",
            "pdf_generator",
            "options",
            "\n".join(options),
            "Text",
            validate_fields_for_doctype=False,
        )
        click.echo(f"Added '{generator_name}' to PDF Generator options.")

# تم إزالة كافة الدوال المتعلقة بتحميل Chromium محلياً (download_chromium, setup_chromium, etc.)
# لأن المتصفح الآن يعمل داخل حاوية Browserless المستقلة.
