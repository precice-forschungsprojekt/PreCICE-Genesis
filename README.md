# PreCICE Structure Generator

## Project Overview

The PreCICE Structure Generator is a Python-based utility designed to automate the generation of preCICE configuration files from YAML topology descriptions. This tool simplifies the process of setting up multi-physics simulations by transforming user-defined YAML configurations into preCICE-compatible XML configuration files.

## Key Features

- Automated preCICE configuration generation
- YAML-based input parsing
- Flexible topology description support
- Comprehensive error logging and handling
- Simple command-line interface

## Prerequisites

- **Python 3.11** (Required - not compatible with Python 3.8 or earlier)
- preCICE library
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-organization/precice-structure-generator.git
cd precice-structure-generator
```

2. Execute the setup script for your system inside the setup_scripts directory:
```bash
./setup_scripts/install_dependencies.sh
#or
./setup_scripts/install_dependencies.ps1
```

3. Alternatively,  if you like to do it manually:

    3.1 Create and activate a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
    3.2 Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    3.3 Initialize the submodule:
    ```bash
    git submodule update --init	
    ```

## Usage

### Command-Line Interface

Generate a preCICE configuration file from a YAML topology:

```bash
python FileGenerator.py -f path/to/your/topology.yaml
```

### Configuration

1. Prepare a YAML topology file describing your multi-physics simulation setup.
2. Use the command-line interface to generate the preCICE configuration.
3. The tool will create the necessary configuration files in the `_generated/` directory.

## Dependencies

- attrs==24.2.0
- colorama==0.4.6
- exceptiongroup==1.2.2
- iniconfig==2.0.0
- jsonschema==4.23.0
- jsonschema-specifications==2024.10.1
- lxml==5.3.0
- myutils==0.0.21
- packaging==24.2
- pip-check-reqs==2.5.3
- pluggy==1.5.0
- pyaml==24.9.0
- pytest==8.3.4
- PyYAML==6.0.2
- referencing==0.35.1
- rpds-py==0.22.1
- termcolor==2.5.0
- tomli==2.2.1
- xmltodict==0.14.2


## Project Structure

```
precice-structure-generator/
│
├── .github/                   # GitHub-specific configurations
├── .git/                      # Git version control directory
│
├── controller_utils/          # Utility from controller
│   ├── precice_struct/        # preCICE configuration structures
│   │   ├── PS_CouplingScheme.py
│   │   └── ...
│   └── ui_struct/             # User interface utilities
│       ├── UI_SimulationInfo.py
│       └── ...
│
├── generation_utils/          # Core generation utilities
│   ├── AdapterConfigGenerator.py
│   ├── Logger.py
│   └── StructureHandler.py
│
├── schemas/                   # JSON/validation schemas
├── setup_scripts/             # Setup and initialization scripts
├── templates/                 # Configuration templates
├── tests/                     # Project test suite
├── tutorials/                 # Extensive tutorials (from original preCICE)
├── validation/                # Validation modules
│
├── _generated/                # Generated configuration files
│   └── precice-config.xml     # Example generated configuration
│
├── FileGenerator.py           # Main file generation script
├── README.md                  # Project documentation (This file)
├── requirements.txt           # Project dependencies
├── pyproject.toml             # Project configuration
└── .gitignore                 # Git ignore file
```

## Logging and Error Handling

The tool provides detailed logging to help you understand the configuration generation process:
- Tracks input YAML file details
- Validates user input
- Generates comprehensive error messages
- Supports troubleshooting configuration issues

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Troubleshooting

- Ensure all dependencies are correctly installed
- Verify the format of your input YAML file
- Check the generated logs for detailed error information

## License

[Specify your project's license]

## Contact

[Add contact information or project maintainer details]

## Acknowledgements

This project was started with code from the [preCICE controller](https://github.com/precice/controller) repository.
The file `format_precice_config.py` was taken from [preCice pre-commit hook file](https://github.com/precice/precice-pre-commit-hooks/blob/main/format_precice_config/format_precice_config.py)
