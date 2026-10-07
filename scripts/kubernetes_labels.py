"""Validate Kubernetes label values, beyond the permissive object JSON schemas."""
import re

LABEL_VALUE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?")


def validate_label_values(labels):
    for key, value in labels.items():
        if not isinstance(value, str) or len(value) > 63 or (value and not LABEL_VALUE.fullmatch(value)):
            raise ValueError(f"Invalid Kubernetes label value for {key}: {value!r}")
