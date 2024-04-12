from __future__ import annotations

import dataclasses
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, NamedTuple, Optional, Set


@dataclass(repr=True, frozen=True)
class SessionDetails:
    id: str
    name: str
    instance_id: str
    memory: str  # TODO parse session size?
    status: str
    host: Optional[str]  # TODO non-optional once dns based routing
    expiry_date: Optional[str]  # TODO parse time into datetime using dateutil?
    created_at: str  # TODO parse time into datetime using dateutil?

    @classmethod
    def fromJson(cls, json: dict[str, Any]) -> SessionDetails:
        return cls(
            id=json["id"],
            name=json["name"],
            instance_id=json["instance_id"],
            memory=json["memory"],
            status=json["status"],
            host=json.get("host"),
            expiry_date=json.get("expiry_date"),
            created_at=json["created_at"],
        )


@dataclass(repr=True, frozen=True)
class InstanceDetails:
    id: str
    name: str
    tenant_id: str
    cloud_provider: str

    @classmethod
    def fromJson(cls, json: dict[str, Any]) -> InstanceDetails:
        return cls(
            id=json["id"],
            name=json["name"],
            tenant_id=json["tenant_id"],
            cloud_provider=json["cloud_provider"],
        )


@dataclass(repr=True, frozen=True)
class InstanceSpecificDetails(InstanceDetails):
    status: str
    connection_url: str
    memory: str
    type: str
    region: str

    @classmethod
    def fromJson(cls, json: dict[str, Any]) -> InstanceSpecificDetails:
        return cls(
            id=json["id"],
            name=json["name"],
            tenant_id=json["tenant_id"],
            cloud_provider=json["cloud_provider"],
            status=json["status"],
            connection_url=json.get("connection_url", ""),
            memory=json.get("memory", ""),
            type=json["type"],
            region=json["region"],
        )


@dataclass(repr=True, frozen=True)
class InstanceCreateDetails:
    id: str
    username: str
    password: str
    connection_url: str

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> InstanceCreateDetails:
        fields = dataclasses.fields(cls)
        if any(f.name not in json for f in fields):
            raise RuntimeError(f"Missing required field. Expected `{[f.name for f in fields]}` but got `{json}`")

        return cls(**{f.name: json[f.name] for f in fields})


@dataclass(repr=True, frozen=True)
class EstimationDetails:
    min_required_memory: str
    recommended_size: str
    did_exceed_maximum: bool

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> EstimationDetails:
        fields = dataclasses.fields(cls)
        if any(f.name not in json for f in fields):
            raise RuntimeError(f"Missing required field. Expected `{[f.name for f in fields]}` but got `{json}`")

        return cls(**{f.name: json[f.name] for f in fields})


class WaitResult(NamedTuple):
    connection_url: str
    error: str

    @classmethod
    def from_error(cls, error: str) -> WaitResult:
        return cls(connection_url="", error=error)

    @classmethod
    def from_connection_url(cls, connection_url: str) -> WaitResult:
        return cls(connection_url=connection_url, error="")


@dataclass(repr=True, frozen=True)
class TenantDetails:
    id: str
    ds_type: str
    regions_per_provider: dict[str, Set[str]]

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> TenantDetails:
        regions_per_provider = defaultdict(set)
        instance_types = set()
        ds_type = None

        for configs in json["instance_configurations"]:
            type = configs["type"]
            if type.split("-")[1] == "ds":
                regions_per_provider[configs["cloud_provider"]].add(configs["region"])
                ds_type = type
            instance_types.add(configs["type"])

        id = json["id"]
        if not ds_type:
            raise RuntimeError(
                f"Tenant with id `{id}` cannot create DS instances. Available instances are `{instance_types}`."
            )

        return cls(
            id=id,
            ds_type=ds_type,
            regions_per_provider=regions_per_provider,
        )
