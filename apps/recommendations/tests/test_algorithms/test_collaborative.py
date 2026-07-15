"""
Tests recommendations/algorithms/collaborative/*.py
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from recommendations.algorithms.collaborative.user_matrix import build_user_matrix
from recommendations.algorithms.collaborative.similarity import calculate_similarity
from recommendations.algorithms.collaborative.prediction import predict_movie_ratings
from recommendations.algorithms.collaborative.ranking import rank_recommendations