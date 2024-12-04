# 3D File Conversion Tool

This tool is used to convert structural software files to .obj. The two supported file types are RISA-3D and Modelsmart 3D.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- Converts RISA-3D files (.r3d) to OBJ format.
- Converts Modelsmart files (.3dd) to OBJ format.
- Generates OBJ files compatible with Fusion 360.
- Supports batch conversion of multiple files, and file types
- Can generate a single .obj or multiple .obj view projections for 3D printing. 

## Installation

### Executable File.
1. Run the executable.

### Source Files.
1. Clone the repository.
2. Install the dependencies | pip install -r requirements.txt

## Usage
### Current tested versions of RISA-3D
- 20.0501
- 22.01000
### Current tested version of Modelsmart 3D
- Version 4

### Executable file.
1. Run the executable.
2. Select your input file(s).
3. Select your desination folder.
4. Choose any extra options.
5. Select convert.

### Source Files
1. Install dependencies.
2. run convert.py in the src directory.
3. Select your input file(s).
4. Select your desination folder.
5. Choose any extra options.
6. Select convert.

## Contributing
Contributions are welcome! Please fork this repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
This project uses:
- [NumPy](https://numpy.org/), licensed under the BSD 3-Clause License.
- [tkinter-tooltip](https://pypi.org/project/tkinter-tooltip/), licensed under the MIT License.

