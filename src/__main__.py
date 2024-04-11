import sys
import asyncio
from .. import Application

async def main():
    try:
        app = Application()
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
            app.utils.log_error(f"Invalid command: {args.command}")

    except Exception as error:
        app.utils.log_error(f"Encountered an error: {error}")
        app.utils.log_error_with_exception(error)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())