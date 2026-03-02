"""
**File:** ``enums.py``
**Region:** ``ds_provider_simployer_py_lib/enums``

Constants for Simployer provider.

Example:
    >>> ResourceType.SIMPLOYER_LINKED_SERVICE
    'ds.resource.linked_service.simployer'
    >>> ResourceType.SIMPLOYER_DATASET
    'ds.resource.dataset.simployer'
    >>> SimployerDataProduct.EMPLOYEES
    'employees'
"""

from enum import StrEnum


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


# Helper to get the main endpoint for a selected data product
def get_endpoint_for_product(data_product: SimployerDataProducts) -> str | None:
    """
    Returns the main endpoint URL for a given SimployerDataProducts value.
    """
    endpoints = {
        SimployerDataProducts.ABSENCE: "/v1/absence",
        SimployerDataProducts.ABSENCE_TYPES: "/v1/absence/absencetypes",
        SimployerDataProducts.ADDRESSES: "/v1/contacts/addresses",
        SimployerDataProducts.ELECTRONIC_ADDRESSES: "/v1/contacts/electronicAddresses",
        SimployerDataProducts.DOCUMENTS: "/v1/documents/persons",
        SimployerDataProducts.EMPLOYEES: "/v1/employees",
        SimployerDataProducts.EMPLOYMENTS: "/v1/employments",
        SimployerDataProducts.EMPLOYMENTS_CATEGORIES: "/v1/employments/categories",
        SimployerDataProducts.EMPLOYMENTS_CONTRACTS: "/v1/employments/contracts",
        SimployerDataProducts.EXTENDED_PROPERTY_TYPES: "/v1/extendedPropertyTypes",
        SimployerDataProducts.EXTENDED_PROPERTY_TYPES_VALUES: "/v1/extendedPropertyTypes/values",
        SimployerDataProducts.LEAVE_PERIODS: "/v1/leave/leaveperiods",
        SimployerDataProducts.ORGANIZATIONS: "/v1/organizations",
        SimployerDataProducts.ORGANIZATIONS_GROUPS: "/v1/organizations/groups",
        SimployerDataProducts.ORGANIZATIONS_GROUPS_AFFILIATED_PEOPLE: "/v1/organizations/groups/affiliatedPeople",
        SimployerDataProducts.ORGANIZATIONS_GROUPS_CATEGORIES: "/v1/organizations/groups/categories",
        SimployerDataProducts.ORGANIZATIONS_HIERARCHY: "/v1/organizations/hierarchy",
        SimployerDataProducts.PERSONS: "/v1/persons",
        SimployerDataProducts.PERSONS_IDENTITY_IDENTIFIERS: "/v1/persons/identityIdentifiers",
        SimployerDataProducts.PERSONS_AUDIT_LOGS: "/v1/persons/auditLogs",
        SimployerDataProducts.PERSONS_CHILDREN: "/v1/persons/children",
        SimployerDataProducts.PERSONS_EXTENDED_PROPERTIES: "/v1/persons/extendedProperties",
        SimployerDataProducts.SICK_LEAVE_PERIODS: "/v1/sickLeave/sickleaveperiods",
        SimployerDataProducts.TENANTS: "/v1/tenants",
        SimployerDataProducts.TENANTS_USERS: "/v1/tenants/users",
        SimployerDataProducts.VACATION_DAYS: "/v1/vacation/vacationdays",
        SimployerDataProducts.VACATION_PERIODS: "/v1/vacation/vacationperiods",
    }
    return endpoints.get(data_product)
