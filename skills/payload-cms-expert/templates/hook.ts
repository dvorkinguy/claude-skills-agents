/**
 * Collection Hook Templates
 *
 * Usage:
 * 1. Copy relevant hook to apps/cms/src/collections/{{CollectionName}}/hooks/
 * 2. Import and register in collection config
 */

import type {
  CollectionBeforeChangeHook,
  CollectionAfterChangeHook,
  CollectionAfterReadHook,
  CollectionBeforeDeleteHook,
  CollectionAfterDeleteHook,
} from 'payload'
import { revalidatePath, revalidateTag } from 'next/cache'

// ============================================
// Before Change Hook
// ============================================
// Runs before document is saved (create or update)
// Use for: validation, data transformation, setting defaults

export const beforeChange: CollectionBeforeChangeHook = async ({
  data,
  req,
  operation, // 'create' | 'update'
  originalDoc,
}) => {
  // Set createdBy on create
  if (operation === 'create' && req.user) {
    data.createdBy = req.user.id
  }

  // Always update timestamp
  data.updatedAt = new Date().toISOString()

  // Example: Auto-generate slug from title
  // if (!data.slug && data.title) {
  //   data.slug = data.title
  //     .toLowerCase()
  //     .replace(/[^a-z0-9]+/g, '-')
  //     .replace(/^-|-$/g, '')
  // }

  // Example: Validate data
  // if (data.price < 0) {
  //   throw new Error('Price cannot be negative')
  // }

  return data
}

// ============================================
// After Change Hook
// ============================================
// Runs after document is saved
// Use for: revalidation, notifications, external API calls

export const afterChange: CollectionAfterChangeHook = async ({
  doc,
  req,
  operation, // 'create' | 'update'
  previousDoc,
}) => {
  // Revalidate on publish
  if (doc._status === 'published') {
    const path = doc.slug === 'home' ? '/' : `/${doc.slug}`

    // Revalidate specific path
    revalidatePath(path)

    // Revalidate sitemap
    revalidateTag('sitemap')

    // Revalidate collection tag
    revalidateTag(`${doc.collection}-${doc.slug}`)

    console.log(`Revalidated: ${path}`)
  }

  // Handle unpublish (was published, now draft)
  if (previousDoc?._status === 'published' && doc._status === 'draft') {
    const path = doc.slug === 'home' ? '/' : `/${doc.slug}`
    revalidatePath(path)
    console.log(`Unpublished and revalidated: ${path}`)
  }

  // Example: Send notification
  // if (operation === 'create') {
  //   await sendNotification({
  //     type: 'new_document',
  //     document: doc,
  //   })
  // }

  // Example: Sync to external system
  // await externalAPI.sync(doc)

  return doc
}

// ============================================
// After Read Hook
// ============================================
// Runs after document is fetched from database
// Use for: computed fields, data enrichment

export const afterRead: CollectionAfterReadHook = async ({
  doc,
  req,
}) => {
  // Example: Add computed field
  // doc.fullName = `${doc.firstName} ${doc.lastName}`

  // Example: Format dates
  // doc.formattedDate = new Intl.DateTimeFormat('en-US').format(
  //   new Date(doc.createdAt)
  // )

  // Example: Add related data
  // if (doc.authorId) {
  //   doc.authorName = await getAuthorName(doc.authorId)
  // }

  return doc
}

// ============================================
// Before Delete Hook
// ============================================
// Runs before document is deleted
// Use for: validation, cleanup, preventing deletion

export const beforeDelete: CollectionBeforeDeleteHook = async ({
  id,
  req,
}) => {
  // Example: Prevent deletion of certain documents
  // const doc = await req.payload.findByID({
  //   collection: 'pages',
  //   id,
  // })
  // if (doc.slug === 'home') {
  //   throw new Error('Cannot delete home page')
  // }

  // Example: Clean up related data
  // await req.payload.delete({
  //   collection: 'comments',
  //   where: { post: { equals: id } },
  // })

  return
}

// ============================================
// After Delete Hook
// ============================================
// Runs after document is deleted
// Use for: cleanup, revalidation, logging

export const afterDelete: CollectionAfterDeleteHook = async ({
  doc,
  req,
}) => {
  // Revalidate the path that was deleted
  const path = doc.slug === 'home' ? '/' : `/${doc.slug}`
  revalidatePath(path)

  // Example: Log deletion
  // console.log(`Deleted ${doc.collection}: ${doc.id}`)

  // Example: Clean up external resources
  // await externalStorage.delete(doc.mediaId)

  return doc
}

// ============================================
// Usage in Collection
// ============================================
/*
import { beforeChange, afterChange, afterRead, beforeDelete, afterDelete } from './hooks'

export const MyCollection: CollectionConfig = {
  slug: 'my-collection',
  hooks: {
    beforeChange: [beforeChange],
    afterChange: [afterChange],
    afterRead: [afterRead],
    beforeDelete: [beforeDelete],
    afterDelete: [afterDelete],
  },
  // ...
}
*/
