import pandas as pd


# Selects a subset of the data for manual labelling
def select_validation_set(size: int = 50) -> pd.DataFrame:
  samples = pd.read_csv("data.csv", sep=";")

  val_set = samples.sample(n=size)
  val_set.to_csv("validation_set.csv", index=False)
  return val_set

select_validation_set()
