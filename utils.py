async def optimize_page(page):
    """
    Blocks unnecessary resources like images, stylesheets, media, and fonts
    to drastically reduce bandwidth usage.
    """
    blocked_resource_types = ["image", "stylesheet", "media", "font", "other"]
    
    async def route_intercept(route):
        if route.request.resource_type in blocked_resource_types:
            await route.abort()
        else:
            await route.continue_()
            
    await page.route("**/*", route_intercept)
