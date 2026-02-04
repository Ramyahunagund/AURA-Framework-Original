# from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
# from helper.cancellation_plan_helper import CancellationPlanHelper
# from helper.gemini_ra_helper import GeminiRAHelper
# from helper.dashboard_helper import DashboardHelper
# from core.playwright_manager import PlaywrightManager
# from pages.overview_page import OverviewPage
# from core.settings import framework_logger
# from playwright.sync_api import expect
# import urllib3
# import traceback
# import re
#
# from test_flows.LandingPage.landing_page import landing_page
#
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# from pages.cancellation_page import CancellationPage
#
# def cancellation_summary_page_icon_validation(stage_callback):
#     framework_logger.info("=== C40797061 - Cancellation Summary Page + icon validation flow started ===")
#     tenant_email = create_ii_subscription(stage_callback)
#
#     with PlaywrightManager() as page:
#         overview_page = OverviewPage(page)
#         cancellation_page = CancellationPage(page)
#
#         try:
#             #Move subscription to subscribed state
#             GeminiRAHelper.access(page)
#             GeminiRAHelper.access_tenant_page(page, tenant_email)
#             GeminiRAHelper.access_subscription_by_tenant(page)
#             GeminiRAHelper.subscription_to_subscribed(page)
#             framework_logger.info(f"Subscription moved to subscribed state")
#
#             # Access Dashboard
#             DashboardHelper.first_access(page, tenant_email)
#             framework_logger.info(f"Opened Instant Ink Dashboard")
#
#             # Click on Cancel Instant Ink on Overview page
#             overview_page.cancel_instant_ink.click()
#             framework_logger.info("Clicked on Cancel Instant Ink on Overview page")
#
#             # Verify bottom section's title on Cancellation Summary Page
#             expect(cancellation_page.bottom_section_title).to_be_visible()
#             framework_logger.info("Verified bottom section's title on Cancellation Summary Page")
#
#             stage_callback("context_name", page, screenshot_only=True)



            # # Verify Have your printing needs changed? section on Cancellation Summary Page
            # CancellationPlanHelper.verify_bottom_section(page, "Have your printing needs changed?")
            # framework_logger.info("Verified 'Have your printing needs changed?' section on Cancellation Summary Page")
            #
            # # Verify Did you get a new printer? section on Cancellation Summary Page
            # CancellationPlanHelper.verify_bottom_section(page, "Did you get a new printer?")
            # framework_logger.info("Verified 'Did you get a new printer?' section on Cancellation Summary Page")
            #
            # # Verify Have questions or need help? section on Cancellation Summary Page
            # CancellationPlanHelper.verify_bottom_section(page, "Have questions or need help?")
            # framework_logger.info("Verified 'Have questions or need help?' section on Cancellation Summary Page")








        # except Exception as e:
        #     framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
        #     raise e



"""commented due to figma frequently change in summary page"""