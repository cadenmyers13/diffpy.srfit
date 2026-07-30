#!/usr/bin/env python
##############################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
##############################################################################
"""Tests for fitresults module."""

import unittest

import numpy as np
import pytest
from scipy.optimize import leastsq

from diffpy.srfit.fitbase.fitrecipe import FitRecipe
from diffpy.srfit.fitbase.fitresults import (
    FitResults,
    initializeRecipe,
    resultsDictionary,
)

# The fit results from the recipe fixture in conftest.py
expected_fitresults = """\
My Custom header
Some quantities invalid due to missing profile uncertainty
Overall (Chi2 and Reduced Chi2 invalid)
------------------------------------------------------------------------------
Residual       0.00000000
Contributions  0.00000000
Restraints     0.00000000
Chi2           0.00000000
Reduced Chi2   0.00000000
Rw             0.00000010

Variables (Uncertainties invalid)
------------------------------------------------------------------------------
"""
expected_refined_variables = ["amplitude", "wave_number", "phase_shift"]


def optimize_recipe(recipe):
    recipe.fithooks[0].verbose = 0
    residuals = recipe.residual
    values = recipe.values
    leastsq(residuals, values)


def test_formatResults_deprecated(build_recipes_one_contribution):
    """Deprecated formatResults should still work but emit a
    DeprecationWarning and delegate to get_results_string."""
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    with pytest.deprecated_call():
        actual_results_string = results.formatResults(
            header="My Custom header"
        )
    assert actual_results_string == results.get_results_string(
        header="My Custom header", update=False
    )


def test_get_results_string(build_recipes_one_contribution):
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    actual_results_string = results.get_results_string(
        header="My Custom header"
    )
    # Because slight variations in refinement, just check
    # that the header of the results are the same.
    assert expected_fitresults.strip() in actual_results_string.strip()
    # check if the refined variables are in the results
    for expected_var in expected_refined_variables:
        assert expected_var in actual_results_string.strip()


def test_printResults_deprecated(build_recipes_one_contribution, capsys):
    """Deprecated printResults should still work but emit a
    DeprecationWarning and delegate to print_results."""
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    with pytest.deprecated_call():
        results.printResults(header="My Custom header")
    actual_results = capsys.readouterr().out
    # Because slight variations in refinement, just check
    # that the header of the results are the same.
    assert expected_fitresults.strip() in actual_results.strip()


def test_print_results(build_recipes_one_contribution, capsys):
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    results.print_results(header="My Custom header")
    actual_results = capsys.readouterr().out
    # Because slight variations in refinement, just check
    # that the header of the results are the same.
    assert expected_fitresults.strip() in actual_results.strip()
    # check if the refined variables are in the results
    for expected_var in expected_refined_variables:
        assert expected_var in actual_results.strip()


def test_saveResults_deprecated(build_recipes_one_contribution, tmp_path):
    """Deprecated saveResults should still work but emit a
    DeprecationWarning and delegate to save_results."""
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    actual_results_file = tmp_path / "fit_results.txt"
    with pytest.deprecated_call():
        results.saveResults(actual_results_file, header="My Custom header")
    assert actual_results_file.exists()
    with open(actual_results_file, "r") as res_file:
        actual_results = res_file.read()
    # Because slight variations in refinement, just check
    # that the header of the results are the same.
    assert expected_fitresults.strip() in actual_results.strip()


def test_save_results(build_recipes_one_contribution, tmp_path):
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    actual_results_file = tmp_path / "fit_results.txt"
    results.save_results(actual_results_file, header="My Custom header")
    assert actual_results_file.exists()
    with open(actual_results_file, "r") as res_file:
        actual_results = res_file.read()
    # Because slight variations in refinement, just check
    # that the header of the results are the same.
    assert expected_fitresults.strip() in actual_results.strip()
    # check if the refined variables are in the results
    for expected_var in expected_refined_variables:
        assert expected_var in actual_results.strip()


