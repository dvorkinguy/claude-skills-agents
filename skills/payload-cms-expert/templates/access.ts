/**
 * Access Control Templates
 *
 * Usage:
 * 1. Copy relevant functions to apps/cms/src/access/
 * 2. Import and use in collection access config
 */

import type { Access, FieldAccess } from 'payload'

// ============================================
// Collection-Level Access
// ============================================

/**
 * Allow anyone (including unauthenticated)
 */
export const isAnyone: Access = () => true

/**
 * Require authentication
 */
export const isAuthenticated: Access = ({ req }) => {
  return !!req.user
}

/**
 * Require admin role
 */
export const isAdmin: Access = ({ req }) => {
  return req.user?.role === 'admin'
}

/**
 * Require admin OR the user themselves
 * Useful for user profiles
 */
export const isAdminOrSelf: Access = ({ req }) => {
  if (!req.user) return false
  if (req.user.role === 'admin') return true

  // Return a query constraint for "self"
  return {
    id: {
      equals: req.user.id,
    },
  }
}

/**
 * Published only for public, all for authenticated
 */
export const publishedOrAuthenticated: Access = ({ req }) => {
  if (req.user) return true // Authenticated see all

  return {
    _status: {
      equals: 'published',
    },
  }
}

/**
 * Owner-based access
 * User can only access their own documents
 */
export const isOwner: Access = ({ req }) => {
  if (!req.user) return false
  if (req.user.role === 'admin') return true

  return {
    createdBy: {
      equals: req.user.id,
    },
  }
}

/**
 * Organization-based access
 * User can only access documents in their organization
 */
export const isSameOrganization: Access = ({ req }) => {
  if (!req.user) return false
  if (req.user.role === 'admin') return true

  return {
    organization: {
      equals: req.user.organization,
    },
  }
}

/**
 * Role-based with multiple roles
 */
export const hasRole = (...roles: string[]): Access => {
  return ({ req }) => {
    if (!req.user) return false
    return roles.includes(req.user.role)
  }
}

// ============================================
// Field-Level Access
// ============================================

/**
 * Only admins can see this field
 */
export const adminFieldAccess: FieldAccess = ({ req }) => {
  return req.user?.role === 'admin'
}

/**
 * Field is read-only for non-admins
 */
export const adminOnlyUpdate: FieldAccess = ({ req, operation }) => {
  if (operation === 'read') return true
  return req.user?.role === 'admin'
}

/**
 * Field is only visible to owner
 */
export const ownerFieldAccess: FieldAccess = ({ req, doc }) => {
  if (req.user?.role === 'admin') return true
  return doc?.createdBy === req.user?.id
}

// ============================================
// Usage Examples
// ============================================

/*
// Collection with various access patterns
export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    // Anyone can read published posts
    read: publishedOrAuthenticated,

    // Only authenticated can create
    create: isAuthenticated,

    // Only admin or author can update
    update: ({ req }) => {
      if (!req.user) return false
      if (req.user.role === 'admin') return true
      return { author: { equals: req.user.id } }
    },

    // Only admin can delete
    delete: isAdmin,
  },
  fields: [
    {
      name: 'internalNotes',
      type: 'textarea',
      access: {
        read: adminFieldAccess,
        update: adminFieldAccess,
      },
    },
    {
      name: 'featured',
      type: 'checkbox',
      access: {
        update: adminOnlyUpdate, // Anyone can read, only admin can update
      },
    },
  ],
}

// User collection with self-access
export const Users: CollectionConfig = {
  slug: 'users',
  access: {
    read: isAdminOrSelf,
    create: isAdmin,
    update: isAdminOrSelf,
    delete: isAdmin,
  },
}

// Organization-scoped collection
export const Projects: CollectionConfig = {
  slug: 'projects',
  access: {
    read: isSameOrganization,
    create: isAuthenticated,
    update: isSameOrganization,
    delete: hasRole('admin', 'manager'),
  },
}
*/
