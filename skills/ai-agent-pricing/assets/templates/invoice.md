# Invoice Template

## Standard Invoice

```markdown
+------------------------------------------------------------------+
|                                                                   |
|  [YOUR COMPANY LOGO]                                             |
|                                                                   |
|  INVOICE                                                          |
|                                                                   |
+------------------------------------------------------------------+

Invoice #:     INV-[YYYY]-[####]
Date:          [Invoice Date]
Due Date:      [Due Date]

+------------------------------------------------------------------+
|  FROM                          |  TO                              |
+------------------------------------------------------------------+
|  [Your Company Name]           |  [Client Company Name]           |
|  [Your Address Line 1]         |  [Client Address Line 1]         |
|  [Your Address Line 2]         |  [Client Address Line 2]         |
|  [Your Email]                  |  [Client Email]                  |
|  [Your Phone]                  |  [Client Phone]                  |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  DESCRIPTION                                  |  AMOUNT           |
+------------------------------------------------------------------+
|  AI Agent Setup - [Description]               |  $[X,XXX.XX]     |
|  Monthly Service - [Month] [Year]             |  $[XXX.XX]       |
|  Additional Tasks (X,XXX @ $0.02 each)        |  $[XX.XX]        |
|  Custom Development - [Description]           |  $[XXX.XX]       |
+------------------------------------------------------------------+
|                                    Subtotal:  |  $[X,XXX.XX]     |
|                                    Tax (X%):  |  $[XXX.XX]       |
|                                    =============================  |
|                                    TOTAL DUE: |  $[X,XXX.XX]     |
+------------------------------------------------------------------+

PAYMENT TERMS
- Due upon receipt / Net 15 / Net 30
- Late payments subject to 1.5% monthly interest

PAYMENT METHODS
- Bank Transfer: [Account details]
- Credit Card: [Payment link]
- PayPal: [PayPal email]

NOTES
[Any additional notes or thank you message]

+------------------------------------------------------------------+
|  Thank you for your business!                                     |
+------------------------------------------------------------------+
```

## React/HTML Invoice Component

```tsx
interface InvoiceProps {
  invoiceNumber: string
  date: string
  dueDate: string
  from: {
    name: string
    address: string[]
    email: string
    phone?: string
  }
  to: {
    name: string
    address: string[]
    email: string
    phone?: string
  }
  items: {
    description: string
    quantity?: number
    rate?: number
    amount: number
  }[]
  taxRate?: number
  notes?: string
  currency?: string
}

export function Invoice({
  invoiceNumber,
  date,
  dueDate,
  from,
  to,
  items,
  taxRate = 0,
  notes,
  currency = '$'
}: InvoiceProps) {
  const subtotal = items.reduce((sum, item) => sum + item.amount, 0)
  const tax = subtotal * (taxRate / 100)
  const total = subtotal + tax

  return (
    <div className="max-w-3xl mx-auto p-8 bg-white">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">INVOICE</h1>
          <p className="text-gray-600">#{invoiceNumber}</p>
        </div>
        <div className="text-right">
          <p className="text-gray-600">Date: {date}</p>
          <p className="text-gray-600">Due: {dueDate}</p>
        </div>
      </div>

      {/* From/To */}
      <div className="grid grid-cols-2 gap-8 mb-8">
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">From</h3>
          <p className="font-medium">{from.name}</p>
          {from.address.map((line, i) => (
            <p key={i} className="text-gray-600">{line}</p>
          ))}
          <p className="text-gray-600">{from.email}</p>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">To</h3>
          <p className="font-medium">{to.name}</p>
          {to.address.map((line, i) => (
            <p key={i} className="text-gray-600">{line}</p>
          ))}
          <p className="text-gray-600">{to.email}</p>
        </div>
      </div>

      {/* Items */}
      <table className="w-full mb-8">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="text-left py-2 font-semibold">Description</th>
            <th className="text-right py-2 font-semibold">Amount</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i} className="border-b border-gray-100">
              <td className="py-3">{item.description}</td>
              <td className="py-3 text-right">
                {currency}{item.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Totals */}
      <div className="flex justify-end">
        <div className="w-64">
          <div className="flex justify-between py-2">
            <span className="text-gray-600">Subtotal</span>
            <span>{currency}{subtotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          </div>
          {taxRate > 0 && (
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Tax ({taxRate}%)</span>
              <span>{currency}{tax.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            </div>
          )}
          <div className="flex justify-between py-2 border-t-2 border-gray-900 font-bold text-lg">
            <span>Total Due</span>
            <span>{currency}{total.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          </div>
        </div>
      </div>

      {/* Notes */}
      {notes && (
        <div className="mt-8 p-4 bg-gray-50 rounded">
          <h3 className="font-semibold mb-2">Notes</h3>
          <p className="text-gray-600">{notes}</p>
        </div>
      )}
    </div>
  )
}
```

## Israeli Invoice (NIS + VAT)

```markdown
+------------------------------------------------------------------+
|                                                                   |
|  [YOUR COMPANY LOGO]                    חשבונית מס / INVOICE      |
|                                                                   |
+------------------------------------------------------------------+

מספר חשבונית / Invoice #:     [####]
תאריך / Date:                 [DD/MM/YYYY]
תאריך לתשלום / Due Date:      [DD/MM/YYYY]

+------------------------------------------------------------------+
|  מאת / FROM                    |  אל / TO                        |
+------------------------------------------------------------------+
|  [שם העסק]                     |  [שם הלקוח]                      |
|  ח.פ. [########]               |  ח.פ. [########]                 |
|  [כתובת]                       |  [כתובת]                         |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  תיאור / DESCRIPTION                          |  סכום / AMOUNT   |
+------------------------------------------------------------------+
|  הקמת סוכן AI - [תיאור]                        |  ₪[X,XXX]        |
|  שירות חודשי - [חודש] [שנה]                    |  ₪[XXX]          |
+------------------------------------------------------------------+
|                               סה"כ לפני מע"מ:  |  ₪[X,XXX]        |
|                                   מע"מ (17%):  |  ₪[XXX]          |
|                                    ==========================      |
|                               סה"כ לתשלום:    |  ₪[X,XXX]        |
+------------------------------------------------------------------+

אמצעי תשלום:
- העברה בנקאית: [פרטי חשבון]
- כרטיס אשראי: [לינק לתשלום]
- ביט / פייבוקס: [מספר טלפון]

הערות:
[הערות נוספות]

+------------------------------------------------------------------+
|  תודה על בחירתכם בנו!                                             |
+------------------------------------------------------------------+
```

## Invoice Numbering System

```
Format: INV-[YEAR]-[SEQUENCE]

Examples:
- INV-2024-0001 (First invoice of 2024)
- INV-2024-0002 (Second invoice of 2024)
- INV-2025-0001 (First invoice of 2025, resets)

For multiple clients:
- INV-[CLIENT_CODE]-[YEAR]-[SEQUENCE]
- INV-TFS-2024-0001 (TechFlow Solutions, first invoice)
```

## Recurring Invoice Schedule

```
Monthly Billing:
- Invoice generated: 1st of month
- Due date: 15th of month
- Reminder: 10th of month
- Late notice: 20th of month

Annual Billing:
- Invoice generated: Contract anniversary - 30 days
- Due date: Contract anniversary
- Reminder: Contract anniversary - 7 days
```
