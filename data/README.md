# Data

This folder contains all the data used.

1. `base/` contains all base-datasets incorporated in one way or another in the used dataset. Each has its own folder with a readme containing a citation and the number of samples.
2. `dataset/` contains the images used as in the dataset.
3. `dataset.csv` contains a list of all images used in the dataset, each assigned a unique ID.
4. `validation_set.csv` contains a list of image-IDs and filenames, specifying a subset of the dataset used for validation of the automatic labelling approach.
5. `validation_labels.csv` contains the labelled validation subset (human and auto labelled).
6. `build_validation_set.py` samples a subset of given size from the dataset and saves it to `validation_set.csv`.
