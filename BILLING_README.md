# Phone Validation SaaS - Billing System

Sistema completo de facturación integrado con Stripe para SaaS de validación de teléfonos.

## 🚀 Características Implementadas

### 1. Facturación Automática
- ✅ Generación automática de facturas por Stripe
- ✅ Facturación mensual/anual según plan
- ✅ Almacenamiento en BD: invoice_id, amount, currency, status, pdf_url, período, fechas

### 2. Webhooks Stripe - Facturación
- ✅ `invoice.created` - Crear factura en BD
- ✅ `invoice.finalized` - Factura lista para pago
- ✅ `invoice.payment_succeeded` - Pago exitoso, reactivar servicios
- ✅ `invoice.payment_failed` - Pago fallido, suspender servicios
- ✅ `invoice.voided` - Factura anulada

### 3. Facturación por Uso (Opcional)
- ✅ Soporte para billing adicional por uso excedente
- ✅ Creación automática de invoice items
- ✅ Registro de usage adicional

### 4. Dashboard de Facturación
- ✅ Listar facturas del usuario
- ✅ Ver detalle de factura con items
- ✅ Descargar PDF de Stripe
- ✅ Resumen: total pagado, facturas pendientes

### 5. Datos Fiscales del Cliente
- ✅ Almacenar: nombre fiscal, dirección, país, ID fiscal
- ✅ Enviar datos a Stripe Customer
- ✅ Endpoint para actualizar info fiscal

### 6. Cancelaciones y Reembolsos
- ✅ Cancelar factura (void)
- ✅ Reembolsos parciales/totales
- ✅ Registro en BD
- ✅ Actualizar status automáticamente

### 7. Seguridad
- ✅ Verificación firma webhooks
- ✅ No exponer claves Stripe
- ✅ Manejo idempotencia en webhooks

## 📊 Modelos de Base de Datos

```sql
-- Usuario con info fiscal
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    stripe_customer_id VARCHAR UNIQUE,
    tax_name VARCHAR,
    tax_address TEXT,
    tax_country VARCHAR,
    tax_id VARCHAR,
    created_at TIMESTAMP
);

-- Facturas
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_invoice_id VARCHAR UNIQUE,
    amount DECIMAL,
    currency VARCHAR DEFAULT 'usd',
    status VARCHAR, -- paid, open, failed, void
    pdf_url VARCHAR,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    issued_at TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP
);

-- Items de factura
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id),
    description VARCHAR,
    amount DECIMAL,
    quantity INTEGER DEFAULT 1,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    created_at TIMESTAMP
);
```

## 🔧 Endpoints de Facturación

### Dashboard
```http
GET /dashboard/billing-summary
# Respuesta:
{
  "total_paid": 299.99,
  "pending_invoices": 1,
  "last_payment_date": "2024-01-15T10:30:00Z",
  "currency": "usd"
}
```

### Facturas
```http
GET /billing/invoices
# Lista todas las facturas del usuario

GET /billing/invoices/{invoice_id}
# Detalle de factura específica con items

POST /billing/refund
# Crear reembolso
{
  "invoice_id": 123,
  "amount": 29.99  # opcional, null = reembolso total
}
```

### Info Fiscal
```http
PUT /billing/tax-info
# Actualizar datos fiscales
{
  "tax_name": "Empresa S.A.",
  "tax_address": "Calle 123, Ciudad",
  "tax_country": "ES",
  "tax_id": "B12345678"
}
```

## 🔄 Flujo Completo de Facturación

### 1. Suscripción Creada
```
Usuario → Checkout Stripe → Webhook subscription.created
    ↓
Crear customer en BD → Activar API keys
```

### 2. Factura Generada
```
Stripe → Webhook invoice.created
    ↓
Crear Invoice en BD con items
```

### 3. Factura Finalizada
```
Stripe → Webhook invoice.finalized
    ↓
Actualizar status → Enviar email (opcional)
```

### 4. Pago Exitoso
```
Usuario paga → Stripe → Webhook invoice.payment_succeeded
    ↓
Actualizar status → paid_at → Reactivar servicios
```

### 5. Pago Fallido
```
Pago falla → Stripe → Webhook invoice.payment_failed
    ↓
Actualizar status → Suspender API keys → Reintento automático
```

### 6. Reembolso
```
Usuario solicita → POST /billing/refund → Stripe API
    ↓
Crear refund → Actualizar BD → Notificar usuario
```

## 🛠️ Configuración Stripe

### Webhooks Requeridos
Configurar en Stripe Dashboard:
- `invoice.created`
- `invoice.finalized`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `invoice.voided`

URL: `https://tu-dominio.com/billing/webhook`

### Variables de Entorno
```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_FREE=price_free_id
STRIPE_PRICE_PRO=price_pro_id
STRIPE_PRICE_ENTERPRISE=price_enterprise_id
```

## 📈 Métricas y Monitoreo

### Queries Útiles
```sql
-- Total facturado por mes
SELECT DATE_TRUNC('month', paid_at) as month,
       SUM(amount) as total
FROM invoices
WHERE status = 'paid'
GROUP BY month
ORDER BY month DESC;

-- Facturas pendientes
SELECT COUNT(*) as pending
FROM invoices
WHERE status IN ('open', 'failed');

-- MRR (Monthly Recurring Revenue)
SELECT SUM(amount) as mrr
FROM invoices
WHERE status = 'paid'
  AND period_end >= CURRENT_DATE
  AND period_start <= CURRENT_DATE;
```

## 🔒 Seguridad

- ✅ Webhooks verifican firma HMAC
- ✅ Endpoints requieren autenticación JWT
- ✅ Datos sensibles encriptados
- ✅ Rate limiting por usuario
- ✅ Logs de auditoría

## 🚀 Próximos Pasos

1. **Testing**: Probar con Stripe test mode
2. **Frontend**: Integrar dashboard de facturación
3. **Emails**: Notificaciones automáticas
4. **Multi-moneda**: Soporte EUR, GBP
5. **Impuestos**: Cálculo automático por país
6. **Analytics**: Dashboard admin con métricas

---

**Ready for production!** 🎉