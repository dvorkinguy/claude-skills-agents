# Rails Integration Patterns for n8n

Patterns for integrating n8n automations into Rails applications.

## Two Use Cases

| Use Case | Description | Key Components |
|----------|-------------|----------------|
| **Selling Automations** | Users buy/subscribe to pre-built workflows | Product catalog, checkout, delivery |
| **In-App Usage** | n8n workflows power app features | Webhooks, API calls, tracking |

---

## 1. Selling Automations

### Automation Model

```ruby
# app/models/automation.rb
class Automation < ApplicationRecord
  extend FriendlyId
  friendly_id :english_slug, use: [:slugged, :history]

  # Associations
  has_many :purchases
  has_many :buyers, through: :purchases, source: :user
  has_one_attached :preview_image
  has_one_attached :workflow_file  # JSON export

  # Validations
  validates :name, presence: true
  validates :english_slug, presence: true, uniqueness: true
  validates :price, numericality: { greater_than_or_equal_to: 0 }

  # Attributes
  # name: Hebrew name
  # english_slug: URL slug
  # description: Hebrew description
  # short_description: For cards
  # price: decimal (ILS)
  # workflow_json: jsonb - n8n workflow structure
  # demo_webhook_url: For live demos
  # category: e.g., 'lead-generation', 'crm'
  # features: jsonb - Feature list
  # requirements: jsonb - What user needs (API keys, etc.)
  # setup_time: integer - Minutes to setup
  # published: boolean

  scope :published, -> { where(published: true) }
  scope :by_category, ->(cat) { where(category: cat) }
  scope :featured, -> { where(featured: true) }
end
```

### Migration

```ruby
class CreateAutomations < ActiveRecord::Migration[7.1]
  def change
    create_table :automations do |t|
      t.string :name, null: false
      t.string :english_slug, null: false, index: { unique: true }
      t.string :slug, index: { unique: true }
      t.text :description
      t.string :short_description
      t.decimal :price, precision: 10, scale: 2, default: 0
      t.jsonb :workflow_json, default: {}
      t.string :demo_webhook_url
      t.string :category
      t.jsonb :features, default: []
      t.jsonb :requirements, default: []
      t.integer :setup_time
      t.boolean :published, default: false
      t.boolean :featured, default: false

      t.timestamps
    end

    add_index :automations, :category
    add_index :automations, :published
  end
end
```

### Purchase Model

```ruby
# app/models/purchase.rb
class Purchase < ApplicationRecord
  belongs_to :user
  belongs_to :automation

  # status: pending, completed, refunded
  # price_paid: decimal
  # payment_method: string
  # stripe_payment_id: string

  after_create :deliver_automation

  private

  def deliver_automation
    PurchaseMailer.delivery(self).deliver_later
  end
end
```

### Delivery Options

#### Option A: JSON Download

```ruby
# app/controllers/automations_controller.rb
class AutomationsController < ApplicationController
  def download
    @automation = current_user.purchased_automations.friendly.find(params[:id])

    send_data @automation.workflow_json.to_json,
              filename: "#{@automation.english_slug}.json",
              type: 'application/json'
  end
end
```

#### Option B: Deploy to User's n8n

```ruby
# app/services/n8n_deployment_service.rb
class N8nDeploymentService
  def initialize(user, automation)
    @user = user
    @automation = automation
  end

  def deploy
    n8n_client = N8nClient.new(@user.n8n_api_key, @user.n8n_url)
    n8n_client.import_workflow(@automation.workflow_json)
  end
end
```

#### Option C: Embedded Viewer

```jsx
// app/javascript/components/WorkflowViewer.jsx
export default function WorkflowViewer({ workflowJson }) {
  // Render read-only workflow visualization
  return (
    <div className="workflow-viewer">
      {/* Custom visualization or n8n embed */}
    </div>
  );
}
```

---

## 2. In-App n8n Usage

### N8n Service

```ruby
# app/services/n8n_service.rb
class N8nService
  include HTTParty
  base_uri ENV['N8N_BASE_URL']

  def initialize
    @headers = {
      'Content-Type' => 'application/json',
      'X-N8N-API-KEY' => ENV['N8N_API_KEY']
    }
  end

  # Trigger workflow via webhook
  def trigger_webhook(webhook_url, payload)
    response = HTTParty.post(webhook_url, {
      body: payload.to_json,
      headers: @headers.merge({
        'X-Webhook-Secret' => ENV['N8N_WEBHOOK_SECRET']
      })
    })
    handle_response(response)
  end

  # Get workflow execution status
  def get_execution(execution_id)
    self.class.get("/executions/#{execution_id}", headers: @headers)
  end

  # List recent executions
  def list_executions(workflow_id, limit: 10)
    self.class.get("/executions", {
      headers: @headers,
      query: { workflowId: workflow_id, limit: limit }
    })
  end

  private

  def handle_response(response)
    case response.code
    when 200..299
      { success: true, data: response.parsed_response }
    else
      { success: false, error: response.message }
    end
  end
end
```

