"""
Endpoint information for Simployer data products.
This module centralizes endpoint URLs and supported HTTP methods.
"""

from .enums import SimployerDataProducts


class EndpointInfo:
    def __init__(
        self,
        name: str,
        url: str,
        methods: list[str],
        description: str | None = None,
    ) -> None:
        self.name = name
        self.url = url
        # Normalize methods to uppercase for consistency
        self.methods = [m.upper() for m in methods]
        self.description = description

    @staticmethod
    def get_endpoint_for_product(data_product: SimployerDataProducts) -> str | None:
        """
        Returns the endpoint URL for a given SimployerDataProducts value.
        If the data product is not found, returns None.

        :param data_product: The SimployerDataProducts enum value for which to retrieve the endpoint URL.
        :return: The endpoint URL as a string if found, otherwise None.
        """
        info = ENDPOINTS.get(data_product.value)
        return str(info.url) if info else None

    @staticmethod
    def supports_method(data_product: SimployerDataProducts, method: str) -> bool:
        """
        Returns True if the given HTTP method is supported for the specified SimployerDataProducts value, False otherwise.
        If the data product is not found, returns False.
        :param data_product: The SimployerDataProducts enum value for which to check method support.
        :param method: The HTTP method to check (e.g., "GET", "POST", "PUT", "DELETE").
        :return: True if the method is supported for the data product, False otherwise.
        """
        info = ENDPOINTS.get(data_product.value)
        return method.upper() in info.methods if info else False


