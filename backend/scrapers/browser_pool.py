import asyncio
import logging
from typing import Optional, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BrowserPool:
    """
    Singleton browser pool for sharing Playwright instances across scrapers.
    Reduces memory usage and eliminates browser startup overhead.
    """
    _instance: Optional['BrowserPool'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.ua = UserAgent()
        self._semaphore = asyncio.Semaphore(8)  # Increased from 3 to 8 for higher concurrency
        self._active_contexts = 0
        
    async def initialize(self):
        """Initialize the browser pool if not already initialized."""
        async with self._lock:
            if self.browser is not None:
                return
                
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--window-size=1920x1080',
                        '--disable-blink-features=AutomationControlled', # Critical for stealth
                    ]
                )
                logger.info("Browser pool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize browser pool: {e}")
                raise
    
    async def get_page(self) -> Tuple[Page, BrowserContext]:
        """
        Get a new page with a fresh browser context.
        Uses semaphore to limit concurrent contexts.
        
        Returns:
            Tuple of (Page, BrowserContext) - caller must close both when done
        """
        await self.initialize()
        
        async with self._semaphore:
            try:
                # Create new context with stealth settings
                context = await self.browser.new_context(
                    user_agent=self.ua.random,
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='Asia/Kolkata',
                    permissions=['geolocation'],
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"macOS"',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                    }
                )
                
                # Create new page
                page = await context.new_page()
                
                # Add stealth scripts to avoid detection
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    window.chrome = {
                        runtime: {}
                    };
                """)
                
                self._active_contexts += 1
                logger.debug(f"Created new page (active contexts: {self._active_contexts})")
                
                return page, context
                
            except Exception as e:
                logger.error(f"Error creating page: {e}")
                raise
    
    async def close_page(self, page: Page, context: BrowserContext):
        """
        Close a page and its context.
        
        Args:
            page: The page to close
            context: The browser context to close
        """
        try:
            if page and not page.is_closed():
                await page.close()
            if context:
                await context.close()
            self._active_contexts = max(0, self._active_contexts - 1)
            logger.debug(f"Closed page (active contexts: {self._active_contexts})")
        except Exception as e:
            logger.debug(f"Error closing page/context: {e}")
    
    async def shutdown(self):
        """Shutdown the browser pool and cleanup resources."""
        async with self._lock:
            try:
                if self.browser:
                    await self.browser.close()
                    self.browser = None
                if self.playwright:
                    await self.playwright.stop()
                    self.playwright = None
                logger.info("Browser pool shutdown successfully")
            except Exception as e:
                logger.error(f"Error shutting down browser pool: {e}")
    
    @classmethod
    async def get_instance(cls) -> 'BrowserPool':
        """Get the singleton instance of BrowserPool."""
        instance = cls()
        await instance.initialize()
        return instance


# Global instance
_browser_pool: Optional[BrowserPool] = None

async def get_browser_pool() -> BrowserPool:
    """Get or create the global browser pool instance."""
    global _browser_pool
    if _browser_pool is None:
        _browser_pool = await BrowserPool.get_instance()
    return _browser_pool
