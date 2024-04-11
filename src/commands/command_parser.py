import argparse
import asyncio
from typing import Sequence, Optional
from processing.processor import DataProcessor


class CommandParser:
    def __init__(self, config: dict):
        self.config = config
        self.processor = DataProcessor(config)
        self.commands = {
            'process': self.processor.process_files,
            'run_data_preparation': self.processor.run_data_preparation,
            'validate_output': self.processor.validate_output,
            'upload_output': self.processor.upload_output,
            'run_all': self.processor.run_all
        }

    async def parse_args(self, args: Optional[Sequence[str]] = None) -> argparse.Namespace:
        parsed_args = await self.parser.parse_args(args=args)  # Fixed the missing 'await' keyword
        await self.execute_command(parsed_args)
        return parsed_args

    async def execute_command(self, parsed_args):
        command = parsed_args.command
        try:
            if command in self.commands:
                await self.commands[command](parsed_args)
        except Exception as e:
            print(f"An error occurred during command execution: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        # Perform any cleanup tasks here
        pass