### Webhook Controller

```ruby
# app/controllers/api/v1/webhooks_controller.rb
module Api
  module V1
    class WebhooksController < ApplicationController
      skip_before_action :verify_authenticity_token
      before_action :verify_n8n_signature

      # POST /api/v1/webhooks/n8n
      def n8n
        case params[:event_type]
        when 'execution_completed'
          handle_execution_completed(params)
        when 'lead_captured'
          handle_lead_captured(params)
        when 'notification'
          handle_notification(params)
        else
          Rails.logger.warn "Unknown n8n event: #{params[:event_type]}"
        end

        render json: { received: true }, status: :ok
      end

      private

      def verify_n8n_signature
        signature = request.headers['X-N8N-Signature']
        expected = OpenSSL::HMAC.hexdigest(
          'sha256',
          ENV['N8N_WEBHOOK_SECRET'],
          request.raw_post
        )

        unless ActiveSupport::SecurityUtils.secure_compare(signature.to_s, expected)
          render json: { error: 'Invalid signature' }, status: :unauthorized
        end
      end

      def handle_execution_completed(params)
        execution = WorkflowExecution.find_by(n8n_execution_id: params[:execution_id])
        execution&.update(
          status: 'completed',
          result: params[:result],
          completed_at: Time.current
        )
      end

      def handle_lead_captured(params)
        Lead.create!(
          email: params[:email],
          name: params[:name],
          source: params[:source],
          metadata: params[:metadata]
        )
      end

      def handle_notification(params)
        Notification.create!(
          user_id: params[:user_id],
          message: params[:message],
          notification_type: params[:type]
        )
      end
    end
  end
end
```

### Routes

```ruby
# config/routes.rb
Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      post 'webhooks/n8n', to: 'webhooks#n8n'
    end
  end
end
```

---

## 3. Common Integration Patterns

### Pattern 1: Form → n8n → CRM

```ruby
# app/controllers/contacts_controller.rb
class ContactsController < ApplicationController
  def create
    @contact = Contact.new(contact_params)

    if @contact.save
      N8nService.new.trigger_webhook(
        ENV['N8N_CONTACT_WEBHOOK'],
        {
          event: 'contact_created',
          contact: @contact.as_json,
          timestamp: Time.current.iso8601
        }
      )
      redirect_to thank_you_path
    else
      render :new
    end
  end
end
```

### Pattern 2: Scheduled Reports via n8n

```ruby
# n8n workflow triggers this endpoint daily
# app/controllers/api/v1/reports_controller.rb
module Api
  module V1
    class ReportsController < ApplicationController
      before_action :verify_n8n_signature

      def daily_stats
        stats = {
          new_users: User.where('created_at > ?', 1.day.ago).count,
          new_leads: Lead.where('created_at > ?', 1.day.ago).count,
          revenue: Purchase.where('created_at > ?', 1.day.ago).sum(:price_paid)
        }
        render json: stats
      end
    end
  end
end
```

### Pattern 3: Demo Execution

```ruby
# app/controllers/demos_controller.rb
class DemosController < ApplicationController
  def execute
    @automation = Automation.friendly.find(params[:automation_id])

    result = N8nService.new.trigger_webhook(
      @automation.demo_webhook_url,
      demo_params
    )

    render json: {
      success: result[:success],
      result: result[:data]
    }
  end

  private

  def demo_params
    params.permit(:input_text, :sample_data).to_h
  end
end
```

### Pattern 4: Background Job with n8n

```ruby
# app/jobs/process_with_n8n_job.rb
class ProcessWithN8nJob < ApplicationJob
  queue_as :default

  def perform(record_id, workflow_type)
    record = Record.find(record_id)
    webhook_url = ENV["N8N_#{workflow_type.upcase}_WEBHOOK"]

    result = N8nService.new.trigger_webhook(webhook_url, {
      record_id: record.id,
      data: record.attributes
    })

    record.update(
      processing_status: result[:success] ? 'completed' : 'failed',
      processing_result: result[:data]
    )
  end
end
```

