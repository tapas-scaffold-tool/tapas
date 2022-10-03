import sys
from subprocess import run, PIPE

from lice.core import LICENSES

from tapas.params import StrEnumParameter
from tapas.tools.common import get_system_param


LICENSE_PARAMETER_ID = get_system_param("license")
LICENSE_NONE_ENUM_VALUE = "none"
LICENSE_ENUM_VALUES = LICENSES + [LICENSE_NONE_ENUM_VALUE]


def generate_license_text(license_type: str):
    if license_type not in LICENSES:
        raise ValueError(f'Unknown license type "{license_type}"')

    proc = run(["lice", license_type], stdout=PIPE, check=True)
    return proc.stdout.decode(sys.stdout.encoding)


def generate_license_file(licence_type: str, file: str = "LICENSE"):
    if not licence_type or licence_type.lower() == "none":
        return

    with open(file, "w") as f:
        f.write(generate_license_text(licence_type))


class LicenseParameter(StrEnumParameter):
    def __init__(self):
        super(LicenseParameter, self).__init__(
            LICENSE_PARAMETER_ID,
            LICENSE_ENUM_VALUES,
            prompt="Choose project license",
            default=LICENSE_NONE_ENUM_VALUE,
        )


TAPAS_SYSTEM_LICENSE_PARAMETER = LicenseParameter()
