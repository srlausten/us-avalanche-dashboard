# US Avalanche Data Dashboard

## Overview

This project is an Avalanche dashboard that visualizes accident data using Python and Data from CAIC US Database. It includes data exploration and visualization tools, and a beta predictive-analysis tool, **not to be used for actual predictions**.  
![dashboard](https://github.com/srlausten/us-avalanche-dashboard/assets/65357089/a9ec671a-1b6b-4ab7-971f-4a2e0e714cb2)

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Dashboard](#dashboard)
- [License](#license)

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- Python (>=3.10) installed
- Poetry installed (for dependency management)

### Installation

1. Clone the repository:

   ```bash
   git clone 
   cd 
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install project dependencies using Poetry:

   ```bash
   poetry install
   ```

## Usage

To run the Panel dashboard, use the following command:

```bash
poetry run python main.py
```

The dashboard will be accessible in your web browser at `http://localhost:5006`.

## Dashboard

- **Map Visualization**: Visualizes accident data on a map using Plotly's Scatter Mapbox. Includes a date slider to filter accidents.

- **Histogram**: Shows a monthly accident histogram with a slider to filter data by month.

- **Predictive Modeling**: WIP



## License

This project is licensed under the [MIT License](LICENSE).

---

...