---

## 4. Execution Tracking

### Model

```ruby
# app/models/workflow_execution.rb
class WorkflowExecution < ApplicationRecord
  belongs_to :user
  belongs_to :automation, optional: true

  # n8n_execution_id: string
  # workflow_name: string
  # status: pending, running, completed, failed
  # input_data: jsonb
  # output_data: jsonb
  # error_message: text
  # started_at: datetime
  # completed_at: datetime

  scope :recent, -> { order(created_at: :desc) }
  scope :by_status, ->(status) { where(status: status) }
end
```

### Tracking Service

```ruby
# app/services/execution_tracker.rb
class ExecutionTracker
  def self.start(user:, workflow_name:, input_data:)
    WorkflowExecution.create!(
      user: user,
      workflow_name: workflow_name,
      input_data: input_data,
      status: 'pending',
      started_at: Time.current
    )
  end

  def self.complete(execution_id:, output_data:)
    execution = WorkflowExecution.find_by(n8n_execution_id: execution_id)
    execution&.update(
      status: 'completed',
      output_data: output_data,
      completed_at: Time.current
    )
  end

  def self.fail(execution_id:, error_message:)
    execution = WorkflowExecution.find_by(n8n_execution_id: execution_id)
    execution&.update(
      status: 'failed',
      error_message: error_message,
      completed_at: Time.current
    )
  end
end
```

---

## 5. Security

### Webhook Signature Verification

```ruby
module WebhookVerifiable
  extend ActiveSupport::Concern

  private

  def verify_n8n_signature
    signature = request.headers['X-N8N-Signature']
    payload = request.raw_post

    expected = OpenSSL::HMAC.hexdigest(
      'sha256',
      ENV['N8N_WEBHOOK_SECRET'],
      payload
    )

    unless ActiveSupport::SecurityUtils.secure_compare(signature.to_s, expected)
      render json: { error: 'Unauthorized' }, status: 401
    end
  end
end
```

### API Key Encryption

```ruby
# app/models/user.rb
class User < ApplicationRecord
  encrypts :n8n_api_key
end
```

### Rate Limiting

```ruby
# config/initializers/rack_attack.rb
Rack::Attack.throttle('n8n webhooks', limit: 100, period: 1.minute) do |req|
  if req.path.start_with?('/api/v1/webhooks')
    req.ip
  end
end
```

---

## 6. Environment Configuration

```bash
# .env
N8N_BASE_URL=https://your-n8n-instance.com/api/v1
N8N_API_KEY=your-api-key
N8N_WEBHOOK_SECRET=your-webhook-secret

# Webhook URLs for different workflows
N8N_CONTACT_WEBHOOK=https://your-n8n.com/webhook/contact
N8N_LEAD_WEBHOOK=https://your-n8n.com/webhook/lead
N8N_REPORT_WEBHOOK=https://your-n8n.com/webhook/report
```

---

## 7. Pricing Models

### One-Time Purchase

```ruby
class Automation < ApplicationRecord
  # price: decimal
  # license_type: 'lifetime'
end
```

### Subscription Access

```ruby
class Subscription < ApplicationRecord
  belongs_to :user
  # plan: basic, pro, enterprise
  # status: active, cancelled, past_due
  # stripe_subscription_id: string

  def accessible_automations
    case plan
    when 'basic' then Automation.where(tier: 'basic')
    when 'pro' then Automation.where(tier: ['basic', 'pro'])
    when 'enterprise' then Automation.all
    end
  end
end
```

### Usage-Based

```ruby
class UsageRecord < ApplicationRecord
  belongs_to :user
  belongs_to :automation
  # executions_count: integer
  # billing_period: date
end
```

---

## 8. Checklist

### Selling Automations
- [ ] Automation model with all fields
- [ ] Purchase/checkout flow (Stripe)
- [ ] Delivery mechanism (download/deploy)
- [ ] Product pages with SEO
- [ ] Demo functionality

### In-App Usage
- [ ] N8nService class
- [ ] Webhook controller
- [ ] Signature verification
- [ ] Execution tracking
- [ ] Error handling

### Security
- [ ] Environment variables configured
- [ ] Webhook signatures verified
- [ ] Rate limiting enabled
- [ ] API keys encrypted

### Monitoring
- [ ] Execution logs
- [ ] Error notifications
- [ ] Usage analytics
