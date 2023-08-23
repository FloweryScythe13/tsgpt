from hamilton import base, driver

import logging
import sys
import data_pipeline


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)

def main():  
    config = {} # we don't have any configuration or invariant data for this example.
    dr = driver.Driver(
        data_pipeline
    )
    # The `final_vars` requested are functions with side-effects
    print(dr.execute(
        final_vars=["text_contents", "labels"],
    ))

        


if __name__ == "__main__":
    main()