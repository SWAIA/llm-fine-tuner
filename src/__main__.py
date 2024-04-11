import sys
import asyncio
from app import Application
from utils import AsyncThreadSafeLogger, ContextualLoggerAdapter

async def main():
    logger = AsyncThreadSafeLogger(__name__, logging.ERROR)
    contextual_logger = ContextualLoggerAdapter(logger.logger, {})
    try:
        app = Application()
        await app._setupAsync()  # Ensure the application setup is complete before proceeding.
        args = app.command_parser.parse_args()
        command_methods = {
            'process': lambda: asyncio.create_task(app.processor.process_files(args.input_dir)),
            'run_data_preparation': app.processor.run_data_preparation,
            'validate_output': app.processor.validate_output,
            'upload_output': app.processor.upload_output,
            'run_all': app.processor.run_all
        }

        command = command_methods.get(args.command)
        if command:
            await command()
        else:
            await contextual_logger.error(f"Invalid command: {args.command}")

    except Exception as error:
        await contextual_logger.error_with_exception(error)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())