from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class DashboardSideMenuPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page.set_default_timeout(30000)
        
        # Menu elements
        self.elements.expand_side_menu_in_mobile_layout = ".vn-side-menu__toggle"
        self.elements.instant_ink_menu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-HP Instant Ink']"
        self.elements.overview_menu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-Overview']"
        self.elements.update_plan_menu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-Update Plan']"
        self.elements.print_history_menu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-Print and Payment History']"
        self.elements.shipment_tracking_menu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-Shipment Tracking']"
        self.elements.my_account_menu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-Account']"
        self.elements.shipping_billing_submenu_link = "[data-testid='jarvis-react-consumer-layout__side-menu-item-Shipping & Billing']"
        self.elements.notifications_submenu_link = '[data-testid="jarvis-react-consumer-layout__side-menu-item-Notifications"]'
        self.elements.printers_menu_link = '[data-testid="jarvis-react-consumer-layout__side-menu-item-Printers"]'

    def _click_with_parent_expansion(self, target_element, parent_element):
        try:
            target_element.click()
        except:
            parent_element.click()
            target_element.click()

    def _click_with_instant_ink_expansion(self, target_element):
        try:
            target_element.click(timeout=2000)
            return
        except:
            pass

        try:
            if self.expand_side_menu_in_mobile_layout.is_visible():
                self.expand_side_menu_in_mobile_layout.click(timeout=30000)
                target_element.wait_for(state="visible", timeout=30000)
        except:
            pass

        self._click_with_parent_expansion(target_element, self.instant_ink_menu_link)

    def _click_with_account_expansion(self, target_element):
        self._click_with_parent_expansion(target_element, self.my_account_menu_link)

    def click_overview(self):
        self._click_with_instant_ink_expansion(self.overview_menu_link)

    def click_update_plan(self):
        self._click_with_instant_ink_expansion(self.update_plan_menu_link)

    def click_print_history(self):
        self._click_with_instant_ink_expansion(self.print_history_menu_link)

    def click_shipment_tracking(self):
        self._click_with_instant_ink_expansion(self.shipment_tracking_menu_link)

    def click_shipping_billing(self):
        self._click_with_account_expansion(self.shipping_billing_submenu_link)

    def click_notifications(self):
        self._click_with_account_expansion(self.notifications_submenu_link)

    def expand_instant_ink_menu(self):
        if not self.overview_menu_link.is_visible():
            try:
                if self.expand_side_menu_in_mobile_layout.is_visible():
                    self.expand_side_menu_in_mobile_layout.click(timeout=30000)
            except:
                pass
            self.instant_ink_menu_link.click()

    def expand_my_account_menu(self):
        if not self.shipping_billing_submenu_link.is_visible():
            self.my_account_menu_link.click()

    def visible_instant_ink_menu_link(self):
        return self.page.wait_for_selector(self.elements.instant_ink_menu_link, state="visible", timeout=120000)
