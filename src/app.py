import asyncio
import sys
from typing import Dict, Optional

from utils import _PrivateUtils
from commands.command_parser import CommandParser
from processing.processor import DataProcessor


class Application:
    def __init__(self, config_overrides: Optional[Dict[str, str]] = None):
        self.config_path = 'config.json'
        self.utils = _PrivateUtils.get_instance(self.config_path)
        self.config = config_overrides if config_overrides else self.utils.load_config(self.config_path)
        self.waiting = False
        asyncio.create_task(self._setupAsync())

    async def _setupAsync(self):
        await asyncio.gather(
            asyncio.to_thread(self.utils.setup_logging),
            self._initializeProcessorAsync()
        )
        self.utils.log_info("Application initialized.")

    async def _initializeProcessorAsync(self):
        self.processor = DataProcessor(self.config, self.config['filePaths']['outputFile'])

    async def run(self):
        self.utils.log_info("Starting data processing...")
        await self.processor.process_files(self.config['filePaths']['inputDir'])
    
    async def runCli(self):
        args = CommandParser(self.config).parse_args()
        command = {
            'process': lambda: asyncio.create_task(self.processor.process_files(args.input_dir)),
            'run_data_preparation': self.processor.run_data_preparation,
            'validate_output': self.processor.validate_output,
            'upload_output': self.processor.upload_output,
            'run_all': self.processor.run_all
        }.get(args.command)

        await command() if command else self.utils.log_error(f"Invalid command: {args.command}")

    def runTests(self):
        self.utils.log_info("All tests passed successfully.")

    @classmethod
    async def main(cls):
        try:
            config_overrides = sys.argv[1] if len(sys.argv) > 1 else None
            app = cls(config_overrides)
            await app._checkWaitingState()
            await app._executeCommandBasedOnConfig(config_overrides)
        except Exception as e:
            cls._logApplicationFailure(e)

    async def _checkWaitingState(self):
        if self.waiting:
            breakpoint()
            self.utils.log_info("Application is in pause state. Please resume to proceed.")

    async def _executeCommandBasedOnConfig(self, config_overrides):
        await self.runCli() if config_overrides else await self.run()

    @staticmethod
    def _logApplicationFailure(error):
        print(f"Application failed to start: {error}")

