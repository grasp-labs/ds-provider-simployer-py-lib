"""
**File:** ``enums.py``
**Region:** ``ds_provider_simployer_py_lib/enums``

Constants for Simployer provider.

Example:
    >>> ResourceType.SIMPLOYER_LINKED_SERVICE
    'ds.resource.linked_service.simployer'
    >>> ResourceType.SIMPLOYER_DATASET
    'ds.resource.dataset.simployer'
    >>> SimployerDataProducts.EMPLOYEES
    'employees'
"""

from enum import StrEnum
from typing import cast


class ResourceType(StrEnum):
    """
    Constants for Simployer provider.
    """

    SIMPLOYER_LINKED_SERVICE = "ds.resource.linked_service.simployer"
    SIMPLOYER_DATASET = "ds.resource.dataset.simployer"


class SimployerDataProducts(StrEnum):
    """
    Simployer data products available through the HRConnect API.

    These represent the main data categories you can query from Simployer.
    Each product has its own endpoint at https://hrconnect.simployer.com/v1/{product_name}

    Reference: https://hrconnect.simployer.com/index.html
    """

    ABSENCE = "absence"
    """Absence records and absence types."""

    ABSENCE_TYPES = "absenceTypes"
    """Types of absences (e.g., vacation, sick leave)."""

    ADDRESSES = "addresses"
    """Addresses (paginated)."""

    CONTACTS = "contacts"
    """Contact information (addresses, electronic addresses)."""

    DOCUMENTS = "documents"
    """Person documents."""

    DOCUMENTS_PERSONS = "documentsPersons"
    """Documents for persons (paginated)."""

    ELECTRONIC_ADDRESSES = "electronicAddresses"
    """Electronic addresses (paginated)."""

    EMPLOYEES = "employees"
    """Employee master data."""

    EMPLOYMENTS = "employments"
    """Employment records and contracts."""

    EMPLOYMENTS_CATEGORIES = "employmentsCategories"
    """Employment categories (paginated)."""

    EMPLOYMENTS_CONTRACTS = "employmentsContracts"
    """Employment contracts (paginated)."""

    EXTENDED_PROPERTY_TYPES = "extendedPropertyTypes"
    """Extended property types and values."""

    EXTENDED_PROPERTY_TYPES_VALUES = "extendedPropertyTypesValues"
    """Extended property type values."""

    LEAVE = "leave"
    """Leave periods."""

    LEAVE_PERIODS = "leavePeriods"
    """Leave periods (paginated)."""

    ORGANIZATIONS = "organizations"
    """Organizations, groups, and hierarchy structure."""

    ORGANIZATIONS_GROUPS = "organizationsGroups"
    """Groups (paginated)."""

    ORGANIZATIONS_GROUPS_AFFILIATED_PEOPLE = "organizationsGroupsAffiliatedPeople"
    """Group-people relations (paginated)."""

    ORGANIZATIONS_GROUPS_CATEGORIES = "organizationsGroupsCategories"
    """Group categories (paginated)."""

    ORGANIZATIONS_HIERARCHY = "organizationsHierarchy"
    """Organization hierarchy."""

    PERSONS = "persons"
    """Person records and related data (children, next of kin, manager structure)."""

    PERSONS_AUDIT_LOGS = "personsAuditLogs"
    """Audit logs for personal data."""

    PERSONS_CHILDREN = "personsChildren"
    """Children (paginated)."""

    PERSONS_EXTENDED_PROPERTIES = "personsExtendedProperties"
    """Extended properties (paginated)."""

    PERSONS_IDENTITY_IDENTIFIERS = "personsIdentityIdentifiers"
    """Identity identifiers (paginated)."""

    SICK_LEAVE = "sickLeave"
    """Sick leave periods."""

    SICK_LEAVE_PERIODS = "sickLeavePeriods"
    """Sick leave periods (paginated)."""

    TENANTS = "tenants"
    """Tenant and user account information."""

    TENANTS_USERS = "tenantsUsers"
    """User accounts for a tenant (paginated)."""

    VACATION = "vacation"
    """Vacation days and vacation periods."""

    VACATION_DAYS = "vacationDays"
    """Remaining vacation days for a person for a year."""

    VACATION_PERIODS = "vacationPeriods"
    """Vacation periods (paginated)."""


