import pandas as pd
from datasets import load_dataset
from utils import util
from hamilton.function_modifiers import extract_fields


PROJ_ROOT = util.get_proj_root()

def miws_dataset() -> pd.DataFrame:
    """Load the MIWS dataset using the HuggingFace Dataset library"""
    dataset = load_dataset(f"{PROJ_ROOT}/data/MIWS_Seed_Complete.csv", split="train")
    return dataset.to_pandas()


def clean_dataset(miws_dataset: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and drop unecessary columns"""
    cleaned_df = cleaned_df[["Text", "Label", "Geographical_Location"]]
    return cleaned_df


def filtered_dataset(clean_dataset: pd.DataFrame, n_rows_to_keep: int = 20) -> pd.DataFrame:
    if n_rows_to_keep is None:
        return clean_dataset

    return clean_dataset.head(n_rows_to_keep)


@extract_fields(
    dict(
        text_contents=list[str],
        labels=list[str],
        locations=list[str],
    )
)
def dataset_rows(filtered_dataset: pd.DataFrame) -> dict:
    """Convert dataframe to dict of lists"""
    df_as_dict = filtered_dataset.to_dict(orient="list")
    return dict(
        text_contents=df_as_dict["Text"], labels=df_as_dict["Label"], locations=df_as_dict["Geographical_Location"], 
    )

