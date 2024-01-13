from hamilton import base, driver

import logging
import sys
import data_pipeline


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)

def main():  
    config = {"loader": "hf"}  # or "pd"
    dr = driver.Driver(
        config,
        data_pipeline
    )
    # The `final_vars` requested are functions with side-effects
    print(dr.execute(
        final_vars=["text_contents", "labels"],
        inputs={"project_root": "."}  # I specify this because of how I run this example.
    ))

        


if __name__ == "__main__":
    main()