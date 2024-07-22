import sys
import pytest
import os
import numpy as np
# sys.path.insert(0, '../')
# sys.path.insert(0, os.path.dirname(__file__))
# os.chdir('../')
print('Current directory:', os.getcwd())


from scripts.scrape_google_scholar import calc_h_index

# pytest for calc_h_index

@pytest.mark.parametrize("citations, h_index", [[[], 0],
                                                [[1], 1],
                                                [[1, 2, 3, 4, 5], 3],
                                                [[1, 2, 3, 4, 5, 6], 3],
                                                [[1, 2, 3, 4, 5, 6, 7], 4],
                                                [[1, 0, 0, 0, 0, 1], 1],
                                                [[4, 4,4,4,4, 4], 4],
                                                ])
def test_calc_h_index(citations, h_index):
    citations = np.array(citations)
    assert calc_h_index(citations) == h_index
