PERMISSIONS = [
    'dashboard:view',
    'admin_user:view',
    'admin_user:write',
    'admin_user:delete',
    'role:view',
    'role:write',
    'inspection:view',
    'inspection:write',
    'recycled:view',
    'recycled:write',
    'verified:view',
    'verified:write',
    'verified:read',
    'audit_log:view',
    'payment:view',
    'payment:write',
    'order:ship',
    'category:view',
    'category:write',
    'category:delete',
    'product:view',
    'product:write',
    'product:delete',
    'user:view',
    'user:write',
    'user:delete',
    'message:view',
    'message:delete',
    'address:view',
    'address:delete',
    'recycle_template:view',
    'recycle_template:create',
    'recycle_template:update',
    'recycle_template:delete',
]

PERMISSION_SET = set(PERMISSIONS)


def validate_permissions(perms):
    if not perms:
        return [], []
    invalid = [p for p in perms if p not in PERMISSION_SET and p != '*']
    valid = [p for p in perms if p in PERMISSION_SET or p == '*']
    return valid, invalid