ENDPOINTS = {
    "absence_comments": EndpointInfo(
        name="Absence Comments", url="/v1/absence/{id}/comments", methods=["GET"], description="Retrieves comments for an absence."
    ),
    "absence_lost_days": EndpointInfo(
        name="Absence Lost Days",
        url="/v1/absence/{id}/lostdays",
        methods=["GET"],
        description="Retrieves lost days for an absence.",
    ),
    "absences_by_unit": EndpointInfo(
        name="Absences by Unit",
        url="/v1/absence/absences/{organizationUnitId}",
        methods=["GET"],
        description="Retrieves absences in period with pagination.",
    ),
    "absence_types": EndpointInfo(
        name="Absence Types",
        url="/v1/absence/absencetypes",
        methods=["GET"],
        description="Retrieves all absence types with pagination.",
    ),
    "contact_addresses": EndpointInfo(
        name="Contact Addresses", url="/v1/contacts/addresses", methods=["GET"], description="Retrieves addresses with pagination."
    ),
    "contact_address": EndpointInfo(
        name="Contact Address",
        url="/v1/contacts/addresses/{id}",
        methods=["GET", "DELETE", "PUT"],
        description="Retrieves, deletes, or updates an address.",
    ),
    "contact_address_unit": EndpointInfo(
        name="Get Addresses for Unit",
        url="/v1/contacts/addresses/unit/{id}",
        methods=["GET", "POST"],
        description="Retrieves addresses for unit.",
    ),
    "contact_electronic_addresses": EndpointInfo(
        name="Electronic Addresses",
        url="/v1/contacts/electronicAddresses",
        methods=["GET"],
        description="Retrieves electronic addresses with pagination.",
    ),
    "contact_electronic_address": EndpointInfo(
        name="Electronic Address",
        url="/v1/contacts/electronicAddresses/{id}",
        methods=["GET", "DELETE", "PUT"],
        description="Retrieves, deletes, or updates an electronic address with the specified ID.",
    ),
    "contact_electronic_address_unit": EndpointInfo(
        name="Get Electronic Addresses for Unit",
        url="/v1/contacts/electronicAddresses/unit/{id}",
        methods=["GET", "POST"],
        description="Retrieves electronic addresses for unit.",
    ),
    "contact_phone_numbers": EndpointInfo(
        name="Phone Numbers",
        url="/v1/contacts/phoneNumbers",
        methods=["GET"],
        description="Retrieves phone numbers with pagination.",
    ),
    "contact_phone_number": EndpointInfo(
        name="Phone Number",
        url="/v1/contacts/phoneNumbers/{id}",
        methods=["GET", "DELETE", "PUT"],
        description="Retrieves, deletes, or updates a phone number with the specified ID.",
    ),
    "contact_phone_number_unit": EndpointInfo(
        name="Phone Numbers for Unit",
        url="/v1/contacts/phoneNumbers/unit/{id}",
        methods=["GET", "POST"],
        description="Retrieves or creates phone numbers for unit.",
    ),
    "documents_persons": EndpointInfo(
        name="Documents for Persons",
        url="/v1/documents/persons",
        methods=["GET"],
        description="Retrieves documents for persons with pagination.",
    ),
    "employees": EndpointInfo(
        name="Employees",
        url="/v1/employees",
        methods=["GET", "POST"],
        description=("GET: Retrieves employees with pagination. POST: Creates a new employee."),
    ),
    "employee": EndpointInfo(
        name="Employee",
        url="/v1/employees/{id}",
        methods=["PUT", "DELETE"],
        description=("Sets the termination cause for an employment."),
    ),
    "employments": EndpointInfo(
        name="Employments",
        url="/v1/employments",
        methods=["GET", "POST"],
        description=("GET: Retrieves employments with pagination. POST: Creates a new employment."),
    ),
    "employment": EndpointInfo(
        name="Employment",
        url="/v1/employments/{id}",
        methods=["GET", "PUT", "DELETE"],
        description=(
            "GET: Retrieves employment by ID. "
            "PUT: Updates an existing employment. "
            "DELETE: Deletes an employment with the specified identifier."
        ),
    ),
    "employment_agreement_guid": EndpointInfo(
        name="Employment Agreement GUID",
        url="/v1/employments/{id}/agreementGuid",
        methods=["GET"],
        description="Retrieves the agreement GUID for an employment.",
    ),
    "employment_set_termination_cause": EndpointInfo(
        name="Set Employment Termination Cause",
        url="/v1/employments/{id}/setTerminationCause",
        methods=["PATCH"],
        description="Sets the termination cause for an employment.",
    ),
    "employment_categories": EndpointInfo(
        name="Employment Categories",
        url="/v1/employments/categories",
        methods=["GET"],
        description="Retrieves employment categories with pagination.",
    ),
    "employment_category": EndpointInfo(
        name="Employment Category",
        url="/v1/employments/categories/{id}",
        methods=["GET"],
        description="Retrieves employment category with given identifier.",
    ),
    "employment_contracts": EndpointInfo(
        name="Employment Contracts",
        url="/v1/employments/contracts",
        methods=["GET"],
        description="Retrieves contracts with pagination.",
    ),
    "employment_contract": EndpointInfo(
        name="Employment Contract",
        url="/v1/employments/contracts/{id}",
        methods=["GET"],
        description="Retrieves the contract with given identifier.",
    ),
    "employment_contracts_person": EndpointInfo(
        name="Employment Contracts for Person",
        url="/v1/employments/contracts/person/{id}",
        methods=["GET"],
        description="Retrieves the contracts associated with person.",
    ),
    "employment_cost_center_department": EndpointInfo(
        name="Employment Cost Centers for Department",
        url="/v1/employments/costCenter/department/{id}",
        methods=["GET"],
        description="Retrieves cost centers for a department.",
    ),
    "employment_employee": EndpointInfo(
        name="Employments for Employee",
        url="/v1/employments/employee/{id}",
        methods=["GET"],
        description="Retrieves employments for given employee.",
    ),
    "employment_person": EndpointInfo(
        name="Employments for Person",
        url="/v1/employments/person/{id}",
        methods=["GET"],
        description="Retrieves employments for given person.",
    ),
    "employment_salaries": EndpointInfo(
        name="Employment Salaries",
        url="/v1/employments/salaries",
        methods=["GET"],
        description="Retrieves salaries with pagination.",
    ),
    "employment_salaries_employment": EndpointInfo(
        name="Employment Salary",
        url="/v1/employments/salaries/employment/{id}",
        methods=["GET"],
        description="Retrieves salary for given employment.",
    ),
    "employment_salaries_person": EndpointInfo(
        name="Employment Salaries for Person",
        url="/v1/employments/salaries/person/{id}",
        methods=["GET"],
        description="Retrieves salaries for given person.",
    ),
    "employment_termination_causes": EndpointInfo(
        name="Employment Termination Causes",
        url="/v1/employments/terminationCauses",
        methods=["GET"],
        description="Retrieves termination causes with pagination.",
    ),
    "employment_termination_cause": EndpointInfo(
        name="Employment Termination Cause",
        url="/v1/employments/terminationCauses/{id}",
        methods=["GET"],
        description="Retrieves termination cause with given identifier.",
    ),
    "extended_property_types": EndpointInfo(
        name="Extended Property Types",
        url="/v1/extendedPropertyTypes",
        methods=["GET", "POST"],
        description="GET: Retrieves extended property types with pagination. POST: Creates extended property type.",
    ),
    "extended_property_type": EndpointInfo(
        name="Extended Property Type",
        url="/v1/extendedPropertyTypes/{id}",
        methods=["GET", "PUT", "DELETE"],
        description=(
            "GET: Retrieves extended property type by ID. "
            "PUT: Updates extended property type. "
            "DELETE: Deletes extended property type."
        ),
    ),
    "extended_property_type_values": EndpointInfo(
        name="Extended Property Type Values",
        url="/v1/extendedPropertyTypes/values",
        methods=["POST"],
        description="Creates extended property type value.",
    ),
    "extended_property_type_value": EndpointInfo(
        name="Extended Property Type Value",
        url="/v1/extendedPropertyTypes/values/{id}",
        methods=["PUT", "DELETE"],
        description="PUT: Updates extended property type value. DELETE: Deletes extended property type value.",
    ),
    "leave_periods": EndpointInfo(
        name="Leave Periods",
        url="/v1/leave/leaveperiods",
        methods=["GET"],
        description="Retrieves leave periods in period, with pagination.",
    ),
    "organizations": EndpointInfo(
        name="Organizations", url="/v1/organizations", methods=["GET"], description="Retrieves organizations with pagination."
    ),
    "organization": EndpointInfo(
        name="Organization",
        url="/v1/organizations/{id}",
        methods=["GET"],
        description="Retrieves an organization with given identifier.",
    ),
    "organization_groups": EndpointInfo(
        name="Organization Groups",
        url="/v1/organizations/groups",
        methods=["GET"],
        description="Retrieves groups with pagination.",
    ),
    "organization_group": EndpointInfo(
        name="Organization Group",
        url="/v1/organizations/groups/{id}",
        methods=["GET"],
        description="Retrieves a group with given identifier.",
    ),
    "organization_group_affiliated_people": EndpointInfo(
        name="Group-Affiliated People",
        url="/v1/organizations/groups/{id}/affiliatedPeople",
        methods=["GET"],
        description="Retrieves group-people relation for given group.",
    ),
    "organization_groups_affiliated_people": EndpointInfo(
        name="Groups-Affiliated People",
        url="/v1/organizations/groups/affiliatedPeople",
        methods=["GET"],
        description="Retrieves group-people relations with pagination.",
    ),
    "organization_groups_categories": EndpointInfo(
        name="Group Categories",
        url="/v1/organizations/groups/categories",
        methods=["GET"],
        description="Retrieves group categories with pagination.",
    ),
    "organization_groups_category": EndpointInfo(
        name="Group Category",
        url="/v1/organizations/groups/categories/{id}",
        methods=["GET"],
        description="Retrieves group category with given identifier.",
    ),
    "organization_groups_person": EndpointInfo(
        name="Groups for Person",
        url="/v1/organizations/groups/person/{id}",
        methods=["GET"],
        description="Retrieves groups identifiers where given person affiliates.",
    ),
    "organization_hierarchy": EndpointInfo(
        name="Organization Hierarchy",
        url="/v1/organizations/hierarchy",
        methods=["GET"],
        description="Retrieves the organizational hierarchy.",
    ),
    "persons": EndpointInfo(
        name="Persons",
        url="/v1/persons",
        methods=["GET", "POST"],
        description="GET: Retrieves a paginated list of people. POST: Creates a new person.",
    ),
    "person": EndpointInfo(
        name="Person",
        url="/v1/persons/{id}",
        methods=["GET", "PATCH", "DELETE"],
        description=(
            "GET: Retrieves person by ID. PATCH: Updates an existing person. DELETE: Deletes a person (must be deactivated first)."
        ),
    ),
    "person_identity_identifiers": EndpointInfo(
        name="Identity Identifiers for Person",
        url="/v1/persons/{id}/identityIdentifiers",
        methods=["GET", "POST"],
        description="GET: Retrieves identity identifiers for given person. POST: Creates a new identity identifier for a person.",
    ),
    "person_children": EndpointInfo(
        name="Children for Person",
        url="/v1/persons/{id}/children",
        methods=["GET", "POST"],
        description="GET: Retrieves children for person. POST: Creates a new child for a person.",
    ),
    "person_extended_properties": EndpointInfo(
        name="Extended Properties for Person",
        url="/v1/persons/{id}/extendedProperties",
        methods=["GET", "POST"],
        description="GET: Retrieves extended properties for person. POST: Creates a new extended property for a person.",
    ),
    "person_next_of_kin": EndpointInfo(
        name="Next of Kin for Person",
        url="/v1/persons/{id}/nextOfKin",
        methods=["GET", "POST"],
        description="GET: Retrieves next of kin for person. POST: Creates a new next of kin for a person.",
    ),
    "person_specified_manager": EndpointInfo(
        name="Specified Manager for Person",
        url="/v1/persons/{id}/specifiedManager",
        methods=["PUT", "DELETE"],
        description=(
            "PUT: Overrides the default manager assigned at the organization level. "
            "DELETE: Removes the specified manager override, reverting to the default manager."
        ),
    ),
    "persons_identity_identifiers": EndpointInfo(
        name="Identity Identifiers",
        url="/v1/persons/identityIdentifiers",
        methods=["GET"],
        description="Retrieves identity identifiers.",
    ),
    "persons_identity_identifier": EndpointInfo(
        name="Identity Identifier",
        url="/v1/persons/identityIdentifiers/{id}",
        methods=["GET", "DELETE", "PUT"],
        description=(
            "GET: Retrieves identity identifier by ID. DELETE: Deletes identity identifier. PUT: Updates identity identifier."
        ),
    ),
    "persons_audit_logs": EndpointInfo(
        name="Audit Logs", url="/v1/persons/auditLogs", methods=["GET"], description="Retrieves audit logs for personal data."
    ),
    "persons_children": EndpointInfo(
        name="Children", url="/v1/persons/children", methods=["GET"], description="Retrieves children."
    ),
    "persons_child": EndpointInfo(
        name="Child",
        url="/v1/persons/children/{id}",
        methods=["GET", "PUT"],
        description="GET: Retrieves child. PUT: Updates an existing child for a person.",
    ),
    "persons_extended_properties": EndpointInfo(
        name="Extended Properties",
        url="/v1/persons/extendedProperties",
        methods=["GET"],
        description="Retrieves extended properties.",
    ),
    "persons_extended_property": EndpointInfo(
        name="Extended Property",
        url="/v1/persons/extendedProperties/{id}",
        methods=["GET", "DELETE"],
        description="GET: Retrieves extended property by ID. DELETE: Deletes extended property.",
    ),
    "persons_extended_properties_type": EndpointInfo(
        name="Extended Properties by Type",
        url="/v1/persons/extendedProperties/type/{id}",
        methods=["GET"],
        description="Retrieves extended properties with given type identifier.",
    ),
    "persons_manager_structure": EndpointInfo(
        name="Manager Structure",
        url="/v1/persons/managerStructure",
        methods=["GET"],
        description="Retrieves the manager structure.",
    ),
    "persons_next_of_kin": EndpointInfo(
        name="Next of Kin", url="/v1/persons/nextOfKin", methods=["GET"], description="Retrieves next of kin."
    ),
    "persons_next_of_kin_id": EndpointInfo(
        name="Next of Kin by ID",
        url="/v1/persons/nextOfKin/{id}",
        methods=["GET", "PUT"],
        description="GET: Retrieves next of kin. PUT: Updates an existing next of kin for a person.",
    ),
    "sick_leave_periods": EndpointInfo(
        name="Sick Leave Periods",
        url="/v1/sickLeave/sickleaveperiods",
        methods=["GET"],
        description="Retrieves sick leave periods in period, with pagination.",
    ),
    "tenants": EndpointInfo(name="Tenants", url="/v1/tenants", methods=["GET"], description="Retrieves the tenant information."),
    "tenants_person_users": EndpointInfo(
        name="Tenant Person Users",
        url="/v1/tenants/person/{personId}/users",
        methods=["GET"],
        description="Retrieves a user account and person ID.",
    ),
    "tenants_users": EndpointInfo(
        name="Tenant Users",
        url="/v1/tenants/users",
        methods=["GET", "POST"],
        description=(
            "GET: Retrieves all user accounts belonging to a specific tenant with pagination. "
            "POST: Creates a new account for person."
        ),
    ),
    "tenants_user": EndpointInfo(
        name="Tenant User",
        url="/v1/tenants/users/{userAccountId}",
        methods=["GET", "DELETE"],
        description=(
            "GET: Retrieves a specific user account by tenant ID and user account ID. DELETE: Deletes user account for person."
        ),
    ),
    "vacation_days": EndpointInfo(
        name="Vacation Days",
        url="/v1/vacation/vacationdays",
        methods=["GET"],
        description="Retrieves remaining vacation days for a person for a given year.",
    ),
    "vacation_periods": EndpointInfo(
        name="Vacation Periods",
        url="/v1/vacation/vacationperiods",
        methods=["GET"],
        description="Retrieves vacations in period with pagination.",
    ),
}
