# Automashup

Automashup is a Python application that allows you to generate a mashup from two songs automatically.

## Installation

pip install -r requirements.txt

To install All-In-One Music Structure Analyzer: https://github.com/mir-aidj/all-in-one/tree/main (LINUX, MACOS RECOMMANDED!)

To install and test DMC on your own: https://github.com/csteinmetz1/automix-toolkit (clone + set up (modify sklearn --> scikit-learn in the setup.py) and test directly on your machine, dont forget to modify the paths) 

## Tutorial

cd ./mashup

streamlit run streamlit.py

## Adding Mashup Methods

The aim of this interface is to present multiple mashup technics.

You can add some to the application by creating a mashup function in the file /mashup/mashup.py. Then to show it in the interface you just have to add it to the list of mashup_technics in the file /mashup/streamlit.py
