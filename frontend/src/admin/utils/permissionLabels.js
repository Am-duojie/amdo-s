export const permissionLabels = {
  '*': '全部权限',
  'dashboard:view': '控制面板查看',
  'admin_user:view': '管理员查看',
  'admin_user:write': '管理员编辑',
  'admin_user:delete': '管理员删除',
  'role:view': '角色查看',
  'role:write': '角色编辑',
  'inspection:view': '质检单查看',
  'inspection:write': '质检单编辑',
  'recycled:view': '回收订单查看',
  'recycled:write': '回收订单操作',
  'verified:view': '验机商品查看',
  'verified:read': '验机商品查看',
  'verified:write': '验机商品编辑',
  'audit:view': '内容审核查看',
  'audit:write': '内容审核处理',
  'audit_log:view': '审计日志查看',
  'payment:view': '支付查看',
  'payment:write': '支付处理',
  'order:ship': '订单发货',
  'category:view': '分类查看',
  'category:write': '分类编辑',
  'category:delete': '分类删除',
  'product:view': '商品查看',
  'product:write': '商品编辑',
  'product:delete': '商品删除',
  'user:view': '用户查看',
  'user:write': '用户编辑',
  'user:delete': '用户删除',
  'message:view': '消息查看',
  'message:delete': '消息删除',
  'address:view': '地址查看',
  'address:delete': '地址删除',
  'recycle_template:view': '回收模板查看',
  'recycle_template:create': '回收模板创建',
  'recycle_template:update': '回收模板编辑',
  'recycle_template:delete': '回收模板删除'
}

export const getPermissionLabel = (code) => permissionLabels[code] || code

export const formatPermission = (code) => {
  const label = getPermissionLabel(code)
  if (!label || label === code) return code
  return `${label} (${code})`
}
