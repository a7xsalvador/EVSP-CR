# Electric Vehicle Scheduling Problem with Charging Restrictions (EVSP-CR)

This repository contains the code developed as part of the thesis titled **"Electric Vehicle Assignment Problem with Limited Capacity Charging Stations"**.

## 📖 Description
The objective of this work is to model and solve the electric vehicle assignment problem considering the limited capacity of charging stations. Mathematical models and optimization algorithms were developed to find efficient solutions.

## 📂 Repository Structure

```
📁 EVSP-CR
 ├── 📁 scripts            # Algorithm implementations
 │   ├── model_arcs.py     # Arc-based model
 │   ├── model_routes.py   # Route-based model
 │   ├── heuristic.py      # LOWRES heuristic implementation
 │   ├── utils.py          # Auxiliary functions
 ├── 📁 results            # Computational experiment results
 ├── README.md             # This file
 ├── requirements.txt      # Necessary libraries to run the code
 └── LICENSE               # Code license
```

## 🚀 Requirements
To run the code, it is recommended to use Python 3.8 or later. Install dependencies by running:

```bash
pip install -r requirements.txt
```

## 📜 Usage
The main scripts can be executed as follows:

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

## 🔬 Thesis Data
The test datasets used in the experiments are available in the `data/` folder.

## 📄 License
This code is distributed under the MIT license. See the `LICENSE` file for more details.

## ✉️ Contact
If you have any questions or suggestions, you can contact the author:

📧 [a7xsalvador@hotmail.com](mailto:a7xsalvador@hotmail.com)

👤 Gabriel Eduardo Salvador Jimenez
