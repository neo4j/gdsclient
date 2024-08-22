from enum import Enum


class ProtocolVersion(Enum):
    V1 = ("v1",)
    V2 = "v2"

    def versioned_procedure_name(self, procedure_name: str) -> str:
        if self == ProtocolVersion.V1:
            return procedure_name
        else:
            return f"{procedure_name}.{self.value}"

    def supports_endpoint(self, endpoint: str) -> bool:
        if self == ProtocolVersion.V2:
            return endpoint.endswith(".v2")
        else:
            return True


class ProtocolVersions:
    @staticmethod
    def from_str(version_string: str) -> ProtocolVersion:
        if version_string == "v1":
            return ProtocolVersion.V1
        elif version_string == "v2":
            return ProtocolVersion.V2
        else:
            raise ValueError(f"Invalid protocol version: {version_string}")