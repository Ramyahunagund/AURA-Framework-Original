from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class CancellationTimelinePage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.close_button = "[data-testid='close-timeline-modal']"
        self.elements.timeline_modal = "[data-testid='cancellation-timeline-modal']"
        self.elements.stepper = "[class^='timelineStepperItem__step-item-info-title_']"
        self.elements.header_icon = '[class^="optimizedCancelPlanBanner__cancel-plan-banner-icon-container___1rKfT"]'
        self.elements.header_title = '[class^="optimizedCancellationInterventionPage__header-title___3lIm-"]'
        self.elements.header_subtitle = '[class^="optimizedCancelPlanBanner__cancel-plan-banner-goodbye-message___1hrh2"]'
        self.elements.restore_subscription = '[data-testid="restore-your-subscription"],[data-testid="restore_subscription"]'
        self.elements.timeline_img = '[data-testid="timeline-header-img"],[class="tradePriceCard__image-content___1HPxH"]'
        self.elements.whats_happens_next = '[data-testid="timeline-header-info"],[class="cancellationSuccessTimeline__text-title___2nx-T"]'
        self.elements.cancellation_step = '[class^="timelineStepperItem__step-item-info-container"],[class="timelineStepper__timeline-step-container___taxeh"]'
        self.elements.cancellation_step_title = '[class^="timelineStepperItem__step-item-info-title"],[data-testid="undefined-title"]'
        self.elements.first_step_icon = 'div[class*="timelineStepperItem__complete-step"],div[class*="timelineStepper__complete-step"]'
        self.elements.second_step_icon = 'div[class*="timelineStepperItem__current-step"],div[class*="timelineStepper__current-step"]'
        self.elements.third_step_icon = '[class^="timelineStepperItem__checkmark-container"],[class*="timelineStepper__checkmark-line-container"]'
        self.elements.fourth_step_icon = '[class^="timelineStepperItem__checkmark-container"],[class*="timelineStepper__checkmark-line-container"]'
        self.elements.fifth_step_icon = '[class*="timelineStepper__checkmark-line-container"]'
        # self.elements.header_icon = '[class^="cancellationTimelineContent__timeline-content-header-icon"]'
        # self.elements.header_title = '[class^="cancellationTimelineContent__timeline-content-header-title"]'
        # self.elements.header_subtitle = '[class^="cancellationTimelineContent__timeline-content-header-subline"]'
        # self.elements.restore_subscription = '[data-testid="restore_subscription"],[data-testid="restore-your-subscription"]'
        # self.elements.timeline_img = '[data-testid="timeline-header-img"]'
        self.elements.whats_happens_next = '[class^="cancellationSuccessTimeline__text-title___2nx-T"],[data-testid="timeline-header-info"]'
        self.elements.cancellation_step = '[class^="timelineStepperItem__step-item-info-container"], [class^="timelineStepper__timeline-step-content"]'
        self.elements.cancellation_step_title = '[class^="timelineStepperItem__step-item-info-title"], [class^="timelineStepper__timeline-step-title"]'
        # self.elements.first_step_icon = 'div[class*="timelineStepperItem__complete-step"]'
        # self.elements.second_step_icon = 'div[class*="timelineStepperItem__current-step"]'
        # self.elements.third_step_icon = '[class^="timelineStepperItem__checkmark-container"]'
        # self.elements.fourth_step_icon = '[class^="timelineStepperItem__checkmark-container"]'
        self.elements.change_your_mind = '[data-testid="cancellation-retention-title"],[class="optimizedCancelPlanBanner__cancel-plan-banner-restore-message___2O6Wu"]'
        self.elements.keep_subscription_as_it_was = '[data-testid="cancellation-alternative-keep-subscription-as-it-was"]'
        self.elements.transfer_subscription_link = '[data-testid="transfer-subscription-to-another-printer"],[data-testid="cancellation-alternative-transfer-subscription-to-another-printer"]'
        self.elements.shop_hp_button = '[data-testid="purchase-ink-at-hp-store"]'
        self.elements.preview_upcoming_button = '[data-testid="preview-upcoming-bill"]'
        self.elements.request_recycling_button = '[data-testid="request-recycling-materials"]'
        self.elements.cancellation_timeline_close_button = '[data-testid="close-timeline-modal"]'
        self.elements.back_to_cancel_confirmation = '[data-testid="back-to-cancel-confirmation"]'
        self.elements.resume_instant_ink_subscription = '[data-testid="resume-instant-ink-subscription"],[data-testid="confirm-subscription-resume"]'
        self.elements.see_cancellation_timeline = '[data-testid="see-cancellation-timeline"]'

    def timeline_stepper_header(self, index: int) -> str:
        self.page.wait_for_selector(self.elements.stepper, timeout=60000)
        return self.page.locator(self.elements.stepper).nth(index)

    def cancellation_step(self, index, timeout=5000):
        self.page.wait_for_selector(self.elements.cancellation_step, timeout=timeout)
        steps = self.page.locator(self.elements.cancellation_step)
        count = steps.count()
        if index >= count:
            raise IndexError(f"Cancellation step index {index} out of range (found {count} steps)")
        step = steps.nth(index)
        step.wait_for(state="visible", timeout=timeout)
        return step
    
    def cancellation_step_title(self, index):
        return self.page.locator(self.elements.cancellation_step_title).nth(index)
    
    def third_step_icon(self, index):
        return self.page.locator(self.elements.third_step_icon).nth(index)
    
    def fourth_step_icon(self, index):
        return self.page.locator(self.elements.fourth_step_icon).nth(index)

    def fifth_step_icon(self, index):
        return self.page.locator(self.elements.fifth_step_icon).nth(index)
    