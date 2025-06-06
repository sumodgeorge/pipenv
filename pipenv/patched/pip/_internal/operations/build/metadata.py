"""Metadata generation logic for source distributions."""

import os

from pipenv.patched.pip._vendor.pyproject_hooks import BuildBackendHookCaller

from pipenv.patched.pip._internal.build_env import BuildEnvironment
from pipenv.patched.pip._internal.exceptions import (
    InstallationSubprocessError,
    MetadataGenerationFailed,
)
from pipenv.patched.pip._internal.utils.subprocess import runner_with_spinner_message
from pipenv.patched.pip._internal.utils.temp_dir import TempDirectory


def generate_metadata(
    build_env: BuildEnvironment, backend: BuildBackendHookCaller, details: str
) -> str:
    """Generate metadata using mechanisms described in PEP 517.

    Returns the generated metadata directory.
    """
    metadata_tmpdir = TempDirectory(kind="modern-metadata", globally_managed=True)

    metadata_dir = metadata_tmpdir.path

    with build_env:
        # Note that BuildBackendHookCaller implements a fallback for
        # prepare_metadata_for_build_wheel, so we don't have to
        # consider the possibility that this hook doesn't exist.
        runner = runner_with_spinner_message("Preparing metadata (pyproject.toml)")
        with backend.subprocess_runner(runner):
            try:
                distinfo_dir = backend.prepare_metadata_for_build_wheel(metadata_dir)
            except InstallationSubprocessError as error:
                raise MetadataGenerationFailed(package_details=details) from error

    return os.path.join(metadata_dir, distinfo_dir)
