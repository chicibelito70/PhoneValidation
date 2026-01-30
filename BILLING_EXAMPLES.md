# Ejemplos de Respuestas JSON - Sistema de Facturación

## 📄 1. Lista de Facturas

**GET /billing/invoices**

```json
[
  {
    "id": 1,
    "stripe_invoice_id": "in_1234567890",
    "amount": 29.99,
    "currency": "usd",
    "status": "paid",
    "pdf_url": "https://pay.stripe.com/invoice/inv_1234567890/pdf",
    "period_start": "2024-01-01T00:00:00Z",
    "period_end": "2024-02-01T00:00:00Z",
    "issued_at": "2024-01-15T10:30:00Z",
    "paid_at": "2024-01-15T10:35:00Z",
    "items": [
      {
        "id": 1,
        "description": "Pro Plan - Monthly",
        "amount": 29.99,
        "quantity": 1,
        "period_start": "2024-01-01T00:00:00Z",
        "period_end": "2024-02-01T00:00:00Z"
      }
    ]
  },
  {
    "id": 2,
    "stripe_invoice_id": "in_0987654321",
    "amount": 29.99,
    "currency": "usd",
    "status": "open",
    "pdf_url": null,
    "period_start": "2024-02-01T00:00:00Z",
    "period_end": "2024-03-01T00:00:00Z",
    "issued_at": "2024-02-15T10:30:00Z",
    "paid_at": null,
    "items": [
      {
        "id": 2,
        "description": "Pro Plan - Monthly",
        "amount": 29.99,
        "quantity": 1,
        "period_start": "2024-02-01T00:00:00Z",
        "period_end": "2024-03-01T00:00:00Z"
      }
    ]
  }
]
```

## 📊 2. Resumen de Facturación

**GET /dashboard/billing-summary**

```json
{
  "total_paid": 299.99,
  "pending_invoices": 1,
  "last_payment_date": "2024-01-15T10:35:00Z",
  "currency": "usd"
}
```

## 📋 3. Detalle de Factura

**GET /billing/invoices/1**

```json
{
  "id": 1,
  "stripe_invoice_id": "in_1234567890",
  "amount": 29.99,
  "currency": "usd",
  "status": "paid",
  "pdf_url": "https://pay.stripe.com/invoice/inv_1234567890/pdf",
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-02-01T00:00:00Z",
  "issued_at": "2024-01-15T10:30:00Z",
  "paid_at": "2024-01-15T10:35:00Z",
  "items": [
    {
      "id": 1,
      "description": "Pro Plan - Monthly",
      "amount": 29.99,
      "quantity": 1,
      "period_start": "2024-01-01T00:00:00Z",
      "period_end": "2024-02-01T00:00:00Z"
    },
    {
      "id": 2,
      "description": "Additional API calls (500 over limit)",
      "amount": 5.00,
      "quantity": 1,
      "period_start": "2024-01-15T00:00:00Z",
      "period_end": "2024-01-16T00:00:00Z"
    }
  ]
}
```

## 💰 4. Crear Reembolso

**POST /billing/refund**

Request:
```json
{
  "invoice_id": 1,
  "amount": 15.00
}
```

Response:
```json
{
  "id": "ref_1234567890",
  "amount": 15.00,
  "currency": "usd",
  "status": "succeeded"
}
```

## 🏢 5. Actualizar Info Fiscal

**PUT /billing/tax-info**

Request:
```json
{
  "tax_name": "Acme Corporation S.L.",
  "tax_address": "Calle Gran Vía 123, 28013 Madrid, Spain",
  "tax_country": "ES",
  "tax_id": "B87654321"
}
```

Response:
```json
{
  "message": "Tax information updated"
}
```

## 🔄 6. Webhook Payloads de Stripe

### invoice.created
```json
{
  "id": "evt_1234567890",
  "object": "event",
  "type": "invoice.created",
  "data": {
    "object": {
      "id": "in_1234567890",
      "customer": "cus_1234567890",
      "amount_due": 2999,
      "currency": "usd",
      "status": "draft",
      "period_start": 1704067200,
      "period_end": 1706745600,
      "lines": {
        "data": [
          {
            "description": "Pro Plan - Monthly",
            "amount": 2999,
            "quantity": 1,
            "period": {
              "start": 1704067200,
              "end": 1706745600
            }
          }
        ]
      }
    }
  }
}
```

### invoice.payment_succeeded
```json
{
  "id": "evt_0987654321",
  "object": "event",
  "type": "invoice.payment_succeeded",
  "data": {
    "object": {
      "id": "in_1234567890",
      "customer": "cus_1234567890",
      "amount_paid": 2999,
      "status": "paid",
      "status_transitions": {
        "paid_at": 1705322100
      }
    }
  }
}
```

### invoice.payment_failed
```json
{
  "id": "evt_1122334455",
  "object": "event",
  "type": "invoice.payment_failed",
  "data": {
    "object": {
      "id": "in_1234567890",
      "customer": "cus_1234567890",
      "status": "open",
      "attempt_count": 3
    }
  }
}
```

## 📈 7. Dashboard de Uso con Facturación

**GET /dashboard/usage**

```json
{
  "daily_usage": 1250,
  "monthly_usage": 8500,
  "plan": "pro",
  "status": "active",
  "billing_info": {
    "current_invoice_amount": 29.99,
    "next_billing_date": "2024-02-01T00:00:00Z",
    "overage_charges": 5.00
  }
}
```

## ⚠️ 8. Errores Comunes

### Factura no encontrada
```json
{
  "detail": "Invoice not found"
}
```

### Reembolso fallido
```json
{
  "detail": "Refund failed: Card was declined"
}
```

### Info fiscal inválida
```json
{
  "detail": "User or Stripe customer not found"
}
```

## 🔄 9. Flujo de Estados de Factura

```
draft → open → paid
   ↓      ↓      ↓
 void   failed  refunded
```

- **draft**: Factura creada, no finalizada
- **open**: Lista para pago, enviada al cliente
- **paid**: Pagada exitosamente
- **failed**: Pago rechazado
- **void**: Cancelada antes del pago
- **refunded**: Reembolsada parcial/totalmente

## 📊 10. Métricas de Negocio

### MRR (Monthly Recurring Revenue)
```sql
SELECT SUM(amount) as mrr
FROM invoices
WHERE status = 'paid'
  AND period_end >= CURRENT_DATE
  AND period_start <= CURRENT_DATE;
```

### Churn Rate
```sql
SELECT
  COUNT(CASE WHEN status = 'canceled' THEN 1 END) * 100.0 / COUNT(*) as churn_rate
FROM subscriptions
WHERE created_at >= '2024-01-01';
```

### LTV (Customer Lifetime Value)
```sql
SELECT user_id, SUM(amount) as ltv
FROM invoices
WHERE status = 'paid'
GROUP BY user_id
ORDER BY ltv DESC;
```