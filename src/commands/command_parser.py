import argparse
from typing import Sequence, Optional
from src.processing.processor import DataProcessor
from src.utils import LoggerService

class CommandParser:
    def __init__(self, config: dict):
        self.config = config
        self.processor = DataProcessor(config)
        self.logger = LoggerService.get_instance()
        self.commands = {
            'process': self.processor.process_files,
            'run_data_preparation': self.processor.run_data_preparation,
            'validate_output': self.processor.validate_output,
            'upload_output': self.processor.upload_output,
            'run_all': self.processor.run_all
        }

    async def parse_args(self, args: Optional[Sequence[str]] = None) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Command parser for data processing tasks")
        parser.add_argument('command', choices=self.commands.keys(), help='The command to execute')
        parsed_args = parser.parse_args(args=args)
        await self.execute_command(parsed_args)
        return parsed_args

    async def execute_command(self, parsed_args):
        command = parsed_args.command
        try:
            if command in self.commands:
                await self.commands[command]()
        except Exception as e:
            self.logger.error(f"An error occurred during command execution: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        # Perform any cleanup tasks here
        pass
