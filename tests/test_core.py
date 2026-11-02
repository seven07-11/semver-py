import unittest

from semver.core import Version, VersionError, compare, parse


class ParseTests(unittest.TestCase):
    def test_basic(self):
        v = parse("1.2.3")
        self.assertEqual(v, Version(1, 2, 3))

    def test_with_prerelease(self):
        v = parse("1.0.0-alpha.1")
        self.assertEqual(v.prerelease, ("alpha", "1"))

    def test_with_build(self):
        v = parse("1.0.0+build.5")
        self.assertEqual(v.build, ("build", "5"))

    def test_full(self):
        v = parse("2.3.4-beta.2+exp.7")
        self.assertEqual(v.major, 2)
        self.assertEqual(v.minor, 3)
        self.assertEqual(v.patch, 4)
        self.assertEqual(v.prerelease, ("beta", "2"))
        self.assertEqual(v.build, ("exp", "7"))

    def test_strips_whitespace(self):
        self.assertEqual(parse("  1.2.3  "), Version(1, 2, 3))

    def test_rejects_leading_zero(self):
        with self.assertRaises(VersionError):
            parse("01.2.3")

    def test_rejects_missing_parts(self):
        with self.assertRaises(VersionError):
            parse("1.2")

    def test_rejects_garbage(self):
        with self.assertRaises(VersionError):
            parse("not-a-version")

    def test_rejects_non_str(self):
        with self.assertRaises(VersionError):
            parse(123)


class CompareTests(unittest.TestCase):
    def test_numeric_parts(self):
        self.assertLess(parse("1.2.3"), parse("1.2.4"))
        self.assertLess(parse("1.2.9"), parse("1.3.0"))
        self.assertLess(parse("1.9.9"), parse("2.0.0"))
        self.assertEqual(parse("1.2.3"), parse("1.2.3"))

    def test_prerelease_lower_than_release(self):
        self.assertLess(parse("1.0.0-alpha"), parse("1.0.0"))

    def test_prerelease_ordering(self):
        self.assertLess(parse("1.0.0-alpha"), parse("1.0.0-alpha.1"))
        self.assertLess(parse("1.0.0-alpha.1"), parse("1.0.0-alpha.beta"))
        self.assertLess(parse("1.0.0-alpha.beta"), parse("1.0.0-beta"))
        self.assertLess(parse("1.0.0-beta"), parse("1.0.0-beta.2"))
        self.assertLess(parse("1.0.0-beta.2"), parse("1.0.0-beta.11"))
        self.assertLess(parse("1.0.0-beta.11"), parse("1.0.0-rc.1"))

    def test_numeric_prerelease_ids(self):
        self.assertLess(parse("1.0.0-1"), parse("1.0.0-2"))
        self.assertLess(parse("1.0.0-2"), parse("1.0.0-10"))

    def test_build_ignored_in_precedence(self):
        a = parse("1.0.0+build.1")
        b = parse("1.0.0+build.2")
        self.assertEqual(compare(a, b), 0)
        self.assertEqual(a, b)

    def test_compare_function(self):
        self.assertEqual(compare(parse("1.0.0"), parse("2.0.0")), -1)
        self.assertEqual(compare(parse("2.0.0"), parse("1.0.0")), 1)
        self.assertEqual(compare(parse("1.0.0"), parse("1.0.0")), 0)


class BumpTests(unittest.TestCase):
    def test_bump_major_resets(self):
        self.assertEqual(parse("1.2.3").bump_major(), Version(2, 0, 0))

    def test_bump_minor_resets_patch(self):
        self.assertEqual(parse("1.2.3").bump_minor(), Version(1, 3, 0))

    def test_bump_patch(self):
        self.assertEqual(parse("1.2.3").bump_patch(), Version(1, 2, 4))

    def test_bump_drops_prerelease(self):
        self.assertEqual(parse("1.2.3-rc.1").bump_patch(), Version(1, 2, 4))

    def test_bump_prerelease_increments(self):
        self.assertEqual(
            parse("1.0.0-alpha.1").bump_prerelease("alpha"),
            Version(1, 0, 0, prerelease=("alpha", "2")),
        )

    def test_bump_prerelease_starts(self):
        self.assertEqual(
            parse("1.0.0").bump_prerelease("alpha"),
            Version(1, 0, 0, prerelease=("alpha", "1")),
        )


class StrTests(unittest.TestCase):
    def test_round_trip(self):
        for s in ["1.2.3", "1.0.0-alpha.1", "2.3.4+build.5", "1.0.0-rc.1+x"]:
            self.assertEqual(str(parse(s)), s)

    def test_is_prerelease(self):
        self.assertTrue(parse("1.0.0-alpha").is_prerelease())
        self.assertFalse(parse("1.0.0").is_prerelease())


if __name__ == "__main__":
    unittest.main()
