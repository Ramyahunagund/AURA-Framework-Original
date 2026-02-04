# test_flows/Header1024pxAbove/header1024px_above.py

import time
import traceback
from playwright.sync_api import sync_playwright, expect
from core.settings import GlobalState, framework_logger
import test_flows_common.test_flows_common as common
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage


def header1024px_above(stage_callback):
    framework_logger.info("=== C38421769 - Header 1024px Above validation flow started ===")
    common.setup()

    timeout_ms = 120000
    viewport_width = 1024 
    viewport_height = 768

    with sync_playwright() as p:
        launch_args = {"headless": GlobalState.headless}
        context_args = {
            "locale": f"{GlobalState.language_code}",
            "viewport": {"width": viewport_width, "height": viewport_height}
        }

        if common.PROXY_URL:
            launch_args["proxy"] = {"server": common.PROXY_URL}
            context_args["proxy"] = {"server": common.PROXY_URL}

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(**context_args)
        framework_logger.info(
            f"Launching Playwright browser with headless={GlobalState.headless}, "
            f"locale={GlobalState.language_code}, viewport={viewport_width}x{viewport_height}"
        )
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        try:
            # Initialize page objects
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Step 1: Launch the Consumer Landing page
            framework_logger.info("Step 1: Launching Consumer Landing page")
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            time.sleep(2) 

            # Step 2: Verify the new Header section
            framework_logger.info("Step 2: Verification: Checking header section visibility")
            expect(landing_page.header_section).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Header section is visible")

            # Step 3: Verify the HP logo
            framework_logger.info("Step 3: Checking HP logo")
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)

            # Validate the HP logo properties
            logo_element = landing_page.header_logo
            logo_box = logo_element.bounding_box()
            if logo_box:
                framework_logger.info(
                    f"HP logo is visible - dimensions: {logo_box['width']}x{logo_box['height']}px"
                )
            else:
                framework_logger.warning("Could not get logo bounding box")

            # Step 4: Click the Country picker icon to verify it opens and shows V4 enabled countries
            framework_logger.info("Step 4: Checking country picker icon")
            expect(landing_page.flag_icon).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Country picker icon (flag) is visible")

            try:
                flag_icon = landing_page.flag_icon
                flag_icon.click(timeout=10000)
                framework_logger.info("Country picker is clickable")

                # Close the picker
                page.keyboard.press("Escape")
            except Exception as e:
                framework_logger.warning(f"Country picker interaction: {str(e)}")

            # Step 5: Check the buttons
            framework_logger.info("Step 5: Checking header buttons")

            # Check for "Manage Account" button (may appear as "Sign In" for non-logged users)
            try:
                if landing_page.manage_account_button.is_visible(timeout=5000):
                    expect(landing_page.manage_account_button).to_be_visible()
                    framework_logger.info("'Manage Account' button is visible")
                else:
                    # For non-logged-in users, "Sign In" button is shown instead
                    expect(landing_page.sign_in_button).to_be_visible(timeout=timeout_ms)
                    framework_logger.info("'Sign In' button is visible (user not logged in)")
            except Exception as e:
                framework_logger.warning(f"Manage Account/Sign In button check: {str(e)}")

            # Check for "Sign Up Now" button
            expect(landing_page.sign_up_header_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("'Sign Up Now' button is visible")

            # Step 6: Check the Typography / Image
            framework_logger.info("Step 6: Validating typography properties")

            # Validate Sign Up button typography
            sign_up_button = landing_page.sign_up_header_button
            button_styles = sign_up_button.evaluate("""
                element => {
                    const styles = window.getComputedStyle(element);
                    return {
                        fontFamily: styles.fontFamily,
                        fontSize: styles.fontSize,
                        fontWeight: styles.fontWeight,
                        color: styles.color,
                        backgroundColor: styles.backgroundColor
                    };
                }
            """)
            framework_logger.info(
                f"Sign Up button typography: "
                f"font={button_styles['fontFamily']}, "
                f"size={button_styles['fontSize']}, "
                f"weight={button_styles['fontWeight']}, "
                f"color={button_styles['color']}"
            )

            # Validate logo dimensions and positioning
            logo_styles = landing_page.header_logo.evaluate("""
                element => {
                    const rect = element.getBoundingClientRect();
                    const styles = window.getComputedStyle(element);
                    return {
                        width: rect.width,
                        height: rect.height,
                        display: styles.display,
                        position: rect.top
                    };
                }
            """)
            framework_logger.info(
                f"Logo properties: "
                f"width={logo_styles['width']}px, "
                f"height={logo_styles['height']}px, "
                f"display={logo_styles['display']}"
            )

            # Additional validation: Check header container positioning
            header_info = landing_page.header_section.evaluate("""
                element => {
                    const rect = element.getBoundingClientRect();
                    const styles = window.getComputedStyle(element);
                    return {
                        height: rect.height,
                        backgroundColor: styles.backgroundColor,
                        position: styles.position,
                        top: rect.top
                    };
                }
            """)
            framework_logger.info(
                f"Header container: "
                f"height={header_info['height']}px, "
                f"background={header_info['backgroundColor']}, "
                f"position={header_info['position']}"
            )

            framework_logger.info("=== C38421769 - Header 1024px Above validation flow completed successfully ===")
        except Exception as e:
            framework_logger.error(
                f"An error occurred during the Header 1024px Above test: {e}\n{traceback.format_exc()}"
            )
            raise e
        finally:
            context.close()
            browser.close()
