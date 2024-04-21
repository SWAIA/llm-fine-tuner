from utils import LoggerService

class CLIOperations:
    def __init__(self):
        self.logger = LoggerService.get_instance()

    def run_data_augmentation(self, input_dir, output_file):
        if input_dir and output_file:
            self.logger.log("info", f"./shell_controller.sh run_data_augmentation {input_dir} {output_file}")

    def set_permissions(self, script_path):
        if script_path:
            self.logger.log("info", f"./shell_controller.sh set_permissions {script_path}")

    def run_data_preparation(self, input_dir, output_file):
        if input_dir and output_file:
            self.logger.log("info", f"./shell_controller.sh run_data_preparation {input_dir} {output_file}")

    def validate_output(self, output_file):
        if output_file:
            self.logger.log("info", f"./shell_controller.sh validate_output {output_file}")

    def upload_output(self, output_file):
        if output_file:
            self.logger.log("info", f"./shell_controller.sh upload_output {output_file}")

    def run_all(self, log_file, input_dir, output_file, temp_dir):
        if log_file and input_dir and output_file and temp_dir:
            self.logger.log("info", f"./shell_controller.sh run_all {log_file} {input_dir} {output_file} {temp_dir}")

    def run_cleanup(self, temp_dir):
        if temp_dir:
            self.logger.log("info", f"./shell_controller.sh cleanup_temp_files {temp_dir}")

    def run_summary_report(self, output_file, report_file):
        if output_file and report_file:
            self.logger.log("info", f"./shell_controller.sh run_summary_report {output_file} {report_file}")
