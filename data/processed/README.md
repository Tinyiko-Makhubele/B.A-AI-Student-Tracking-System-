# OULAD day-63 prepared data

This directory contains the versioned modelling table and the Week 1 preparation notes for the EduAI early-warning prototype.

The modelling CSV contains 26,292 eligible student-course records from all 22 course presentations. It includes the binary at_risk target and a student-disjoint evaluation_split assignment. The source final_result and id_student fields are omitted. Demographic fields are retained for subgroup checks only.

## Rebuild

Download the Open University Learning Analytics Dataset (OULAD) source CSVs from [UCI](https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset) and place them under data/raw/. Install the packages listed in requirements-data-prep.txt, then run python scripts/build_oulad_day63.py and python scripts/inspect_oulad.py from the repository root.

UCI lists OULAD under CC BY 4.0. This derived table applies linked-table joins, a day-63 feature cutoff, cohort filtering, target mapping, and split assignment. Cite Kuzilek, Hlosta, and Zdrahal (2017), *Open University Learning Analytics Dataset*, *Scientific Data*, 4, 170171, https://doi.org/10.1038/sdata.2017.171.

No model has been trained. The dataset is a public-data prototype, not evidence about current students at the project institution.
