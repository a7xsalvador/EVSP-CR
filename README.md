# Electric Vehicle Scheduling Problem with Charging Restrictions (EVSP-CR)
This repository contains the code developed as part of the thesis titled **"Electric Vehicle Assignment Problem with Limited Capacity Charging Stations"**.

## Description
The objective of this work is to model and solve the electric vehicle assignment problem considering the limited capacity of charging stations. Mathematical models and optimization algorithms were developed to find efficient solutions.

- **compatibility.py** has functions for the compatibility relations defined in the thesis.
- **generate_data.py** has a function that generates random instances.
- **graph_construction.py** creates the arcs and nodes for a given instance. It also estimates the cost and fuel consumption of each arc based on the distance between two elements of a randomly generated city in `generate_data.py`.
- **initial_model.py** has a function that relaxes the master problem and calls the column generation algorithm.
- **lp_functions.py** has auxiliary functions needed in `initial_model.py`.
- **model_functions.py** has functions needed before creating an instance: for time discretization, for computing the Manhattan distance, and for estimating the time to go from one point to another within the city.


## Requirements
To run the code, it is recommended to use Python 3.8 or later. Install dependencies by running:

```bash
pip install -r requirements.txt
```

In each folder you will find an .ipynb which can create a random instance and optimize the problem.


## Usage The main scripts can be executed as follows: 

```bash
python scripts/model_arcs.py
```

```bash
python scripts/model_routes.py
```

To run the LOWRES heuristic:
```bash
python scripts/heuristic.py
```

## Thesis Data
The results of the implementation of the algorithm can be found in the folder `data`.


## License
This code is distributed under the APACHE license. See the `LICENSE` file for more details.

## Contact
If you have any questions or suggestions, you can contact the author:

[a7xsalvador@hotmail.com](mailto:a7xsalvador@hotmail.com)

Gabriel Eduardo Salvador Jimenez