# Extended endpoint info mapping: includes URL and supported HTTP methods
_ENDPOINT_INFO = {
    SimployerDataProducts.ABSENCE: {"url": "/v1/absence", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.ABSENCE_TYPES: {
        "url": "/v1/absence/absencetypes",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.ADDRESSES: {"url": "/v1/contacts/addresses", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.CONTACTS: {"url": "/v1/contacts", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.DOCUMENTS: {"url": "/v1/documents/persons", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.DOCUMENTS_PERSONS: {
        "url": "/v1/documents/persons",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.ELECTRONIC_ADDRESSES: {
        "url": "/v1/contacts/electronicAddresses",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.EMPLOYEES: {"url": "/v1/employees", "methods": {"GET": True, "POST": True, "DELETE": False}},
    SimployerDataProducts.EMPLOYMENTS: {"url": "/v1/employments", "methods": {"GET": True, "POST": True, "DELETE": False}},
    SimployerDataProducts.EMPLOYMENTS_CATEGORIES: {
        "url": "/v1/employments/categories",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.EMPLOYMENTS_CONTRACTS: {
        "url": "/v1/employments/contracts",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.EXTENDED_PROPERTY_TYPES: {
        "url": "/v1/extendedPropertyTypes",
        "methods": {"GET": True, "POST": True, "DELETE": False},
    },
    SimployerDataProducts.EXTENDED_PROPERTY_TYPES_VALUES: {
        "url": "/v1/extendedPropertyTypes/values",
        "methods": {"GET": True, "POST": True, "DELETE": False},
    },
    SimployerDataProducts.LEAVE: {"url": "/v1/leave", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.LEAVE_PERIODS: {
        "url": "/v1/leave/leaveperiods",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.ORGANIZATIONS: {"url": "/v1/organizations", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.ORGANIZATIONS_GROUPS: {
        "url": "/v1/organizations/groups",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.ORGANIZATIONS_GROUPS_AFFILIATED_PEOPLE: {
        "url": "/v1/organizations/groups/affiliatedPeople",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.ORGANIZATIONS_GROUPS_CATEGORIES: {
        "url": "/v1/organizations/groups/categories",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.ORGANIZATIONS_HIERARCHY: {
        "url": "/v1/organizations/hierarchy",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.PERSONS: {"url": "/v1/persons", "methods": {"GET": True, "POST": True, "DELETE": False}},
    SimployerDataProducts.PERSONS_AUDIT_LOGS: {
        "url": "/v1/persons/auditLogs",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.PERSONS_CHILDREN: {
        "url": "/v1/persons/children",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.PERSONS_EXTENDED_PROPERTIES: {
        "url": "/v1/persons/extendedProperties",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.PERSONS_IDENTITY_IDENTIFIERS: {
        "url": "/v1/persons/identityIdentifiers",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.SICK_LEAVE: {"url": "/v1/sickLeave", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.SICK_LEAVE_PERIODS: {
        "url": "/v1/sickLeave/sickleaveperiods",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.TENANTS: {"url": "/v1/tenants", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.TENANTS_USERS: {"url": "/v1/tenants/users", "methods": {"GET": True, "POST": True, "DELETE": False}},
    SimployerDataProducts.VACATION: {"url": "/v1/vacation", "methods": {"GET": True, "POST": False, "DELETE": False}},
    SimployerDataProducts.VACATION_DAYS: {
        "url": "/v1/vacation/vacationdays",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
    SimployerDataProducts.VACATION_PERIODS: {
        "url": "/v1/vacation/vacationperiods",
        "methods": {"GET": True, "POST": False, "DELETE": False},
    },
}


def get_endpoint_for_product(data_product: SimployerDataProducts) -> str | None:
    """
    Returns the main endpoint URL for a given SimployerDataProducts value.
    """
    info = _ENDPOINT_INFO.get(data_product)
    return str(info["url"]) if info else None


def get_supported_methods_for_product(data_product: SimployerDataProducts) -> dict[str, bool] | None:
    """
    Returns supported HTTP methods for a given SimployerDataProducts value.
    Example: {"GET": True, "POST": False, "DELETE": False}
    """
    info = _ENDPOINT_INFO.get(data_product)
    return cast("dict[str, bool] | None", info["methods"] if info else None)


def supports_method(data_product: SimployerDataProducts, method: str) -> bool:
    methods = get_supported_methods_for_product(data_product)
    return bool(methods and methods.get(method.upper()))


def get_methods_for_product(data_product: SimployerDataProducts) -> list[str]:
    """
    Returns a list of supported HTTP methods for a given SimployerDataProducts value.
    Example: ["GET", "POST", "DELETE"]
    """
    methods_dict = get_supported_methods_for_product(data_product)
    methods = list(methods_dict.keys()) if methods_dict else []
    return methods
