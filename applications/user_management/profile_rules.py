"""
Profile Rules and Invariants for User Management.

INVARIANT: Can a User have more than one profile type?
Answer: YES, but ONLY for specific role combinations:
    - Teacher ⟷ Staff ✅
    - Teacher ⟷ Counselor ✅

All other profile combinations are PROHIBITED.
"""

from dataclasses import dataclass
from enum import StrEnum

from config.roles import RoleEnum


class ProfileType(StrEnum):
    """Enumeration of all profile types in the system."""
    
    PARENT = "Parent"
    STUDENT = "Student"
    SCHOOL_STAFF = "SchoolStaff"


@dataclass(frozen=True)
class ProfileCombination:
    """Immutable representation of an allowed profile combination."""
    
    profiles: frozenset[ProfileType]
    
    def __post_init__(self):
        if len(self.profiles) == 0:
            raise ValueError("Profile combination must have at least one profile type")
    
    @classmethod
    def single(cls, profile: ProfileType) -> "ProfileCombination":
        """Create a single-profile combination."""
        return cls(profiles=frozenset([profile]))
    
    @classmethod
    def dual(cls, profile1: ProfileType, profile2: ProfileType) -> "ProfileCombination":
        """Create a dual-profile combination."""
        return cls(profiles=frozenset([profile1, profile2]))
    
    def contains(self, profile: ProfileType) -> bool:
        """Check if this combination contains a specific profile type."""
        return profile in self.profiles
    
    def is_compatible_with(self, existing_profiles: set[ProfileType]) -> bool:
        """
        Check if adding this combination is compatible with existing profiles.
        
        Compatible means: existing + new profiles form a valid combination.
        """
        combined = existing_profiles | self.profiles
        return any(
            allowed.profiles == combined
            for allowed in ALLOWED_PROFILE_COMBINATIONS
        )


# Core invariant: Define ALL allowed profile combinations
ALLOWED_PROFILE_COMBINATIONS: list[ProfileCombination] = [
    # Single profiles (standard cases)
    ProfileCombination.single(ProfileType.PARENT),
    ProfileCombination.single(ProfileType.STUDENT),
    ProfileCombination.single(ProfileType.SCHOOL_STAFF),
    
    # Dual profiles (special cases - Teacher can be Staff or Counselor)
    # Note: These represent logical "can be both", not required structures
]


# Role → Required Profile Type Mapping
ROLE_TO_PROFILE_MAP: dict[RoleEnum, ProfileType] = {
    # Staff roles → SchoolStaff profile
    RoleEnum.PRINCIPAL: ProfileType.SCHOOL_STAFF,
    RoleEnum.VP: ProfileType.SCHOOL_STAFF,
    RoleEnum.TEACHER: ProfileType.SCHOOL_STAFF,
    RoleEnum.STAFF: ProfileType.SCHOOL_STAFF,
    RoleEnum.LIBRARIAN: ProfileType.SCHOOL_STAFF,
    RoleEnum.ACT: ProfileType.SCHOOL_STAFF,
    RoleEnum.CSLR: ProfileType.SCHOOL_STAFF,
    RoleEnum.NURSE: ProfileType.SCHOOL_STAFF,
    RoleEnum.RCP: ProfileType.SCHOOL_STAFF,
    
    # Regular roles
    RoleEnum.STUDENT: ProfileType.STUDENT,
    RoleEnum.PARENT: ProfileType.PARENT,
}


# Roles that CAN have multiple profiles (Teacher can also be Staff/Counselor)
MULTI_PROFILE_CAPABLE_ROLES: set[RoleEnum] = {
    RoleEnum.TEACHER,
    RoleEnum.CSLR,  # Counselor
    RoleEnum.STAFF,
}


def get_required_profile_type(role: RoleEnum) -> ProfileType:
    """Get the required profile type for a given role."""
    profile_type = ROLE_TO_PROFILE_MAP.get(role)
    if profile_type is None:
        raise ValueError(f"Role {role.value} has no profile mapping")
    return profile_type


def can_have_multiple_profiles(role: RoleEnum) -> bool:
    """Check if a role can have multiple profiles."""
    return role in MULTI_PROFILE_CAPABLE_ROLES


def validate_profile_combination(profile_types: set[ProfileType]) -> bool:
    """
    Validate if a set of profile types forms an allowed combination.
    
    Args:
        profile_types: Set of profile types to validate
        
    Returns:
        True if the combination is allowed, False otherwise
    """
    if not profile_types:
        return False
    
    # Single profile is always allowed if it's a defined type
    if len(profile_types) == 1:
        return True
    
    # Multiple profiles: Only SchoolStaff can have multiple
    # (Teacher can be Staff+Counselor implicitly via role system)
    # For now, we restrict to single profile per user in profile creation
    return False


def get_allowed_additional_profiles(
    existing_profiles: set[ProfileType],
    role: RoleEnum
) -> set[ProfileType]:
    """
    Get profiles that can be added given existing profiles and role.
    
    Args:
        existing_profiles: Set of existing profile types
        role: User's role
        
    Returns:
        Set of profile types that can be added
    """
    if not can_have_multiple_profiles(role):
        return set()
    
    required_profile = get_required_profile_type(role)
    
    # If user already has the required profile, no additional allowed
    if required_profile in existing_profiles:
        return set()
    
    # Can add the required profile
    return {required_profile}


def validate_role_profile_consistency(
    roles: set[RoleEnum],
    profile_types: set[ProfileType]
) -> tuple[bool, str]:
    """
    Validate that roles and profile types are consistent.
    
    Args:
        roles: Set of user roles
        profile_types: Set of profile types
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not roles:
        return False, "User must have at least one role"
    
    if not profile_types:
        return False, "User must have at least one profile"
    
    # Check each role has its required profile
    required_profiles = {get_required_profile_type(role) for role in roles}
    
    # All required profiles must be present
    missing_profiles = required_profiles - profile_types
    if missing_profiles:
        return False, f"Missing required profiles: {missing_profiles}"
    
    # Check no extra profiles exist
    extra_profiles = profile_types - required_profiles
    if extra_profiles:
        return False, f"User has unauthorized profiles: {extra_profiles}"
    
    # Validate the combination is allowed
    if not validate_profile_combination(profile_types):
        return False, f"Profile combination not allowed: {profile_types}"
    
    return True, ""