def test_get_results_dictionary(build_recipes_one_contribution):
    # Case: user gets results dictionary after optimization
    # expected: results dictionary contains expected keys and values
    recipe, _ = build_recipes_one_contribution
    optimize_recipe(recipe)
    results = FitResults(recipe)
    actual_results_dict = results.get_results_dictionary()
    expected_results_dict = {
        "amplitude": 1.000000000060171,
        "wave_number": 1.00000000012548,
        "phase_shift": -1.6129114631049646e-18,
        "Residual": 3.3284672708760557e-19,
        "Contributions": 3.3284672708760557e-19,
        "Restraints": 0,
        "Chi2": 3.3284672708760557e-19,
        "Reduced Chi2": 4.7549532441086507e-20,
        "Rw": 2.7196679825449506e-10,
    }
    actual_values = np.round(np.array(list(actual_results_dict.values())), 5)
    actual_keys = set(actual_results_dict.keys())
    expected_values = np.round(
        np.array(list(expected_results_dict.values())), 5
    )
    expected_keys = set(expected_results_dict.keys())
    assert expected_keys == actual_keys
    assert list(expected_values == list(actual_values))


def test_resultsDictionary(temp_data_files):
    # Case: user gets results dictionary from a results file
    # expected: results dictionary contains expected keys and values
    # resultsDictionary is deprecated in favor of
    # FitResults.get_results_dictionary, but it parses results from a file
    # rather than a live FitResults instance, so it is not a direct
    # delegating alias and keeps its own behavioral coverage here.
    with pytest.deprecated_call():
        actual_results_dict = resultsDictionary(
            temp_data_files / "fit_results.res"
        )
    # bad behavior: values are stored as strings
    expected_results_dict = {
        "than": "25",  # bad behavior: shouldn't be here
        "wave_number": "1.00000000e+00",
        "phase_shift": "-1.61291146e-18",
        "amplitude": "1.00000000e+00",
        "Rw": "0.00000000",
        "Chi2": "0.00000000",
        "Restraints": "0.00000000",
        "Contributions": "0.00000000",
        "Residual": "0.00000000",
        "Feb": "25",  # bad behavior: shouldn't be here
    }
    # convert values to float for comparison (with rounding)
    for key in expected_results_dict:
        expected_results_dict[key] = float(expected_results_dict[key])
    for key in actual_results_dict:
        actual_results_dict[key] = float(actual_results_dict[key])

    actual_keys = set(actual_results_dict.keys())
    actual_values = np.round(np.array(list(actual_results_dict.values())), 5)
    expected_keys = set(expected_results_dict.keys())
    expected_values = np.round(
        np.array(list(expected_results_dict.values())), 5
    )
    assert expected_keys == actual_keys
    assert list(expected_values == list(actual_values))


@pytest.mark.parametrize(
    "as_input",
    [
        lambda filename: filename,
        lambda filename: open(filename, "r"),
        lambda filename: open(filename, "r").read(),
    ],
    ids=["filename", "file_obj", "string"],
)
def testInitializeRecipe_deprecated(datafile, as_input):
    """Deprecated module-level initializeRecipe should still work but
    emit a DeprecationWarning, for filename, file-object, and string
    inputs.

    Its replacement, FitRecipe.initialize_recipe_with_results, is
    exercised in test_fitrecipe.py.
    """
    recipe = FitRecipe("recipe")
    recipe.create_new_variable("A", 0)
    recipe.create_new_variable("sig", 0)
    recipe.create_new_variable("x0", 0)
    filename = datafile("results.res")
    Aval = 5.77619823e-01
    sigval = -9.22758690e-01
    x0val = 6.12422115e00

    with pytest.deprecated_call():
        initializeRecipe(recipe, as_input(filename))
    assert Aval == pytest.approx(recipe.A.value)
    assert sigval == pytest.approx(recipe.sig.value)
    assert x0val == pytest.approx(recipe.x0.value)
    return


if __name__ == "__main__":

    unittest.main()
