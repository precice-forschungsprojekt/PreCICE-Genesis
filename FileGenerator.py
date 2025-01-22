from pathlib import Path
from generation_utils.StructureHandler import StructureHandler
from generation_utils.Logger import Logger
from controller_utils.ui_struct.UI_UserInput import UI_UserInput
from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from controller_utils.precice_struct import PS_PreCICEConfig
from generation_utils.AdapterConfigGenerator import AdapterConfigGenerator
import yaml
import argparse
import subprocess
import os
import sys

class FileGenerator:
    def __init__(self, input_file: Path, output_path: Path) -> None:
        """ Class which takes care of generating the content of the necessary files
            :param input_file: Input yaml file that is needed for generation of the precice-config.xml file
            :param output_path: Path to the folder where the _generated/ folder will be placed"""
        self.input_file = input_file
        self.precice_config = PS_PreCICEConfig()
        self.mylog = UT_PCErrorLogging()
        self.user_ui = UI_UserInput()
        self.logger = Logger()
        self.structure = StructureHandler(output_path)

    def _generate_precice_config(self) -> None:
        """Generates the precice-config.xml file based on the topology.yaml file."""

        # Try to open the yaml file and get the configuration
        try:
            with open(self.input_file, "r") as config_file:
                config = yaml.load(config_file.read(), Loader=yaml.SafeLoader)
                self.logger.info(f"Input YAML file: {self.input_file}")
        except FileNotFoundError:
            self.logger.error(f"Input YAML file {self.input_file} not found.")
            return
        except Exception as e:
            self.logger.error(f"Error reading input YAML file: {str(e)}")
            return

        # Build the ui
        self.logger.info("Building the user input info...")
        self.user_ui.init_from_yaml(config, self.mylog)

        # Generate the precice-config.xml file
        self.logger.info("Generating preCICE config...")
        self.precice_config.create_config(self.user_ui)

        # Set the target of the file and write out to it
        # Warning: self.structure.precice_config is of type Path, so it needs to be converted to str
        target = str(self.structure.precice_config)
        try:
            self.logger.info(f"Writing preCICE config to {target}...")
            self.precice_config.write_precice_xml_config(
            target, self.mylog, sync_mode=self.user_ui.sim_info.sync_mode, mode=self.user_ui.sim_info.mode
        )

        except Exception as e:
            self.logger.error(f"Failed to write preCICE XML config: {str(e)}")
            return

        self.logger.success(f"XML generation completed successfully: {target}")
    
    def _generate_static_files(self, target: Path, name: str) -> None:
        """Generate static files from templates
            :param target: target file path
            :param name: name of the function"""
        try:
            tempalte = Path(__file__).parent / "templates" / f"template_{name}"
            self.logger.info(f"Reading in the template file for {name}")

            # Check if the template file exists
            if not tempalte.exists():
                raise FileNotFoundError(f"Template file not found: {tempalte}")

            # Read the template content
            template_content = tempalte.read_text(encoding="utf-8")

            self.logger.info(f"Writing the template to the target: {str(target)}")

            # Write content to the target file
            with open(target, 'w', encoding="utf-8") as template:
                template.write(template_content)

            self.logger.success(f"Successfully written {name} content to: {str(target)}")

        except FileNotFoundError as fileNotFoundException:
            self.logger.error(f"File not found: {fileNotFoundException}")
        except PermissionError as premissionErrorException:
            self.logger.error(f"Permission error: {premissionErrorException}")
        except Exception as generalExcpetion:
            self.logger.error(f"An unexpected error occurred: {generalExcpetion}")
        pass
    
    def _generate_README(self) -> None:
        """Generates the README.md file"""
        self._generate_static_files(target=self.structure.README,
                                    name="README.md")

    def _generate_run(self, run_sh: Path) -> None:
        """Generates the run.sh file
            :param run_sh: Path to the run.sh file"""
        self._generate_static_files(target=run_sh,
                                    name="run.sh")

    def _generate_clean(self) -> None:
        """Generates the clean.sh file."""
        self._generate_static_files(target=self.structure.clean,
                                    name="clean.sh")

    def _generate_adapter_config(self, target_participant: str, adapter_config: Path) -> None:
        """Generates the adapter-config.json file."""
        adapter_config_generator = AdapterConfigGenerator(adapter_config_path=adapter_config,
                                                            precice_config_path=self.structure.precice_config, 
                                                            topology_path=self.input_file,  
                                                            target_participant=target_participant)
        adapter_config_generator.write_to_file()
    
    def generate_level_0(self) -> None:
        """Fills out the files of level 0 (everything in the root folder)."""
        self._generate_clean()
        self._generate_README()
        self._generate_precice_config()
    
    def _extract_participants(self) -> list[str]:
        """Extracts the participants from the topology.yaml file."""
        try:
            with open(self.input_file, "r") as config_file:
                config = yaml.load(config_file.read(), Loader=yaml.SafeLoader)
                self.logger.info(f"Input YAML file: {self.input_file}")
        except FileNotFoundError:
            self.logger.error(f"Input YAML file {self.input_file} not found.")
            return
        except Exception as e:
            self.logger.error(f"Error reading input YAML file: {str(e)}")
            return
        
        return list(config["participants"].keys())
    
    def generate_level_1(self) -> None:
        """Generates the files of level 1 (everything in the generated sub-folders)."""

        participants = self._extract_participants()
        for participant in participants:
            target_participant = self.structure.create_level_1_structure(participant)
            adapter_config = target_participant[1]
            run_sh = target_participant[2]
            self._generate_adapter_config(target_participant=participant, adapter_config=adapter_config)
            self._generate_run(run_sh)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Takes topology.yaml files as input and writes out needed files to start the precice.")
    parser.add_argument(
        "-f", "--input-file", 
        type=Path, 
        required=False, 
        help="Input topology.yaml file",
        default=Path("controller_utils/examples/1/topology.yaml")
    )
    parser.add_argument(
        "-o", "--output-path",
        type=Path,
        required=False,
        help="Output path for the generated folder.",
        default=Path(__file__).parent
    )

    args = parser.parse_args()

    fileGenerator = FileGenerator(args.input_file, args.output_path)
    fileGenerator.generate_level_0()
    fileGenerator.generate_level_1()
    
    # Format the generated preCICE configuration

    # Find the precice-config.xml file in the generated directory
    generated_dir = args.output_path / '_generated'
    precice_config_path = None
    for root, dirs, files in os.walk(generated_dir):
        for file in files:
            if file == 'precice-config.xml':
                precice_config_path = os.path.join(root, file)
                break
        if precice_config_path:
            break
    
    # Format the precice-config.xml if found
    if precice_config_path:
        print("Formatting preCICE configuration...")
        print(precice_config_path)
        try:
            result = subprocess.run([sys.executable, 'format_precice_config.py', precice_config_path], 
                                    check=True, 
                                    capture_output=True, 
                                    text=True)
            print("preCICE configuration formatted successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error formatting preCICE configuration: {e.stderr}")
    else:
        print("No precice-config.xml found to format.")