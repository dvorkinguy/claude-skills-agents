import { pgTable, text, timestamp, uuid, boolean, integer, jsonb } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// ============================================
// REUSABLE HELPERS
// ============================================

const timestamps = {
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
};

// ============================================
// USERS TABLE
// ============================================

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name'),
  avatar: text('avatar'),

  // Auth provider (Clerk, Auth0, etc.)
  authId: text('auth_id').notNull().unique(),

  // Subscription (Stripe)
  stripeCustomerId: text('stripe_customer_id').unique(),
  subscriptionId: text('subscription_id'),
  subscriptionStatus: text('subscription_status'), // active, canceled, past_due
  subscriptionPriceId: text('subscription_price_id'),
  subscriptionCurrentPeriodEnd: timestamp('subscription_current_period_end'),

  ...timestamps,
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;

// ============================================
// TEAMS TABLE
// ============================================

export const teams = pgTable('teams', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  slug: text('slug').notNull().unique(),
  ownerId: uuid('owner_id').notNull().references(() => users.id),
  avatar: text('avatar'),
  settings: jsonb('settings'),
  ...timestamps,
});

export type Team = typeof teams.$inferSelect;
export type NewTeam = typeof teams.$inferInsert;

// ============================================
// TEAM MEMBERS TABLE
// ============================================

export const teamMembers = pgTable('team_members', {
  id: uuid('id').primaryKey().defaultRandom(),
  teamId: uuid('team_id').notNull().references(() => teams.id, { onDelete: 'cascade' }),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  role: text('role').notNull().default('member'), // owner, admin, member
  ...timestamps,
});

export type TeamMember = typeof teamMembers.$inferSelect;
export type NewTeamMember = typeof teamMembers.$inferInsert;

// ============================================
// PROJECTS TABLE
// ============================================

export const projects = pgTable('projects', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  description: text('description'),
  teamId: uuid('team_id').notNull().references(() => teams.id, { onDelete: 'cascade' }),
  isActive: boolean('is_active').default(true).notNull(),
  settings: jsonb('settings'),
  ...timestamps,
});

export type Project = typeof projects.$inferSelect;
export type NewProject = typeof projects.$inferInsert;

// ============================================
// RELATIONS
// ============================================

export const usersRelations = relations(users, ({ many }) => ({
  ownedTeams: many(teams),
  teamMemberships: many(teamMembers),
}));

export const teamsRelations = relations(teams, ({ one, many }) => ({
  owner: one(users, {
    fields: [teams.ownerId],
    references: [users.id],
  }),
  members: many(teamMembers),
  projects: many(projects),
}));

export const teamMembersRelations = relations(teamMembers, ({ one }) => ({
  team: one(teams, {
    fields: [teamMembers.teamId],
    references: [teams.id],
  }),
  user: one(users, {
    fields: [teamMembers.userId],
    references: [users.id],
  }),
}));

export const projectsRelations = relations(projects, ({ one }) => ({
  team: one(teams, {
    fields: [projects.teamId],
    references: [teams.id],
  }),
}));
