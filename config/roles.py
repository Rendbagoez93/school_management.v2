from enum import StrEnum


class RoleEnum(StrEnum):
    ADMIN = "Admin"
    PRINCIPAL = "Principal"
    VP = "Vice Principal"
    TEACHER = "Teacher"
    STAFF = "Staff"
    LIBRARIAN = "Librarian"
    ACT = "Accountant"
    CSLR = "Counselor"
    NURSE = "Nurse"
    RCP = "Receptionist"
    STUDENT = "Student"
    PARENT = "Parent"

    @classmethod
    def to_list(cls):
        """Return a list of all role names."""
        return [role.value for role in cls]

    @classmethod
    def staff_roles(cls):
        """Return a list of roles that are considered staff."""
        not_included = [cls.STUDENT, cls.PARENT, cls.ADMIN]
        return [role.value for role in cls if role not in not_included]

    @classmethod
    def regular_roles(cls):
        """Return a list of roles that are considered regular users."""
        included = [cls.PARENT, cls.STUDENT]
        return [role.value for role in cls if role in included]
    
    
