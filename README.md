# NYU DevOps SP25 Project -- Recommendations Squad
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-001/recommendations/graph/badge.svg?token=y6OUlCB4bC)](https://codecov.io/gh/CSCI-GA-2820-SP25-001/recommendations)
[![Build Status](https://github.com/CSCI-GA-2820-SP25-001/recommendations/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-001/recommendations/actions)

Based on [NYU DevOps Project Template](github.com/nyu-devops/project-template)


## Overview

 This repo belongs to the Recommendations Squad who is responsible for managing relationships between two products.

 The `/service` folder contains our `models.py` file for our model and a `routes.py` file for our service. The `/tests` folder has test cases for testing the model and the service separately.

## Manual Setup

You can clone this repository into your a folder on your local computer.
You can use the following command:

```
git clone https://github.com/CSCI-GA-2820-SP25-001/recommendations.git
```


## Contents

This repository contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Database Table Schema

| Column | Description |
| ------ | ----------- |
| id | Integer, serves as the primary key |
| product_a_sku |  String with no more than 25 characters, can not be null, represents product a |
| product_b_sku |  String with no more than 25 characters, can not be null, represents product b |
| type | one of {"UP_SELL", "CROSS_SELL", "ACCESSORY", "BUNDLE"}, denotes the relationship between product a and product b |

### Example Object

```Python
{'id': 1033, 'likes': 0, 'product_a_sku': 'uRfNZyNY', 'product_b_sku': 'svLLqnLF', 'type': 'ACCESSORY'}
```

### Testing
Use either of the following commands to test the code:

```
make test
```
or 
```
pytest
```

Use the following command to run on Local Host: 

```
make run
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
