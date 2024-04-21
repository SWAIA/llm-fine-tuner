import asyncio
import sys
from typing import Dict, Optional

class Application:
    def __init__(self, config_overrides: Optional[Dict[str, str]] = None):
        self.config_path = './../config.json'
        self.logger = None
        self.config_manager = None
        self.utils = None
        self.config = config_overrides  # Directly use the provided overrides
        self.waiting = False

    async def async_init(self):
        from utils import LoggerService, ConfigManager  # Imports moved here to avoid circular dependency
        self.logger = self.logger or await LoggerService.get_instance("ApplicationLogger", (30, 40))
        self.config_manager = self.config_manager or ConfigManager(self.config_path)
        self.config = self.config or await self.config_manager.load_config()
        asyncio.create_task(self._setup_async())

    async def _setup_async(self):
        await self.logger.log("info", "Application initialized.")

    async def run(self):
        from commands.command_parser import CommandParser
        command_parser = CommandParser(self.config)
        await command_parser.parse_args()

    async def _check_waiting_state(self):
        if self.waiting:
            breakpoint()
            await self.logger.log("info", "Application is in pause state. Please resume to proceed.")

    async def process_and_log_context(self, _: str):
        # This method seems to be unrelated to the current refactoring but remains for potential future use.
        pass

    @staticmethod
    async def _log_application_failure(error):
        print(f"Application failed to start: {error}")

    @classmethod
    async def main(cls):
        try:
            config_overrides = sys.argv[1] if len(sys.argv) > 1 else None
            app = cls(config_overrides)
            await app.async_init()  # Initialize async parts
            await app._check_waiting_state()
            await app.run()
        except Exception as e:
            await cls._log_application_failure(e)

if __name__ == "__main__":
    asyncio.run(Application.main())
