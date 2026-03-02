/**
 * New Collection Template
 *
 * Usage:
 * 1. Copy this file to apps/cms/src/collections/{{CollectionName}}/index.ts
 * 2. Replace {{CollectionName}}, {{collectionName}}, {{collection-name}} placeholders
 * 3. Add fields as needed
 * 4. Register in payload.config.ts
 * 5. Run: pnpm payload migrate:create && pnpm payload migrate
 */

import type { CollectionConfig } from 'payload'
import { slugField } from '../../fields/slug'

export const {{CollectionName}}: CollectionConfig = {
  // URL-safe identifier (plural, kebab-case)
  slug: '{{collection-name}}',

  // Admin UI configuration
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', '_status', 'updatedAt'],
    group: 'Content', // Or: 'System', 'Taxonomy'
    description: 'Description of this collection',
  },

  // Access control
  access: {
    // Public can read published items
    read: ({ req }) => {
      if (req.user) return true // Authenticated see all
      return { _status: { equals: 'published' } }
    },
    // Only authenticated users can create
    create: ({ req }) => !!req.user,
    // Only authenticated users can update
    update: ({ req }) => !!req.user,
    // Only authenticated users can delete
    delete: ({ req }) => !!req.user,
  },

  // Fields definition
  fields: [
    // Required title field
    {
      name: 'title',
      type: 'text',
      required: true,
      admin: {
        description: 'The title of this item',
      },
    },

    // Auto-generated slug
    ...slugField(),

    // Add your custom fields below
    // Example: text field
    // {
    //   name: 'subtitle',
    //   type: 'text',
    // },

    // Example: textarea field
    // {
    //   name: 'description',
    //   type: 'textarea',
    // },

    // Example: rich text field
    // {
    //   name: 'content',
    //   type: 'richText',
    // },

    // Example: relationship field
    // {
    //   name: 'category',
    //   type: 'relationship',
    //   relationTo: 'categories',
    // },

    // Example: upload field
    // {
    //   name: 'featuredImage',
    //   type: 'upload',
    //   relationTo: 'media',
    // },

    // Example: select field
    // {
    //   name: 'status',
    //   type: 'select',
    //   options: [
    //     { label: 'Active', value: 'active' },
    //     { label: 'Inactive', value: 'inactive' },
    //   ],
    //   defaultValue: 'active',
    // },

    // Example: checkbox field
    // {
    //   name: 'featured',
    //   type: 'checkbox',
    //   defaultValue: false,
    // },

    // Example: date field
    // {
    //   name: 'publishedAt',
    //   type: 'date',
    //   admin: {
    //     date: {
    //       pickerAppearance: 'dayAndTime',
    //     },
    //   },
    // },

    // Example: group field
    // {
    //   name: 'metadata',
    //   type: 'group',
    //   fields: [
    //     { name: 'author', type: 'text' },
    //     { name: 'source', type: 'text' },
    //   ],
    // },

    // Example: array field
    // {
    //   name: 'tags',
    //   type: 'array',
    //   fields: [
    //     { name: 'tag', type: 'text' },
    //   ],
    // },
  ],

  // Enable timestamps
  timestamps: true,

  // Enable versioning with drafts
  versions: {
    drafts: {
      autosave: {
        interval: 300, // 5 minutes
      },
    },
    maxPerDoc: 10,
  },

  // Hooks (uncomment as needed)
  // hooks: {
  //   beforeChange: [
  //     async ({ data, req, operation }) => {
  //       if (operation === 'create') {
  //         // Set default values on create
  //       }
  //       return data
  //     },
  //   ],
  //   afterChange: [
  //     async ({ doc, req, operation }) => {
  //       // Trigger revalidation, send notifications, etc.
  //     },
  //   ],
  // },
}
