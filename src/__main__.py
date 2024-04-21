import tracemalloc
import asyncio

async def main_async():
    tracemalloc.start()  # Get the object allocation traceback
    from utils import LoggerService
    
    logger = LoggerService("MainLogger", [0,100]) 
    
    try:
        from app import Application
        app = Application()
        await app.async_init()  # Initialize async parts of the Application
        await app.run()  # Run the application

    except Exception as error:
        await logger.log("error", f"Exception occurred: {error}")  # Use the LoggerService instance for logging exceptions.
    finally:
        tracemalloc.stop()  # Stop tracemalloc after the main function execution

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(main_async())
    else:
        loop.run_until_complete(main_async())
