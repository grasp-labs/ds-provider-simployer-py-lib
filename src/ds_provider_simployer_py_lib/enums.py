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


class ResourceType(StrEnum):
    """
    Constants for Simployer provider.
    """

    SIMPLOYER_LINKED_SERVICE = "ds.resource.linked_service.simployer"
    SIMPLOYER_DATASET = "ds.resource.dataset.simployer"


class SimployerDataProducts(StrEnum):
    """
    Simployer data products available through the HRConnect API.
    Each value matches a key in the ENDPOINTS dictionary in endpoint_info.py,
    which defines the API endpoint and supported methods for that data product.
    The values are used in SimployerDatasetSettings to specify which data product
    to read from or write to.
    Example usage:
        settings = SimployerDatasetSettings(
            data_product=SimployerDataProducts.EMPLOYEES,
            read=ReadSettings(page_size=100)
        )
    """

    ABSENCE_COMMENTS = "absence_comments"
    ABSENCE_LOST_DAYS = "absence_lost_days"
    ABSENCES_BY_UNIT = "absences_by_unit"
    ABSENCE_TYPES = "absence_types"
    CONTACT_ADDRESSES = "contact_addresses"
    CONTACT_ADDRESS = "contact_address"
    CONTACT_ADDRESS_UNIT = "contact_address_unit"
    CONTACT_ELECTRONIC_ADDRESSES = "contact_electronic_addresses"
    CONTACT_ELECTRONIC_ADDRESS = "contact_electronic_address"
    CONTACT_ELECTRONIC_ADDRESS_UNIT = "contact_electronic_address_unit"
    CONTACT_PHONE_NUMBERS = "contact_phone_numbers"
    CONTACT_PHONE_NUMBER = "contact_phone_number"
    CONTACT_PHONE_NUMBER_UNIT = "contact_phone_number_unit"
    DOCUMENTS_PERSONS = "documents_persons"
    EMPLOYEES = "employees"
    EMPLOYEE = "employee"
    EMPLOYMENTS = "employments"
    EMPLOYMENT = "employment"
    EMPLOYMENT_AGREEMENT_GUID = "employment_agreement_guid"
    EMPLOYMENT_SET_TERMINATION_CAUSE = "employment_set_termination_cause"
    EMPLOYMENT_CATEGORIES = "employment_categories"
    EMPLOYMENT_CATEGORY = "employment_category"
    EMPLOYMENT_CONTRACTS = "employment_contracts"
    EMPLOYMENT_CONTRACT = "employment_contract"
    EMPLOYMENT_CONTRACTS_PERSON = "employment_contracts_person"
    EMPLOYMENT_COST_CENTER_DEPARTMENT = "employment_cost_center_department"
    EMPLOYMENT_EMPLOYEE = "employment_employee"
    EMPLOYMENT_PERSON = "employment_person"
    EMPLOYMENT_SALARIES = "employment_salaries"
    EMPLOYMENT_SALARIES_EMPLOYMENT = "employment_salaries_employment"
    EMPLOYMENT_SALARIES_PERSON = "employment_salaries_person"
    EMPLOYMENT_TERMINATION_CAUSES = "employment_termination_causes"
    EMPLOYMENT_TERMINATION_CAUSE = "employment_termination_cause"
    EXTENDED_PROPERTY_TYPES = "extended_property_types"
    EXTENDED_PROPERTY_TYPE = "extended_property_type"
    EXTENDED_PROPERTY_TYPE_VALUES = "extended_property_type_values"
    EXTENDED_PROPERTY_TYPE_VALUE = "extended_property_type_value"
    LEAVE_PERIODS = "leave_periods"
    ORGANIZATIONS = "organizations"
    ORGANIZATION = "organization"
    ORGANIZATION_GROUPS = "organization_groups"
    ORGANIZATION_GROUP = "organization_group"
    ORGANIZATION_GROUP_AFFILIATED_PEOPLE = "organization_group_affiliated_people"
    ORGANIZATION_GROUPS_AFFILIATED_PEOPLE = "organization_groups_affiliated_people"
    ORGANIZATION_GROUPS_CATEGORIES = "organization_groups_categories"
    ORGANIZATION_GROUPS_CATEGORY = "organization_groups_category"
    ORGANIZATION_GROUPS_PERSON = "organization_groups_person"
    ORGANIZATION_HIERARCHY = "organization_hierarchy"
    PERSONS = "persons"
    PERSON = "person"
    PERSON_IDENTITY_IDENTIFIERS = "person_identity_identifiers"
    PERSON_CHILDREN = "person_children"
    PERSON_EXTENDED_PROPERTIES = "person_extended_properties"
    PERSON_NEXT_OF_KIN = "person_next_of_kin"
    PERSON_SPECIFIED_MANAGER = "person_specified_manager"
    PERSONS_IDENTITY_IDENTIFIERS = "persons_identity_identifiers"
    PERSONS_IDENTITY_IDENTIFIER = "persons_identity_identifier"
    PERSONS_AUDIT_LOGS = "persons_audit_logs"
    PERSONS_CHILDREN = "persons_children"
    PERSONS_CHILD = "persons_child"
    PERSONS_EXTENDED_PROPERTIES = "persons_extended_properties"
    PERSONS_EXTENDED_PROPERTY = "persons_extended_property"
    PERSONS_EXTENDED_PROPERTIES_TYPE = "persons_extended_properties_type"
    PERSONS_MANAGER_STRUCTURE = "persons_manager_structure"
    PERSONS_NEXT_OF_KIN = "persons_next_of_kin"
    PERSONS_NEXT_OF_KIN_ID = "persons_next_of_kin_id"
    SICK_LEAVE_PERIODS = "sick_leave_periods"
    TENANTS = "tenants"
    TENANTS_PERSON_USERS = "tenants_person_users"
    TENANTS_USERS = "tenants_users"
    TENANTS_USER = "tenants_user"
    VACATION_DAYS = "vacation_days"
    VACATION_PERIODS = "vacation_periods"
