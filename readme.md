# VIROMEdash - Global Virome Sequence Metadata Visualizer

## 📌 What is VIROMEdash?

**VIROMEdash** is a visual analytics tool for exploring global viral sequence metadata from the [NCBI Virus](https://www.ncbi.nlm.nih.gov/labs/virus/vssi/#/) database. It provides interactive dashboards that visualize metadata across five major dimensions:

- Taxonomy (species)
- Host organism
- Geography
- Collection date
- Baltimore classification

The portal includes data mined from NCBI Virus (as of May 2022), and also supports uploading custom datasets or accession lists.

---

## 🚫 Web Server Status

> **Note:**  
> VIROMEdash is no longer maintained on a public web server due to lack of funding.  
> However, you can **run it locally** by following the installation steps below.

---

## ⚙️ Local Installation Guide

Tested on **Python 3.11**

### 1. Clone the repository

```bash
git clone https://github.com/eselimnl/viromedash.git
cd viromedash

```

### 2. Set up a virtual environment
```
python3.11 -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies
```pip install -r requirements.txt 
```

### 4. Run the app
```
python3.11 app.py
```
If the app is running, open your browser and go to: http://127.0.0.1:8050/

### File structure

viromedash/
├── app.py
├── pages/
│   ├── index.py
│   ├── geography.py
│   ├── species.py
│   ├── host.py
│   ├── date.py
│   ├── baltimore.py
│   └── self_catalogue.py
├── data/
│   └── species_year_nt_prot.csv
├── requirements.txt
└── README.md


