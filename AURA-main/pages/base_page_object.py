from playwright.sync_api import Page

class ElementLocators:
    pass

class WaitProxy:
    def __init__(self, page: Page, elements):
        self.page = page
        self.elements = elements
    
    def __getattr__(self, name):
        if hasattr(self.elements, name):
            selector = getattr(self.elements, name)
            return lambda **kwargs: self.page.wait_for_selector(selector, **kwargs)
        raise AttributeError(f"No selector '{name}' found for wait operation")

class BasePageObject:
    def __init__(self, page: Page):
        self.page = page
        self.elements = ElementLocators()
        self.wait = WaitProxy(page, self.elements)

    def __getattr__(self, name):
        if hasattr(self.elements, name):
            locator_str = getattr(self.elements, name)
            return self.page.locator(locator_str)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def get_selector(self, name):
        if hasattr(self.elements, name):
            return getattr(self.elements, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no selector '{name}'")