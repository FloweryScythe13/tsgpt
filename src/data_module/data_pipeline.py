import pandas as pd
from datasets import load_dataset
from utils.util import get_proj_root
from hamilton.function_modifiers import extract_fields, config


@config.when(loader="hf")
def miws_dataset__hf(project_root: str = get_proj_root()) -> pd.DataFrame:
    """Load the MIWS dataset using the HuggingFace Dataset library"""
    dataset = load_dataset(f"{project_root}/data2/", split="train")
    return dataset.to_pandas()


@config.when(loader="pd")
def miws_dataset__pd(project_root: str = get_proj_root()) -> pd.DataFrame:
    """Load the MIWS dataset using the Pandas library"""
    return pd.read_csv(f"{project_root}/data/MIWS_Seed_Complete.csv", delimiter=',', quotechar='"')


def clean_dataset(miws_dataset: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and drop unecessary columns"""
    cleaned_df = miws_dataset[["ID", "Text", "Ideology", "Label", "Geographical_Location"]]
    return cleaned_df


def filtered_dataset(clean_dataset: pd.DataFrame, n_rows_to_keep: int = 400) -> pd.DataFrame:
    if n_rows_to_keep is None:
        return clean_dataset

    return clean_dataset.head(n_rows_to_keep)


@extract_fields(
    dict(
        ids=list[int],
        text_contents=list[str],
        ideologies=list[str],
        labels=list[str],
        locations=list[str],
    )
)
def dataset_rows(filtered_dataset: pd.DataFrame) -> dict:
    """Convert dataframe to dict of lists"""
    df_as_dict = filtered_dataset.to_dict(orient="list")
    return dict(
        ids=df_as_dict["ID"], text_contents=df_as_dict["Text"], ideologies=df_as_dict["Ideology"], labels=df_as_dict["Label"], locations=df_as_dict["Geographical_Location"], 
    )
