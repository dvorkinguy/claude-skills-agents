/**
 * New Block Template
 *
 * Usage:
 * 1. Copy this file to apps/cms/src/blocks/{{BlockName}}/config.ts
 * 2. Replace {{BlockName}}, {{blockName}} placeholders
 * 3. Add fields as needed
 * 4. Register in Pages collection (apps/cms/src/collections/Pages/index.ts)
 * 5. Create frontend component (apps/www/components/cms/blocks/{{BlockName}}Section.tsx)
 * 6. Add to BlockRenderer.tsx
 */

import type { Block } from 'payload'

export const {{BlockName}}: Block = {
  // URL-safe identifier (camelCase)
  slug: '{{blockName}}',

  // TypeScript interface name (auto-generated)
  interfaceName: '{{BlockName}}Block',

  // Admin UI labels
  labels: {
    singular: '{{Block Name}}',
    plural: '{{Block Name}}s',
  },

  // Optional: image showing block preview
  // imageURL: '/path/to/preview.png',

  // Optional: image showing block preview in alt format
  // imageAltText: 'Preview of {{Block Name}} block',

  // Fields definition
  fields: [
    // Style variant selector
    {
      name: 'style',
      type: 'select',
      defaultValue: 'default',
      options: [
        { label: 'Default', value: 'default' },
        { label: 'Alternate', value: 'alternate' },
        // Add more style variants
      ],
      admin: {
        description: 'Visual style variant',
      },
    },

    // Common fields
    {
      name: 'headline',
      type: 'text',
      required: true,
      admin: {
        description: 'Main headline text',
      },
    },

    {
      name: 'subheadline',
      type: 'textarea',
      admin: {
        description: 'Supporting text below headline',
      },
    },

    // Media field
    // {
    //   name: 'media',
    //   type: 'upload',
    //   relationTo: 'media',
    //   admin: {
    //     description: 'Background or featured image',
    //   },
    // },

    // CTA button group
    // {
    //   name: 'primaryCTA',
    //   type: 'group',
    //   fields: [
    //     { name: 'text', type: 'text', label: 'Button Text' },
    //     { name: 'url', type: 'text', label: 'Button URL' },
    //     {
    //       name: 'style',
    //       type: 'select',
    //       options: [
    //         { label: 'Primary', value: 'primary' },
    //         { label: 'Secondary', value: 'secondary' },
    //       ],
    //       defaultValue: 'primary',
    //     },
    //   ],
    // },

    // Array of items
    // {
    //   name: 'items',
    //   type: 'array',
    //   minRows: 1,
    //   maxRows: 6,
    //   fields: [
    //     { name: 'title', type: 'text', required: true },
    //     { name: 'description', type: 'textarea' },
    //     { name: 'icon', type: 'text' },
    //     { name: 'media', type: 'upload', relationTo: 'media' },
    //   ],
    // },

    // Rich text content
    // {
    //   name: 'content',
    //   type: 'richText',
    // },

    // Background options
    // {
    //   name: 'background',
    //   type: 'select',
    //   options: [
    //     { label: 'None', value: 'none' },
    //     { label: 'Light', value: 'light' },
    //     { label: 'Dark', value: 'dark' },
    //     { label: 'Gradient', value: 'gradient' },
    //   ],
    //   defaultValue: 'none',
    // },

    // Spacing options
    // {
    //   name: 'spacing',
    //   type: 'select',
    //   options: [
    //     { label: 'Normal', value: 'normal' },
    //     { label: 'Compact', value: 'compact' },
    //     { label: 'Large', value: 'large' },
    //   ],
    //   defaultValue: 'normal',
    // },
  ],
}
