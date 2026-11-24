#!/usr/bin/env python3
"""Tests for main.py: the entry line and the command line interface.

Pure standard library (unittest + subprocess). Run with:
    python3 test_main.py
"""

import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as entry_module


class TestEntryLine(unittest.TestCase):
    def test_line_is_nonempty_single_line(self):
        self.assertTrue(entry_module.LINE.strip(), "entry line is empty")
        self.assertNotIn("\n", entry_module.LINE)
        self.assertNotIn("\r", entry_module.LINE)

    def test_line_within_gate(self):
        # The gate accepts 1 to 200 characters of UTF-8 text.
        self.assertGreaterEqual(len(entry_module.LINE), 1)
        self.assertLessEqual(len(entry_module.LINE), 200)
        entry_module.LINE.encode("utf-8")

    def test_line_names_a_daily_gadget(self):
        self.assertIn("smartwatch", entry_module.LINE.lower())

    def test_line_names_a_concrete_behaviour(self):
        # A concrete, specific gripe: congratulates standing, dies by lunch.
        self.assertIn("standing", entry_module.LINE.lower())
        self.assertIn("lunch", entry_module.LINE.lower())

    def test_line_has_a_punch(self):
        # The punch lands in the last few words.
        self.assertIn("houseplant", entry_module.LINE.lower())


def run_cli(env=None):
    full_env = dict(os.environ)
    full_env.pop("MAKEFUN_OUTPUT_DIR", None)
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, "main.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True, text=True, env=full_env, timeout=30,
    )


class TestCli(unittest.TestCase):
    def test_run_prints_line_and_writes_entry_txt(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(env={"MAKEFUN_OUTPUT_DIR": tmp})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), entry_module.LINE)
            with open(os.path.join(tmp, "entry.txt"), encoding="utf-8") as handle:
                self.assertEqual(handle.read(), entry_module.LINE + "\n")

    def test_run_is_deterministic(self):
        first = run_cli()
        second = run_cli()
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)

    def test_output_is_valid_gate_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(env={"MAKEFUN_OUTPUT_DIR": tmp})
            self.assertEqual(result.returncode, 0, result.stderr)
            with open(os.path.join(tmp, "entry.txt"), "rb") as handle:
                raw = handle.read()
            text = raw.decode("utf-8")
            self.assertTrue(1 <= len(text.rstrip("\n")) <= 200)
            self.assertTrue(text.rstrip("\n").strip())


class TestValidateLine(unittest.TestCase):
    def test_accepts_the_entry_line(self):
        self.assertEqual(entry_module.validate_line(entry_module.LINE),
                         entry_module.LINE)

    def test_rejects_empty_line(self):
        with self.assertRaises(ValueError):
            entry_module.validate_line("   ")

    def test_rejects_multiline(self):
        with self.assertRaises(ValueError):
            entry_module.validate_line("first line\nsecond line")

    def test_rejects_too_long(self):
        with self.assertRaises(ValueError):
            entry_module.validate_line("x" * 201)

    def test_rejects_missing_gadget_words(self):
        with self.assertRaises(ValueError):
            entry_module.validate_line("My toaster is slow today.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
