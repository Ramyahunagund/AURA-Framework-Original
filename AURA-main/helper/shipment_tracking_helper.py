from pages.shipment_tracking_page import ShipmentTrackingPage
import test_flows_common.test_flows_common as common

class ShipmentTrackingHelper:
    @staticmethod
    def verify_cartridge_installed_message(page, cartridge):
        shipment_tracking_page = ShipmentTrackingPage(page)
        cartridges = cartridge.split(",")

        cartridge_locators = {
            "k": shipment_tracking_page.get_selector("kCartridgeItem"),
            "c": shipment_tracking_page.get_selector("cCartridgeItem"),
            "m": shipment_tracking_page.get_selector("mCartridgeItem"),
            "y": shipment_tracking_page.get_selector("yCartridgeItem"),
            "cmy": shipment_tracking_page.get_selector("cmyCartridgeItem")
        }

        for cartridge_type in cartridges:
            cartridge_type = cartridge_type.strip()
            if cartridge_type not in cartridge_locators:
                raise RuntimeError(f"Invalid cartridge type: {cartridge_type}")

            cartridge_element = page.wait_for_selector(cartridge_locators[cartridge_type], timeout=20000)
            assert cartridge_element.is_visible(), f"Cartridge {cartridge_type} is not visible."

    @staticmethod
    def verify_multiple_cartridge_types_installed_message(page, cartridge, cartridge2):
        try:
            ShipmentTrackingHelper.verify_cartridge_installed_message(page, cartridge)
        except RuntimeError:
            ShipmentTrackingHelper.verify_cartridge_installed_message(page, cartridge2)

    @staticmethod
    def cartridge_installed_message(page):
        shipment_tracking_page = ShipmentTrackingPage(page)
        
        cartridge_locators = {
            "K": shipment_tracking_page.get_selector("kCartridgeItem"),
            "C": shipment_tracking_page.get_selector("cCartridgeItem"),
            "M": shipment_tracking_page.get_selector("mCartridgeItem"),
            "Y": shipment_tracking_page.get_selector("yCartridgeItem"),
            "CMY": shipment_tracking_page.get_selector("cmyCartridgeItem")
        }

        for cartridge_type in common.printer_colors():
            cartridge_type = cartridge_type.strip()
            if cartridge_type not in cartridge_locators:
                raise RuntimeError(f"Invalid cartridge type: {cartridge_type}")

            cartridge_element = page.wait_for_selector(cartridge_locators[cartridge_type], timeout=20000)
            assert cartridge_element.is_visible(), f"Cartridge {cartridge_type} is not visible."

    @staticmethod
    def click_view_entire_history(page):
        shipment_tracking_page = ShipmentTrackingPage(page)
        shipment_tracking_page.shipment_history_table.wait_for(state="visible", timeout=30000)
        shipment_tracking_page.shipment_history_table.click()

    @staticmethod
    def verify_shipment_tracking_table(page):
        shipment_tracking_page = ShipmentTrackingPage(page)
        shipment_tracking_page.shipment_history_table.wait_for(state="visible", timeout=30000)
        shipment_tracking_page.shipment_history_table.click()

        colors = common.printer_colors()

        page.wait_for_selector(shipment_tracking_page.elements.shipment_history_description, state="visible", timeout=10000)
        rk_k_cmy_text = shipment_tracking_page.shipment_history_description.first.text_content(timeout=1000)
        cartridge_numbers = common.extract_numbers_from_text(rk_k_cmy_text)
        assert len(colors) == len(cartridge_numbers), f"Expected {len(colors)} cartridge numbers, found {len(cartridge_numbers)}"
        assert cartridge_numbers[0] == '1', f"Expected 1 cartridge, found {cartridge_numbers[0]}"
        assert cartridge_numbers[1] == '1', f"Expected 1 cartridge, found {cartridge_numbers[1]}"
        if len(colors) == 4:
            assert cartridge_numbers[2] == '1', f"Expected 1 cartridge, found {cartridge_numbers[2]}"
            assert cartridge_numbers[3] == '1', f"Expected 1 cartridge, found {cartridge_numbers[3]}"

        wk_text = shipment_tracking_page.shipment_history_description.last.text_content(timeout=1000)
        wk_numbers = common.extract_numbers_from_text(wk_text)
        assert len(wk_numbers) == 1, f"Expected 1 Welcome Kit number, found {len(wk_numbers)}"
        assert wk_numbers[0] == '1', f"Expected 1 Welcome Kit, found {wk_numbers[0]}"
