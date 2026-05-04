import frappe
import re
from frappe.utils.pdf import get_pdf as frappe_get_pdf
from playwright.sync_api import sync_playwright

from .chrome_manager import ensure_chrome_running


def before_request():
    """Set pdf_generator to chrome for print designer formats"""
    if (
        frappe.request.path == "/api/method/frappe.utils.print_format.download_pdf"
        or frappe.request.path == "/printview"
    ):
        # Get the print format being requested
        print_format = frappe.request.args.get("format")
        if print_format:
            pdf_generator = frappe.get_cached_value(
                "Print Format", print_format, "pdf_generator"
            )

            # Set pdf_generator in form_dict
            if pdf_generator == "chrome":
                frappe.local.form_dict.pdf_generator = "chrome"
            else:
                frappe.local.form_dict.pdf_generator = frappe.request.args.get(
                    "pdf_generator", pdf_generator or "wkhtmltopdf"
                )

        # Initialize Connection if chrome is being used
        if frappe.local.form_dict.get("pdf_generator") == "chrome":
            try:
                ensure_chrome_running()
            except Exception as e:
                frappe.log_error(f"Failed to connect to Centralized Chrome: {e}")
                # Fallback to wkhtmltopdf
                frappe.local.form_dict.pdf_generator = "wkhtmltopdf"


def after_request():
    """Cleanup after request"""
    pass


def get_pdf(print_format, html, options=None, output=None, pdf_generator=None):
    """Main PDF generation function called by Frappe"""
    if pdf_generator != "chrome":
        return None

    try:
        frappe.logger().info(
            f"Generating PDF with Centralized Chrome for format: {print_format}"
        )

        if not options:
            options = {}
        if print_format:
            orientation = frappe.get_cached_value("Print Format", print_format, "pdf_page_orientation")
            if orientation:
                options["orientation"] = orientation

        # Get chrome manager instance
        chrome_manager = ensure_chrome_running()

        # Generate PDF using Playwright
        pdf_data = generate_with_playwright(html, options, chrome_manager)

        if output:
            with open(output, "wb") as f:
                f.write(pdf_data)
            return output

        return pdf_data

    except Exception as e:
        frappe.log_error(f"Chrome PDF generation failed for {print_format}: {e}")
        return fallback_to_wkhtmltopdf(html, options, output)


def generate_with_playwright(html, options, chrome_manager):
    """Generate PDF using Playwright connected to Centralized Chrome"""
    # Clean HTML from UI elements
    html = re.sub(r'<div class="action-banner print-hide">.*?</div>', '', html, flags=re.DOTALL)

    with sync_playwright() as p:
        try:
            # Connect to Remote Chrome using CDP
            # Note: browserless expects ws:// link for CDP connection
            connection_url = chrome_manager.get_connection_url()
            
            # Ensure the URL is formatted for WebSocket if it's a direct browserless call
            if connection_url.startswith('http'):
                connection_url = connection_url.replace('http', 'ws', 1)

            browser = p.chromium.connect_over_cdp(connection_url)

            # Isolated Context for multi-tenant safety
            context = browser.new_context()
            page = context.new_page()

            # Set content and wait for network to be idle (important for external assets/letterheads)
            page.set_content(html, wait_until="networkidle")

            page.emulate_media(media="print")

            # Map options
            pdf_options = map_frappe_to_playwright(options)

            # Generate
            pdf_data = page.pdf(**pdf_options)

            # Strict Cleanup to avoid memory leaks in the centralized container
            page.close()
            context.close()
            browser.close()

            return pdf_data

        except Exception as e:
            frappe.log_error(f"Playwright Remote Connection Error: {e}")
            raise


def map_frappe_to_playwright(options):
    """Map Frappe PDF options to Playwright PDF options"""
    if not options:
        options = {}

    playwright_options = {
        "format": options.get("page_size", "A4"),
        "print_background": True,
        "scale": 1,
        "display_header_footer": False,
        "landscape": options.get("orientation", "Portrait") == "Landscape",
        "page_ranges": options.get("page_ranges", ""),
        "margin": {
            "top": f"{options.get('margin_top', 0)}mm",
            "right": f"{options.get('margin_right', 0)}mm",
            "bottom": f"{options.get('margin_bottom', 0)}mm",
            "left": f"{options.get('margin_left', 0)}mm",
        },
        "prefer_css_page_size": False,
    }

    if options.get("page_size") == "Custom":
        playwright_options["width"] = f"{options.get('page_width', 210)}mm"
        playwright_options["height"] = f"{options.get('page_height', 297)}mm"
        playwright_options.pop("format", None)

    return {k: v for k, v in playwright_options.items() if v is not None}


def fallback_to_wkhtmltopdf(html, options, output):
    """Fallback to Frappe's wkhtmltopdf generator"""
    frappe.logger().warning("Falling back to wkhtmltopdf")
    try:
        return frappe_get_pdf(html, options, output)
    except Exception as e:
        frappe.log_error(f"Total PDF failure: {e}")
        raise
