**Added:**

Claude's summary:

Done. Applied the shim-test pattern across 9 test files: -402/+310 lines, tests went 171 → 172, and spurious deprecation warnings dropped 148 → 104. Full suite passes, flake8/black/isort clean.

What I did per deprecated function:

Kept the exhaustive behavioral coverage on the new API only.
Replaced each duplicated old-name test with a thin shim asserting two things: it emits DeprecationWarning (via pytest.deprecated_call() / assertWarns) and it returns the same result as the replacement.
Fixed ~20 stray calls to deprecated names scattered inside new-API tests (e.g. recipe.isFree, fc.setProfile, self.m.registerStringFunction, equationFromString) — these were silently exercising the old path and generating most of the warning noise.
Consolidated the three testInitializeFrom{FileName,FileObj,String} tests into one parametrized deprecation test.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
