# Automatic Handwriting Quality Analysis: Classification Accuracy and Feature Interpretability

This repo contains all files used for my bachelor thesis at Technical University Berlin, Germany.

Supervised by [Prof. Dr. Bettina Berendt](https://people.cs.kuleuven.be/~bettina.berendt/) @ [IaS](https://www.tu.berlin/en/ias/about/team) TU Berlin.

## Usage

```bash
$ pip install -r requirements.txt       # install repo requirements
```

### The Labeller

Used to acquire quality labels on handwritten document by human readers along two standardized scales (_HLS_[^1] and _An Evaluation of Handwriting Performance_[^2]). To use on the validation dataset from `data/validation_set.csv`, run:

```bash
$ python labeller/labeller.py           # run from project root
```

### Generating Validation Dataset

To randomly sample a subset of the general dataset (used here for validation of the automatic labelling approach), run:

```bash
$ python data/build_validation_set.py   # run from project root
```



[^1]: J. Ziviani and J. Elkins, “An Evaluation of Handwriting Performance,” Educational Review, vol. 36, no. 3, pp. 249–261, Nov. 1984, doi: 10.1080/0013191840360304.
[^2]: A. L. Barnett, M. Prunty, and S. Rosenblum, “Development of the Handwriting Legibility Scale (HLS): A preliminary examination of Reliability and Validity,” Research in Developmental Disabilities, vol. 72, pp. 240–247, Jan. 2018, doi: 10.1016/j.ridd.2017.11.013.
